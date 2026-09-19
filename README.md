# Free ChatGPT

Interface de chat simples para conversar com o **GPT-4o**, composta por uma API em FastAPI e um frontend estático de arquivo único.

## Motivo do projeto

Ter um chat próprio com o GPT-4o, com a chave da OpenAI guardada no servidor (nunca exposta no navegador) e uma interface enxuta, sem framework de frontend nem etapa de build. O projeto também serve como base de estudo para integrar um LLM a uma API e a uma interface web.

## Funcionalidades

- Envio de mensagens ao GPT-4o e exibição da resposta no chat.
- Várias conversas na barra lateral, criadas e apagadas pelo usuário. Ficam salvas no `localStorage` do navegador.
- Sugestões de perguntas na tela inicial.
- Indicador de status da API (online/offline) e tratamento de erros e de timeout (60 s).
- Layout responsivo, com menu lateral em telas pequenas.
- Visual escuro baseado no design system *Lumina*: fundo animado (UnicornStudio), feixes de luz e bordas em degradê.

## Especificações

### API

| Método | Rota            | Descrição                                   |
| ------ | --------------- | ------------------------------------------- |
| `POST` | `/send_message` | Envia uma mensagem ao GPT-4o e devolve o texto da resposta. |

**Requisição**

```json
{ "message": "Explique o que é uma API REST" }
```

`message` é obrigatória e não pode ser vazia.

**Resposta (200)**

```json
{ "response": "Uma API REST é ..." }
```

A documentação interativa (Swagger) fica em `/docs` com o servidor rodando.

### Limitações atuais

- A API recebe **apenas a última mensagem**. O histórico da conversa não é enviado ao modelo, então o GPT-4o não lembra do que foi dito antes.
- As conversas ficam só no navegador: não há banco de dados nem contas de usuário.
- O CORS está aberto para qualquer origem (`allow_origins=["*"]`). Restrinja antes de publicar o backend.

## Stack

**Backend**
- Python 3.13+
- [FastAPI](https://fastapi.tiangolo.com/) (com o CLI `fastapi dev`)
- [OpenAI Python SDK](https://github.com/openai/openai-python) (Responses API, modelo `gpt-4o`)
- Pydantic para validação, `python-dotenv` para variáveis de ambiente
- [uv](https://docs.astral.sh/uv/) para dependências e ambiente virtual

**Frontend**
- HTML, CSS e JavaScript puros em um único arquivo (`frontend/index.html`)
- [Lucide](https://lucide.dev/) para ícones
- [UnicornStudio](https://www.unicorn.studio/) para o fundo animado (WebGL, carregado por CDN)
- Google Fonts (Inter e Instrument Serif)

## Estrutura

```
.
├── backend/
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── .env                  # OPENAI_API_KEY (não versionado)
│   └── src/my_chatgpt/
│       ├── main.py           # app FastAPI e rota /send_message
│       └── schemas.py        # modelos de requisição e resposta
└── frontend/
    ├── index.html            # interface do chat
    └── lumina-video/         # assets do design system (CSS, JS, imagens)
```

## Como executar

### Pré-requisitos

- [uv](https://docs.astral.sh/uv/getting-started/installation/) instalado (ele baixa o Python 3.13 se necessário)
- Uma chave de API da OpenAI

### 1. Configurar a chave da OpenAI

Crie o arquivo `backend/.env`:

```env
OPENAI_API_KEY=sk-...
```

### 2. Subir o backend

Execute **de dentro de `backend/`**, onde está o `pyproject.toml`:

```bash
cd backend
uv run fastapi dev src/my_chatgpt/main.py --port 8001
```

O `uv` cria o `backend/.venv` e instala as dependências na primeira execução. A API fica em `http://localhost:8001` e a documentação em `http://localhost:8001/docs`.

> O frontend procura a API em `http://localhost:8001` por padrão. Para usar outra porta, abra a página com `?api=http://localhost:PORTA`.

### 3. Servir o frontend

Em outro terminal:

```bash
cd frontend
python3 -m http.server 5500
```

Abra **http://localhost:5500**. Sirva a pasta por HTTP em vez de abrir o arquivo direto (`file://`), para evitar problemas nas chamadas à API.

O fundo animado precisa de internet, porque o runtime do UnicornStudio e as fontes vêm de CDNs.

## Solução de problemas

- **`Failed to spawn: fastapi`**: você rodou o `uv run` fora de `backend/`. Entre nessa pasta e rode de novo.
- **Status "API offline" na página**: confira se o backend está rodando e se a porta é a mesma do frontend (`?api=...`).
- **Erro 500 ao enviar mensagem**: verifique se `backend/.env` existe e se a `OPENAI_API_KEY` é válida.
