from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from openai import OpenAIError
import time
import streamlit as st
from neo4j import GraphDatabase

def get_openai_llm(api_key, model, temperature, max_tokens):
    return ChatOpenAI(openai_api_key=api_key, model=model, temperature=temperature, max_tokens=max_tokens)

def process_query(session_id: str, query: str, model: str, cypher_prompt, kg_prompt, compile_prompt, schema, temperature, max_tokens, generate_kg: bool):
    # Initialize LLMs
    llm = get_openai_llm(st.secrets["OPENAI_API_KEY"], model, temperature, max_tokens)
    cypher_chain = LLMChain(llm=llm, prompt=cypher_prompt)
    kg_chain = LLMChain(llm=llm, prompt=kg_prompt)
    compile_chain = LLMChain(llm=llm, prompt=compile_prompt)

    # Generate Cypher query and execute it
    cypher_query = cypher_chain.run({"schema": schema, "question": query})
    cypher_query = cypher_query.strip().replace("```cypher", "").replace("```", "").strip()

    with driver.session() as session:
        results = session.run(cypher_query)
        results = list(results)  # Convert to list to preserve Neo4j types

    final_answer_placeholder = st.empty()
    
    def generate_final_answer():
        partial_answer = ""
        try:
            final_response = compile_chain.run({"query": query, "results": str(results)})
        except OpenAIError as e:
            final_response = "Result exceeds token limit. Please try again with a more specific query."

        for char in final_response:
            partial_answer += char
            final_answer_placeholder.markdown(partial_answer)
            time.sleep(0.01)
        
        return final_response
    
    final_response = generate_final_answer()

    # Store the Cypher query in the session state
    st.session_state.queries.append(cypher_query)

    if generate_kg:
        kg_query = kg_chain.run({"schema": schema, "question": query})
        kg_query = kg_query.strip().replace("```cypher", "").replace("```", "").strip()
        st.subheader("Knowledge Graph Cypher Query")
        st.code(kg_query)
        st.markdown("To visualize the KG, input the cypher query [here](http://35.203.6.204:7474/browser/)", unsafe_allow_html=True)
        st.session_state.queries.append(kg_query)
        
    return final_response
