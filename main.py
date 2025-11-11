import os
import json
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

app = FastAPI()
load_dotenv()

API_KEY = os.getenv("Gemini_api_key")
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-2.5-flash')

try:
    with open("knowledge_base.json", "r") as f:
        knowledge_base = json.load(f)
except FileNotFoundError:
    print("Error")


AVAILABLE_INTENTS = list(knowledge_base.keys())

class UserQuery(BaseModel):
    query: str

@app.post("/process-query")
async def process_user_query(user_query: UserQuery):
    
    query = user_query.query 
    intent_list_str = "\n".join([f"- {intent}" for intent in AVAILABLE_INTENTS])
    
    prompt = f"""
    You are an intent classification bot.
    Analyze the user query and map it to one of the following intents:
    {intent_list_str}

    User Query: "{query}"

    Respond with ONLY the single best-matching intent key from the list.
    If no intent matches, respond with: unknown_intent
    Your Response:
    """
    
    try:
        response = model.generate_content(prompt)
        intent_key = response.text.strip()

        if intent_key in knowledge_base:
            result_data = knowledge_base[intent_key]
            result_data['intent_key'] = intent_key 
            return result_data
        else:
            return knowledge_base["unknown_intent"]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "DTU Admin Bot API is running."}