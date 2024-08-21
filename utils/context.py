import redis
import streamlit as st

redis_client = redis.StrictRedis(
    host=st.secrets["redis_host"],
    port=12019,
    password=st.secrets["redis_password"],
    db=0,
    decode_responses=True
)

def store_context(session_id: str, question: str, answer: str):
    context_key = f"context:{session_id}"
    context_data = redis_client.get(context_key)
    if context_data:
        context = context_data
        context += f"\nUser: {question}\nBot: {answer}"
    else:
        context = f"User: {question}\nBot: {answer}"
    redis_client.set(context_key, context, ex=1800)  # Set TTL to 24 hours

def get_context(session_id: str) -> str:
    context_key = f"context:{session_id}"
    context_data = redis_client.get(context_key)
    if context_data:
        return context_data
    return ""
