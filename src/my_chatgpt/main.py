from dotenv import load_dotenv
from fastapi import FastAPI
from openai import AsyncOpenAI

from my_chatgpt.schemas import SendMessageRequest, SendMessageResponse

load_dotenv()

app = FastAPI(title="my-chatgpt")
client = AsyncOpenAI()


@app.post("/send_message", response_model=SendMessageResponse)
async def send_message(payload: SendMessageRequest) -> SendMessageResponse:
    result = await client.responses.create(
        model="gpt-4o",
        input=payload.message,
    )
    return SendMessageResponse(response=result.output_text)
