from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
from backend.src.agent.agent import rule_based_agent, llm_agent
from backend.src.utils.helper import logger
from backend.src.observability.metrics_service import get_metrics_summary
from backend.src.observability.metrics_db import init_metrics_db, log_request_metrics
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
import time


limiter = Limiter(key_func=get_remote_address)
app = FastAPI()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.on_event("startup")
def startup():
    init_metrics_db()

@app.get("/")
def get_welcome_page():
    return "Welcome to Ashu's LLM + RAG PROJECT!!"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/metrics")
def get_metrics():
    return get_metrics_summary()

@app.get("/ask_rule_based_agent")
@limiter.limit("10/minute")
def ask_rule_based_agent(request: Request, query: str, session_id: str = "default"):
    start_time = time.time()
    status = "success"
    route = None
    tool = None
    latency_ms = 0
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
        route = metadata.get('route')
        tool = metadata.get('tool')
        return {
            "answer": answer,
            "metadata": {
                "latency_ms": latency_ms,
                **metadata
            }
        }
    except Exception as e:
        status = "error"
        latency_ms = round((time.time() - start_time) * 1000, 2)
        logger.exception(f"Query failed | session_id={session_id} | latency_ms={latency_ms}")
        return {
            "error": str(e),
            "metadata": {
                "latency_ms": latency_ms
            }
        }
    finally:
        client_ip = request.client.host if request.client else "unknown"
        log_request_metrics(
            endpoint="/ask_rule_based_agent",
            client_ip=client_ip,
            latency_ms=latency_ms,
            status=status,
            route=route,
            tool=tool
        )

@app.get("/ask_llm_agent")
@limiter.limit("10/minute")
def ask_llm_agent(request: Request, query: str, session_id: str = "default"):
    start_time = time.time()
    status = "success"
    route = None
    tool = None
    latency_ms = 0
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
        route = metadata.get('route')
        tool = metadata.get('tool')
        return {
            "answer": answer,
            "metadata": {
                "latency_ms": latency_ms,
                **metadata
            }
        }
    except Exception as e:
        status = "error"
        latency_ms = round((time.time() - start_time) * 1000, 2)
        logger.exception(f"Query failed | session_id={session_id} | latency_ms={latency_ms}")
        return {
            "error": str(e),
            "metadata": {
                "latency_ms": latency_ms
            }
        }
    finally:
        client_ip = request.client.host if request.client else "unknown"
        log_request_metrics(
            endpoint="/ask_llm_agent",
            client_ip=client_ip,
            latency_ms=latency_ms,
            status=status,
            route=route,
            tool=tool
        )
