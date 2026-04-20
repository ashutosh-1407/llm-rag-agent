from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from backend.src.agent.agent import rule_based_agent, llm_agent
from backend.src.utils.helper import logger
from backend.src.observability.metrics import get_metrics as fetch_metrics
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
import time


limiter = Limiter(key_func=get_remote_address)
app = FastAPI()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/")
def get_welcome_page():
    return "Welcome to Ashu's LLM + RAG PROJECT!!"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/metrics")
def get_metrics():
    return fetch_metrics()

@app.get("/ask_rule_based_agent")
@limiter.limit("10/minute")
def ask_rule_based_agent(request: Request, query: str, session_id: str = "default"):
    start_time = time.time()
    try:
        logger.info(f"Incoming query | session_id={session_id} | query={query}")
        answer, metadata = rule_based_agent(query, session_id, 5)
        latency_ms = round((time.time() - start_time) * 1000, 2)
        logger.info(
            f"Query served | session_id={session_id} | "
            f"latency_ms={latency_ms} | "
            f"route={metadata.get('route')} | "
            f"tool={metadata.get('tool')} | "
            f"retrieved_k={metadata.get('retrieved_k')}"
        )
        return {
            "answer": answer,
            "metadata": {
                "latency_ms": latency_ms,
                **metadata
            }
        }
    except Exception as e:
        latency_ms = round((time.time() - start_time) * 1000, 2)
        logger.exception(f"Query failed | session_id={session_id} | latency_ms={latency_ms}")
        return {
            "error": str(e),
            "metadata": {
                "latency_ms": latency_ms
            }
        }

@app.get("/ask_llm_agent")
@limiter.limit("10/minute")
def ask_llm_agent(request: Request, query: str, session_id: str = "default"):
    start_time = time.time()
    try:
        logger.info(f"Incoming query | session_id={session_id} | query={query}")
        answer, metadata = llm_agent(query, session_id, 5)
        latency_ms = round((time.time() - start_time) * 1000, 2)
        logger.info(
            f"Query served | session_id={session_id} | "
            f"latency_ms={latency_ms} | "
            f"route={metadata.get('route')} | "
            f"tool={metadata.get('tool')} | "
            f"retrieved_k={metadata.get('retrieved_k')}"
        )
        return {
            "answer": answer,
            "metadata": {
                "latency_ms": latency_ms,
                **metadata
            }
        }
    except Exception as e:
        latency_ms = round((time.time() - start_time) * 1000, 2)
        logger.exception(f"Query failed | session_id={session_id} | latency_ms={latency_ms}")
        return {
            "error": str(e),
            "metadata": {
                "latency_ms": latency_ms
            }
        }
