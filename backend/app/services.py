import os
import json
import re
import logging
from dotenv import load_dotenv
from openai import OpenAI

from app.models import (
    UserInput,
    IntentAnalysis,
    EmotionRiskAnalysis,
    StrategyDecision,
    BotResponse
)
from app.prompts import prompt_manager
from app.local_llm import generate_local_response

load_dotenv()

# ===============================
# Logging
# ===============================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "local").lower() # "local", "openai", "aliyun", "hf"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
HF_TOKEN = os.getenv("HF_TOKEN", "")
HF_MODEL_ID = os.getenv("HF_MODEL_ID", "Qwen/Qwen2.5-72B-Instruct")
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
ALI_MODEL_ID = os.getenv("ALI_MODEL_ID", "qwen-turbo") # qwen-turbo, qwen-plus, qwen-max

# Init API Client
api_client = None
current_model_id = "gpt-3.5-turbo" # Default fallback

if LLM_PROVIDER == "aliyun":
    if not DASHSCOPE_API_KEY:
        logger.warning("LLM_PROVIDER is 'aliyun' but DASHSCOPE_API_KEY is missing.")
    api_client = OpenAI(
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=DASHSCOPE_API_KEY
    )
    current_model_id = ALI_MODEL_ID
elif LLM_PROVIDER == "openai":
    api_client = OpenAI(api_key=OPENAI_API_KEY)
    current_model_id = "gpt-3.5-turbo"

def clean_json_response(content: str) -> dict:
    """Robust JSON cleaner for LLM output"""
    if not content:
        return {}

    try:
        # ```json ... ```
        match = re.search(r"```json\s*([\s\S]*?)\s*```", content)
        if match:
            content = match.group(1)

        return json.loads(content)
    except Exception:
        try:
            # fallback: extract first {...}
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1:
                return json.loads(content[start:end + 1])
        except Exception:
            pass

    return {}


# ===============================
# LLM Dispatcher
# ===============================
def generate_llm_response(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.7
) -> str:
    """
    Local-first, OpenAI as fallback
    """
    # -------- Local LLM --------
    if LLM_PROVIDER == "local":
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        return generate_local_response(full_prompt)

    # -------- OpenAI API --------
    if not api_client:
        logger.error("API client not initialized")
        return ""

    try:
        completion = api_client.chat.completions.create(
            model=current_model_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            timeout=15.0
        )
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"API Generation Error: {e}")
        return ""


# ---- Mock Modules for Fallback ----
def mock_intent(message: str) -> IntentAnalysis:
    if "退货" in message or "退款" in message:
        return IntentAnalysis(intent="售后/退换货", confidence=0.9, reasoning="检测到退换货关键词")
    if "发货" in message or "快递" in message:
        return IntentAnalysis(intent="订单/物流查询", confidence=0.9, reasoning="检测到物流关键词")
    if "投诉" in message:
        return IntentAnalysis(intent="投诉/不满", confidence=0.9, reasoning="检测到投诉关键词")
    return IntentAnalysis(intent="商品咨询", confidence=0.6, reasoning="默认意图")

def mock_emotion(message: str) -> EmotionRiskAnalysis:
    lvl = 0
    risk_tags = []
    if "!" in message or "愤怒" in message or "垃圾" in message:
        lvl = 2
    if "投诉" in message or "举报" in message:
        risk_tags.append("平台投诉")
    return EmotionRiskAnalysis(emotion_level=lvl, risk_tags=risk_tags, risk_score=lvl * 25)

def mock_strategy(intent: IntentAnalysis, emotion: EmotionRiskAnalysis) -> StrategyDecision:
    if intent.intent == "售后/退换货":
        return StrategyDecision(strategy="标准售后", prompt_template_name="after_sales", reasoning="售后流程")
    return StrategyDecision(strategy="热情导购", prompt_template_name="guide", reasoning="默认导购")

def mock_response(strategy: StrategyDecision) -> str:
    if strategy.strategy == "标准售后":
        return "亲，非常抱歉让您不满意了。我们支持7天无理由退换货，您可以直接在订单页面申请哦，运费我们有赠送运费险的。"
    return "亲，您好！我是您的专属客服，请问有什么可以帮您？如果是关于商品的问题，可以直接问我哦~"


# ===============================
# Core Pipeline
# ===============================
async def process_chat(user_input: UserInput) -> BotResponse:
    message = user_input.message

    # -------- 1. Intent --------
    try:
        intent_text = generate_llm_response(
            system_prompt=prompt_manager.intent_detection,
            user_prompt=f"用户输入: {message}\n请仅输出 JSON。",
            temperature=0.1
        )
        intent_data = clean_json_response(intent_text)
        if not intent_data:
            raise ValueError("Invalid intent JSON")
        intent = IntentAnalysis(**intent_data)
    except Exception as e:
        logger.error(f"Intent Error: {e}")
        intent = mock_intent(message)

    # -------- 2. Emotion --------
    try:
        emotion_text = generate_llm_response(
            system_prompt=prompt_manager.emotion_risk,
            user_prompt=f"用户输入: {message}\n请仅输出 JSON。",
            temperature=0.1
        )
        emotion_data = clean_json_response(emotion_text)
        if not emotion_data:
            raise ValueError("Invalid emotion JSON")
        emotion = EmotionRiskAnalysis(**emotion_data)
    except Exception as e:
        logger.error(f"Emotion Error: {e}")
        emotion = mock_emotion(message)

    # -------- 3. Strategy --------
    try:
        ctx = (
            f"Intent: {intent.intent}, "
            f"Emotion Level: {emotion.emotion_level}, "
            f"Risk Tags: {emotion.risk_tags}"
        )
        strat_text = generate_llm_response(
            system_prompt=prompt_manager.strategy_routing,
            user_prompt=f"{ctx}\n请仅输出 JSON。",
            temperature=0.1
        )
        strat_data = clean_json_response(strat_text)
        if not strat_data:
            raise ValueError("Invalid strategy JSON")
        strategy = StrategyDecision(**strat_data)
    except Exception as e:
        logger.error(f"Strategy Error: {e}")
        strategy = mock_strategy(intent, emotion)

    # -------- 4. Response --------
    try:
        gen_prompt = (
            prompt_manager.response_generation
            .replace("{{strategy}}", strategy.strategy)
            .replace("{{intent}}", intent.intent)
            .replace("{{emotion_level}}", str(emotion.emotion_level))
            .replace("{{history}}", str(user_input.history))
            .replace("{{message}}", message)
        )

        reply = generate_llm_response(
            system_prompt=prompt_manager.system_role,
            user_prompt=gen_prompt,
            temperature=0.7
        )

        if not reply:
            reply = mock_response(strategy)

    except Exception as e:
        logger.error(f"Response Error: {e}")
        reply = mock_response(strategy)

    return BotResponse(
        content=reply,
        intent_analysis=intent,
        emotion_analysis=emotion,
        strategy_decision=strategy,
        suggested_actions=[]
    )
