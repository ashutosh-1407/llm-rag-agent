from backend.src.rag.retriever_store import get_retriever
from backend.src.llm.generator import generate_completion
from backend.src.tools.tools import TOOL_MAP
from backend.src.tools.registry import tools
from backend.src.utils.helper import logger, rerank
from backend.src.memory.memory_store import get_history, append_turn


def agent_decide(query):
    query = query.lower()
    if "summarize" in query:
        return {"type": "tool", "name": "summarize_doc"}
    elif "support" in query:
        return {"type": "tool", "name": "get_support_info"}
    elif "return" in query or "policy" in query:
        return {"type": "retrieval"}
    else:
        return {"type": "llm"}

def rule_based_agent(query, session_id="default", k=5):
    logger.info(f"Fetching history | session_id={session_id}")
    history = get_history(session_id)
    history_text = "\n".join(
        f"User: {item['query']}\nAssistant: {item['answer']}"
        for item in history[-3:]
    )
    if history != []:
        logger.info(f"Found history | history text={history_text}")
    else:
        logger.info("No history found.")

    logger.info(f"Fetching context | query={query} | k={k}")
    retriever = get_retriever()
    contexts = retriever.retrieve(query, k)
    contexts = rerank(contexts)
    context_text = "\n\n".join(contexts)

    logger.info(f"Running rule based agent with tools | query={query} | session_id={session_id}")
    
    # prompt with history and using tools with rule-based agent
    system_prompt = f"""
    You are a helpful assistant.

    Use the provided context ONLY to answer the user's question.

    Conversation history:
    {history_text if history_text else "No prior conversation."}

    Context:
    {context_text if context_text else "No retrieved context."}

    Question:
    {query}
    """.strip()
    
    decision = agent_decide(query)
    route = "direct_llm"
    tools_used = None
    if decision["type"] == "tool":
        route = "tool"
        tools_used = decision["name"]
        answer = TOOL_MAP[tools_used]()
    elif decision["type"] == "retrieval":
        route = "retrieval"
    else:
        context_text = ""
    
    messages = [{"role": "user", "content": system_prompt}]
    response = generate_completion(messages)
    answer = response.choices[0].message.content

    metadata = {
        "route": route,
        "tool": tools_used,
        "retrieved_k": len(contexts),
        "retrieved_chunks": contexts
    }

    return answer, metadata

# llm decides if tools needs to be run
def llm_agent(query, session_id="default", k=5):
    logger.info(f"Fetching history | session_id={session_id}")
    history = get_history(session_id)
    history_text = "\n".join(
        f"User: {item['query']}\nAssistant: {item['answer']}"
        for item in history[-3:]
    )
    if history != []:
        logger.info(f"Found history | history text={history_text}")
    else:
        logger.info("No history found.")

    logger.info(f"Fetching context | query={query} | k={k}")
    retriever = get_retriever()
    contexts = retriever.retrieve(query, k)
    contexts = rerank(contexts)
    context_text = "\n\n".join(contexts)
    
    logger.info(f"Running llm based agent with tools | query={query} | session_id={session_id}")

    system_prompt = f"""
    You are a helpful assistant.

    Use the provided context to answer the user's question.
    Use tools if they are helpful.
    If the answer is not in the context and no tool applies, say you don't know.

    Conversation history:
    {history_text if history_text else "No prior conversation."}

    Context:
    {context_text if context_text else "No retrieved context."}
    """.strip()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ]

    # Step 1 - Ask LLM - it may call a tool
    response = generate_completion(messages, tools)

    message = response.choices[0].message

    route = "direct_llm"
    tools_used = None

    # Step 2 - Did LLM call a tool?
    if message.tool_calls:
        route = "tool"
        
        # Step 3 - Send tool result back to LLM
        messages.append(message)
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tools_used = tool_name
            if tool_name not in TOOL_MAP:
                tool_result = f"Tool '{tool_name}' is not implemented."
            else:
                tool_result = TOOL_MAP[tool_name]()
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(tool_result)
            })

        # Step 4 - Final response
        final_response = generate_completion(messages)

        answer = final_response.choices[0].message.content
    else:
        # no tool needed
        # if context exists, this is effectively retrieval-based answering
        if contexts:
            route = "retrieval"
            answer = message.content
    
    # fallback safety
    if not answer:
        answer = "Sorry, I couldn't generate an answer"
    
    append_turn(session_id, query, answer)

    metadata = {
        "route": route,
        "tool": tools_used,
        "retrieved_k": len(contexts),
        "retrieved_chunks": contexts
    }
    
    # Step 5 - No tool needed
    return answer, metadata

def run_agent_with_debug(query: str, session_id: str = "default"):
    answer, metadata = llm_agent(query, session_id, 5)
    return {
        "answer": answer,
        "retrieved_chunks": metadata["retrieved_chunks"],
        "metadata": metadata
    }
