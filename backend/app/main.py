from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models import UserInput, BotResponse
from app.services import process_chat
from app.prompts import prompt_manager

app = FastAPI(title="CalmGuard API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/chat", response_model=BotResponse)
async def chat_endpoint(user_input: UserInput):
    try:
        response = await process_chat(user_input)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/prompts")
async def get_prompts():
    return {
        "system_role": prompt_manager.system_role,
        "intent_detection": prompt_manager.intent_detection,
        "emotion_risk": prompt_manager.emotion_risk,
        "strategy_routing": prompt_manager.strategy_routing,
        "response_generation": prompt_manager.response_generation
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
