import streamlit as st
import time
from neo4j import GraphDatabase
from utils.caching import create_cache_key, cache_results
from utils.context import store_context, get_context
from utils.rag_loop import get_openai_llm, process_query
from utils.prompts import cypher_generation_prompt, compile_prompt, kg_generation_prompt, schema


# Key variables
api_key = st.secrets["OPENAI_API_KEY"]
URL = st.secrets["url"]
AUTH = (st.secrets["username"], st.secrets["password"])
driver = GraphDatabase.driver(URL, auth=AUTH)
driver.verify_connectivity()

# Load secrets from the config file
st.set_page_config(
    page_title="Bioinformatics Chatbot",
    page_icon="n23_icon.png",
    initial_sidebar_state="expanded",
    layout="wide"
)

# Title and sidebar inputs
st.title("ALS Chatbot")

with st.sidebar:
    st.markdown("# Chat Options")
    use_model = st.selectbox("Select GPT Model", ["gpt-4o", "gpt-4o-mini"])
    max_tokens = st.number_input("Output Token Length", min_value=1, max_value=4096, value=4096)
    temperature = st.slider("Temperature", min_value=0.0, max_value=0.5, value=0.01)
    generate_kg = st.checkbox("Generate Knowledge Graph")

if use_model == "gpt-4o":
    model = "gpt-4o-2024-08-06"
else:
    model = "gpt-4o-mini"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "queries" not in st.session_state:
    st.session_state.queries = []

session_id = st.session_state.get('session_id', str(time.time()))
st.session_state['session_id'] = session_id

# Display chat messages and Cypher queries
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and i < len(st.session_state.queries):
            st.subheader("Generated Cypher Query")
            st.code(st.session_state.queries[i])

# Chat input
if prompt := st.chat_input("Ask a question about bioinformatics"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        context = get_context(session_id)
        full_response = process_query(session_id, prompt, model, cypher_generation_prompt, kg_generation_prompt, compile_prompt, driver, schema, temperature, max_tokens, generate_kg)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        store_context(session_id, prompt, full_response)
