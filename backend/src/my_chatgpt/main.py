import logging
from pathlib import Path

import openai
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI

from my_chatgpt.schemas import SendMessageRequest, SendMessageResponse

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

logger = logging.getLogger("my_chatgpt")

app = FastAPI(title="my-chatgpt")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_client: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI:
    """Cria o cliente sob demanda, para uma chave ausente virar erro amigável em vez de derrubar o servidor."""
    global _client
    if _client is None:
        _client = AsyncOpenAI()
    return _client


def to_http_error(exc: Exception) -> HTTPException:
    """Traduz erros da OpenAI em mensagens claras para o usuário, sem expor detalhes internos."""
    if isinstance(exc, openai.RateLimitError):
        if exc.code == "insufficient_quota":
            return HTTPException(
                status_code=402,
                detail="Sem créditos na conta da OpenAI. Adicione saldo ou verifique o plano de cobrança.",
            )
        return HTTPException(
            status_code=429,
            detail="Muitas requisições em pouco tempo. Aguarde alguns instantes e tente novamente.",
        )
    if isinstance(exc, openai.AuthenticationError):
        return HTTPException(
            status_code=500,
            detail="Chave da OpenAI inválida ou ausente. Verifique a OPENAI_API_KEY no backend/.env.",
        )
    if isinstance(exc, openai.PermissionDeniedError | openai.NotFoundError):
        return HTTPException(
            status_code=502,
            detail="A conta da OpenAI não tem acesso ao modelo gpt-4o.",
        )
    if isinstance(exc, openai.BadRequestError):
        return HTTPException(status_code=400, detail="A OpenAI não aceitou a mensagem enviada.")
    if isinstance(exc, openai.APITimeoutError):
        return HTTPException(status_code=504, detail="A OpenAI demorou demais para responder. Tente novamente.")
    if isinstance(exc, openai.APIConnectionError):
        return HTTPException(status_code=503, detail="Não foi possível conectar à OpenAI. Verifique a conexão do servidor.")
    if isinstance(exc, openai.APIStatusError):
        return HTTPException(status_code=502, detail="A OpenAI está com problemas no momento. Tente novamente em instantes.")
    if isinstance(exc, openai.OpenAIError):
        # p.ex. OPENAI_API_KEY ausente ao criar o cliente
        return HTTPException(
            status_code=500,
            detail="OpenAI não configurada. Defina a OPENAI_API_KEY no backend/.env.",
        )
    return HTTPException(status_code=500, detail="Erro inesperado ao processar a mensagem.")


@app.post("/send_message", response_model=SendMessageResponse)
async def send_message(payload: SendMessageRequest) -> SendMessageResponse:
    try:
        result = await get_client().responses.create(
            model="gpt-4o",
            input=payload.message,
        )
    except Exception as exc:
        logger.exception("Falha ao chamar a OpenAI")
        raise to_http_error(exc) from exc
    return SendMessageResponse(response=result.output_text)
