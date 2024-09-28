# ALS Chatbot

### 1. **Introduction**

GraphRAG involves the use of Knowledge Graphs to supplement the knowledge base of a traditional Large Language Model. Unlike traditional RAG models that rely on unstructured text data for retrieval, it leverages the structured, relational nature of graph databases to provide contextually rich and highly relevant information during the generation process.

<img width="1165" alt="Screenshot 2024-08-21 at 1 31 27 PM" src="https://github.com/user-attachments/assets/6e84d6c9-114d-444f-a186-f7dd97092a90">


### 2. **Working Principle**

GraphRAG enhances language models by integrating structured knowledge from graph databases, focusing on key principles:

- Structured Information Retrieval: Uses graph databases to access precise, relationship-based data, improving accuracy over unstructured text sources.
- Contextual Awareness: Maintains conversation context to provide consistent and relevant responses.
- Dynamic Query Generation: Generates tailored Cypher queries to extract relevant data, handling both simple and complex queries.
- Leveraging Relationships: Utilizes the connections within a knowledge graph to offer deeper insights and more focused answers.



### 3. **Components**

The components of the Chatbot can be are as follows:


#### 3.1     **Graph Database : Neo4J**

The backbone of the Knowledge Base. A graph has 3 primary components

* Nodes: Subjects of the study. In the context of target discovery, they can map the genes, proteins, ontologies, diseases, phenotypes etc.**     
* Relationships : Form the edges of the graph, mapping out the type of connection between 2 nodes.
* Properties : Both Nodes and Relationships can have their own properties which are specific to that data-type. Used to include additional information such as IDs, scores etc.

The graph database is hosted on the Cloud using the Neo4j database system.


#### 3.2    **Language Model : GPT**

The core of RAG implementations. We leverage OpenAI’s GPT-4o and 4o-mini models to convert natural language user queries into graph readable **Cypher** queries. The queried data is then fed-back into the model to generate a user output, thereby supplementing the knowledge of the LLM with user specific datasets.


#### 3.3   **Context Manager : Redis**

A Redis database is used to store and manage conversation context, ensuring that the chatbot can maintain a coherent dialogue over multiple interactions. By storing key pieces of information from previous exchanges, the context manager allows the chatbot to refer back to earlier points in the conversation, providing more relevant and consistent answers.


#### 3.4   **Graphical User Interface : Streamlit**

The full web-app is hosted on Streamlit which provides the front-end framework for the chatbot. It allows users to input their questions, receive answers, and, if enabled, view the underlying Cypher queries generated by the chatbot.


#### 3.5   **Graph Visualization : Neo4j Browser**

For users who need to see the relationships and data retrieved from the knowledge graph. Has functionality to generate subgraphs based on Cypher Queries, change the orientations and colors of the nodes and relationships etc.



### 4. **Graph Structure**


<img width="1190" alt="Screenshot 2024-08-21 at 1 31 01 PM" src="https://github.com/user-attachments/assets/d2a00adc-7627-4195-a358-57df4c5189f8">



### 5. **Code Structure**

The repository is structured as follows:

- **app.py**: The main application file that initializes the Streamlit app, manages the chat interface, and processes user queries. It integrates various utility functions and prompts to handle caching, context management, LLM interactions, and Cypher query generation.

- **utils/caching.py**: Contains helper functions for caching query results using Redis. This helps to improve performance by storing and retrieving previously computed results.

- **utils/context.py**: Manages conversation context by storing and retrieving previous interactions from Redis, ensuring that the chatbot can maintain a coherent conversation over multiple queries.

- **utils/rag\_loop.py**: Handles interactions with OpenAI's GPT models and processes user queries through the RAG (Retrieval-Augmented Generation) loop. It generates and executes Cypher queries and formats the final response.

- **utils/prompts.py**: Houses prompt templates used for generating Cypher queries, compiling responses, and creating knowledge graphs. This ensures that the LLM is guided properly in generating accurate queries and responses.

- **config/secrets.toml**: Stores sensitive information like API keys and database credentials. This file is kept out of version control by listing it in .gitignore.



### 6. **Relevant Links**

Links:

Github Repo : <https://github.com/VishantanK/ALS_Chatbot>

Visualization Browser : <http://35.203.6.204:7474/browser/>

