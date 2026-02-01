import torch
import logging
from transformers import AutoTokenizer, AutoModelForCausalLM

# ===============================
# Performance tuning (CPU)
# ===============================
torch.set_num_threads(4)          # 4~8 根据你的 CPU 调
torch.set_num_interop_threads(1)

# ===============================
# Logging
# ===============================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===============================
# Config
# ===============================
MODEL_PATH = r"D:/AI_Programs/CalmGuard/hf_models/TinyLlama-1.1B-Chat-v1.0"

# ===============================
# Global cache
# ===============================
_tokenizer = None
_model = None


def get_llm():
    """
    Load local TinyLlama (offline only).
    Load once, reuse globally.
    """
    global _tokenizer, _model

    if _tokenizer is not None and _model is not None:
        return _tokenizer, _model

    logger.info("Loading local TinyLlama from disk...")
    logger.info(f"Model path: {MODEL_PATH}")

    try:
        use_cuda = torch.cuda.is_available()
        device = "cuda" if use_cuda else "cpu"
        torch_dtype = torch.float16 if use_cuda else torch.float32

        logger.info(f"Device: {device}")
        logger.info(f"Dtype: {torch_dtype}")

        # -------- tokenizer --------
        tokenizer = AutoTokenizer.from_pretrained(
            MODEL_PATH,
            local_files_only=True,
            use_fast=False   # TinyLlama 必须 False
        )

        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        # -------- model --------
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH,
            local_files_only=True,
            torch_dtype=torch_dtype,
            low_cpu_mem_usage=True
        )

        model.to(device)
        model.eval()
        model.config.use_cache = True   # ⭐ KV cache

        _tokenizer = tokenizer
        _model = model

        logger.info("TinyLlama loaded successfully ✅")
        return _tokenizer, _model

    except Exception as e:
        logger.exception("Failed to load local TinyLlama ❌")
        raise RuntimeError(f"Local LLM load failed: {e}")


def build_tinyllama_prompt(user_input: str) -> str:
    """
    TinyLlama official chat prompt
    """
    return (
        "<|user|>\n"
        f"{user_input}\n"
        "<|assistant|>\n"
    )


def generate_local_response(
    prompt: str,
    max_new_tokens: int = 128,    # ⬅ 默认缩短
    temperature: float = 0.6,     # 安抚场景更稳
    top_p: float = 0.9
) -> str:
    """
    Fast local generation using model.generate (no pipeline).
    """
    tokenizer, model = get_llm()

    inputs = tokenizer(
        prompt,
        return_tensors="pt"
    )

    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    with torch.inference_mode():   # ⭐ 核心优化
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=temperature,
            top_p=top_p,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.pad_token_id
        )

    # 只解码新生成部分
    generated_ids = outputs[0][inputs["input_ids"].shape[-1]:]

    return tokenizer.decode(
        generated_ids,
        skip_special_tokens=True
    ).strip()


# ===============================
# CLI Test
# ===============================
if __name__ == "__main__":
    print("✅ TinyLlama (optimized) ready. 输入 exit 退出。\n")

    while True:
        text = input("你：")
        if text.lower() in ["exit", "quit"]:
            break

        prompt = build_tinyllama_prompt(text)
        reply = generate_local_response(prompt)

        print("\n模型：", reply)
        print("-" * 50)
