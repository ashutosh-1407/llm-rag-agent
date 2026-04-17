# from dotenv import load_dotenv
from openai import OpenAI
from src.tools.registry import tools, TOOL_MAP
from src.utils.constants import OPENAI_MODEL_NAME
import os


# load_dotenv()
# client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_answer_with_memory(query, contexts, history):
    combined_context = "\n\n".join(contexts)

    # basic prompt
    # prompt = f"""
    # Answer the question based only on the context below.

    # Context:
    # {combined_context}

    # Question:
    # {query}
    # """

    # prompt wighout hallucination I believe
    # prompt = f"""
    #     You are a helpful assistant.

    #     Answer the question ONLY using the context below.
    #     If the answer is not in the context, say "I don't know".

    #     Be concise and clear.

    #     Context:
    #     {combined_context}

    #     Question:
    #     {query}
    #     """

    # prompt with history and using tools with rule-based agent
    prompt = f"""
    You are a helpful assistant.

    Conversation so far:
    {history}

    Context:
    {contexts}

    Question:
    {query}
    """

    response = client.chat.completions.create(
        model=OPENAI_MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        tools=tools
    )

    return response.choices[0].message.content

# llm decides if tools needs to be run
def run_agent(query, contexts):
    combined_context = "\n\n".join(contexts)
    
    system_prompt = f"""
    You are a helpful assistant.

    Use tools if needed.

    Context:
    {combined_context}
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ]

    # Step 1 - Ask LLM - it may call a tool
    response = client.chat.completions.create(
        model = OPENAI_MODEL_NAME,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    message = response.choices[0].message

    # Step 2 - Did LLM call a tool?
    if message.tool_calls:
        tool_call = message.tool_calls[0]
        tool_fn_name = tool_call.function.name
        tool_result = TOOL_MAP[tool_fn_name]()
        
        # Step 3 - Send tool result back to LLM
        messages.append(message)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": tool_result
        })

        # Step 4 - Final response
        final_response = client.chat.completions.create(
            model=OPENAI_MODEL_NAME,
            messages=messages
        )

        return final_response.choices[0].message.content
    
    # Step 5 - No tool needed
    return message.content