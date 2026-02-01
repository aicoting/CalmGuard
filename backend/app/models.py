from pydantic import BaseModel, Field
from typing import List, Optional

class UserInput(BaseModel):
    message: str
    history: Optional[List[dict]] = []

class IntentAnalysis(BaseModel):
    intent: str = Field(..., description="Primary intent of the user (e.g., 'complaint', 'risk', 'emotional_venting')")
    confidence: float
    reasoning: str

class EmotionRiskAnalysis(BaseModel):
    emotion_level: int = Field(..., description="0-3 scale: 0=calm, 1=annoyed, 2=angry, 3=hostile")
    risk_tags: List[str] = Field(..., description="List of risk factors e.g., 'legal_threat', 'media_exposure'")
    risk_score: int = Field(..., description="0-100 score indicating risk severity")

class StrategyDecision(BaseModel):
    strategy: str = Field(..., description="Selected strategy: 'comfort', 'explain', 'escalate', 'refuse_risk'")
    prompt_template_name: str
    reasoning: str

class BotResponse(BaseModel):
    content: str
    intent_analysis: IntentAnalysis
    emotion_analysis: EmotionRiskAnalysis
    strategy_decision: StrategyDecision
    suggested_actions: Optional[List[str]] = []
