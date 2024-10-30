import streamlit as st 
from pathlib import Path
from langchain_community.agent_toolkits import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
import sqlite3
from langchain_groq import ChatGroq

st.set_page_config(page_title="LangChain: Chat with SQL DB",page_icon="🦜")
st.title("🦜Langchain Chat with SQL DB")

# INJECTION_WARNING = '''
#                     SQL agent can vulenrable to prompt injection. Use DB role with 
# '''

LOCALDB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"

## RAdio_option

radio_opt = ["Use SQLite 3 Database - Student.db", "Connect to your SQL database"]
selected_opt = st.sidebar.radio(label="Choose the DB which you want to chat",options=radio_opt)

if radio_opt.index(selected_opt) == 1:
    db_uri = MYSQL
    mysql_host = st.sidebar.text_input("Provide MYSQL Host")
    mysql_user = st.sidebar.text_input("MySQL User")
    mysql_pass = st.sidebar.text_input("MYSQL Password",type="password")
    mysql_db = st.sidebar.text_input("MySQL Database")
else : 
    db_uri = LOCALDB


api_key = st.sidebar.text_input(label="GROQ Api Key", type="password")

if not db_uri:
    st.info("Please enter the database information and Uri")

if not api_key:
    st.info("Please enter the Groq Api key")

##LLM 
llm = ChatGroq(groq_api_key=api_key,model_name = "Llama3-8b-8192",streaming=True)

@st.cache_resource(ttl="2h")
def configure_db(db_uri,mysql_host=None,mysql_user=None,mysql_pass=None,mysql_db=None):
    if db_uri ==LOCALDB:
        db_filePath = (Path(__file__).parent/"student.db").absolute()
        print(db_filePath)
        creator = lambda : sqlite3.connect(f"file:{db_filePath}?mode=ro",uri=True)
        return SQLDatabase(create_engine("sqlite:///",creator=creator))
    
    elif db_uri==MYSQL:
        if not (mysql_host and mysql_user and mysql_pass and  mysql_db):
            st.error("Please Provide all my MySQL connection details")
            st.stop()
        return SQLDatabase(create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_pass}@{mysql_host}/{mysql_db}"))

if db_uri==MYSQL:
    db=configure_db(db_uri,mysql_host,mysql_user,mysql_pass,mysql_db)
else:
    db=configure_db(db_uri)

## toolkit
toolkit=SQLDatabaseToolkit(db=db,llm=llm)

agent=create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)

if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query=st.chat_input(placeholder="Ask anything from the database")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        streamlit_callback=StreamlitCallbackHandler(st.container())
        response=agent.run(user_query,callbacks=[streamlit_callback])
        st.session_state.messages.append({"role":"assistant","content":response})
        st.write(response)   
    

