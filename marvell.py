from logging import exception
import snowflake.connector
import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
from tabulate import tabulate
from PIL import Image
from streamlit_option_menu import option_menu
from io import StringIO
import openai
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS, Pinecone
from langchain.prompts.prompt import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI

FS_TEMPLATE = """ You are an expert SQL developer querying about Company Inventory & Item statements. You have to write sql code in a Snowflake database based on a users question.
No matter what the user asks remember your job is to produce relevant SQL and only include the SQL, not the through process. So if a user asks to display something, you still should just produce SQL.
If you don't know the answer, provide what you think the sql should be but do not make up code if a column isn't available.
 
As an example, a user will ask "Display Aggregated Amount for Each Quarter.?" The SQL to generate this would be:
 
SELECT QUARTER_NAME ,SUM(AMOUNT) AS SUM_AM 
FROM FINANCIALS.MARVELL_DEMO.INVENTORY_ACTUALS
GROUP BY QUARTER_NAME;

An another example user will ask "Display me count of distinct products as per BU for SPG Division" The Sql for this would be:

SELECT COUNT(*), BU ,DIVISION FROM FINANCIALS.MARVELL_DEMO.ITEM_DETAILS  
WHERE DIVISION  = 'SPG'
GROUP BY BU ,DIVISION;

User can also ask "Display Total Amount for BBA BU in each quarter"

SELECT B.BU,A.QUARTER_NAME ,MIN(A.AMOUNT)  FROM FINANCIALS.MARVELL_DEMO.PROJECTED_INVENTORY  A
INNER JOIN FINANCIALS.MARVELL_DEMO.ITEM_DETAILS  B 
ON A.ITEM_WID = B.ITEM_WID  
WHERE BU = 'BBA'
GROUP BY B.BU, A.QUARTER_NAME;

Questions about Inventory Amount as per quarter should query FINANCIALS.MARVELL_DEMO.INVENTORY_ACTUALS
Questions about Yield Quantity & Yield Amount per quarter should query  FINANCIALS.MARVELL_DEMO.INVENTORY_ON_HANDS 
Questions about Item (Division, Product line, Part Number Etc.) should query FINANCIALS.MARVELL_DEMO.ITEM_DETAILS 
Questions about Inventory & Future Projections should query FINANCIALS.MARVELL_DEMO.PROJECTED_INVENTORY
 
The financial figure column names include underscores _, so if a user asks for free cash flow, make sure this is converted to FREE_CASH_FLOW. 
Some figures may have slightly different terminology, so find the best match to the question. For instance, if the user asks about Sales and General expenses, look for something like SELLING_AND_GENERAL_AND_ADMINISTRATIVE_EXPENSES
 
If the user asks about information from multiple tables, create join logic that uses the ITEM_WID to join the tables and populate appropriate Columns to display. Don't use SQL terms for the table alias though. Just use a, b, c, etc.
Question: {question}
Context: {context}

SQL: ```sql ``` \n
 
"""
FS_PROMPT = PromptTemplate(input_variables=["question", "context"], template=FS_TEMPLATE, )

llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0.1,
    max_tokens=1000, 
    openai_api_key=st.secrets["openai_key"]
)


def get_faiss():
    " get the loaded FAISS embeddings"
    embeddings = OpenAIEmbeddings(openai_api_key=st.secrets["openai_key"])
    return FAISS.load_local("faiss_index", embeddings)

def fs_chain(question):
    """
    returns a question answer chain for faiss vectordb
    """
    docsearch = get_faiss()
    qa_chain = RetrievalQA.from_chain_type(llm, 
                                           retriever=docsearch.as_retriever(),
                                           chain_type_kwargs={"prompt": FS_PROMPT})
    return qa_chain({"query": question})

st.set_page_config(layout="wide")

username=st.secrets["streamlit_username"]
password=st.secrets["streamlit_password"]
column_list = ['ITEM_WID','AMOUNT','QUARTER_NAME','QUANTITY','CUM_YIELD','YIELD_QUANTITY','COMPANY','DIVISION','BU','PRODUCT_LINE','SUB_PRODUCT_LINE','FINANCIAL_GROUP','PART_NUMBER','ITEM_STAGE','ASSY_PART_NUMBER','DIE_PART_NUMBER','ECCN','FAB_PART_NUMBER','SCHEDULE_B_NUM','TEST_PART_NUMBER','PLATFORM','BASE_DIE','BASE_DIE_REV','FAB_HOUSE','DESIGN_COUNTRY','MARKETING_ITEM','ITEM_TYPE','PLANNER_CODE','INVENTORY_ORGANIZATION','COUNTRY_OF_MANUFACTURING','DEVICE','PRODUCT_GROUP','PROJECT_CODE','PROJECT_CODE_DESCRIPTION','PACKAGE_CODE','SERVICE_PART_NUMBER','LICENSE_EXCEPTION','END_MARKET','SUB_MARKET','MODEL_NUMBER','SPEED','ITEM_TYPE_GROUP','MPR_YEAR_CATEGORY','MPR_YEAR_CATEGORY_GROUP','MPR_YEAR_CATEGORY_SORTING','CURRENT_MODEL_NUMBER','SALES_COMP_DIVISION','SALES_COMP_BU','SALES_COMP_PRODUCT_LINE','SALES_COMP_FINANCIAL_GROUP','SALES_COMP_SUB_PRODUCT_LINE','TECHNOLOGY_GROUP','IDENTIFIED_IP','BUSINESS_OWNER','PRODUCT_LINE_MANAGER']
cutoff = 20
# establish snowpark connection
conn = st.connection("snowpark")

# Reset the connection before using it if it isn't healthy
try:
    query_test = conn.query('select 1')
except:
    conn.reset()

# adding this to test out caching
st.cache_data(ttl=86400)

def plot_financials(df_2, x, y, x_cutoff, title):
    """"
    helper to plot the altair financial charts
    
    return st.altair_chart(alt.Chart(df_2.head(x_cutoff)).mark_bar().encode(
        x=x,
        y=y
        ).properties(title=title)
    ) 
    """
    #df_subset = df_2.head(x_cutoff)
    df = pd.DataFrame(df_2)
    #st.write(df)
    #st.write(df.dtypes)
    #df["df.columns[1:]"] = df["df.columns[1:]"].astype(int)
    #st.write(df.dtypes)
    # Create a bar chart using st.bar_chart()
    return st.bar_chart(data=df,x=df.columns[0], y=df.columns[1:], color=None,width=0, height=300, use_container_width=True)

# adding this to test out caching
st.cache_data(ttl=86400)

def sf_query(str_input):
    """
    performs snowflake query with caching
    """
    data = conn.query(str_input)
    return data

def creds_entered():
    if len(st.session_state["streamlit_username"])>0 and len(st.session_state["streamlit_password"])>0:
          if  st.session_state["streamlit_username"].strip() != username or st.session_state["streamlit_password"].strip() != password: 
              st.session_state["authenticated"] = False
              st.error("Invalid Username/Password ")

          elif st.session_state["streamlit_username"].strip() == username and st.session_state["streamlit_password"].strip() == password:
              st.session_state["authenticated"] = True


def authenticate_user():
      if "authenticated" not in st.session_state:
        buff, col, buff2 = st.columns([1,1,1])
        col.text_input(label="Username:", value="", key="streamlit_username", on_change=creds_entered) 
        col.text_input(label="Password", value="", key="streamlit_password", type="password", on_change=creds_entered)
        return False
      else:
           if st.session_state["authenticated"]: 
                return True
           else:  
                  buff, col, buff2 = st.columns([1,1,1])
                  col.text_input(label="Username:", value="", key="streamlit_username", on_change=creds_entered) 
                  col.text_input(label="Password:", value="", key="streamlit_password", type="password", on_change=creds_entered)
                  return False

if authenticate_user():
    with st.sidebar:
      image = Image.open("assets/jadenew.png")
      image = st.image('assets/jadenew.png',width=280)
      selected = option_menu( menu_title="Menu",
      menu_icon = "search",
      options=["Finance Data"], 
      icons=['database'],  
      default_index=0,
      styles={#"container":{"font-family": "Garamond"},
        "nav-link": {"font-family": "Source Sans Pro"},"font-size": "12px", "text-align": "left", "margin":"0px", "--hover-color": "grey"})
    if selected =='Finance Data':
        str_input = st.chat_input("Enter your question:")
        st.markdown("""
        I am  Finance Assistant of your company. I possess the ability to extract information from your company's financial statements like balance sheet, income statements, etc spanning across 2003 to 2022. Please ask me questions and I will try my level best to provide accurate responses.
          
      
          **Some Sample Questions:**
      
          - What was the total Ending Gross Inventory dollar amount at the end of last quarter?
          - What is the projected inventory for all the parts in CCS BU per quarter?
          - How many 5nm parts are available and in what BU?
          - What is the Inventory on hand for 5nm parts in 2024-Q4 and what is the average yield quantity?

        
        
        """)
        
        if "messages" not in st.session_state.keys():
              st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                role = message["role"]
                df_str = message["content"]
                if role == "user":
                    st.markdown(message["content"], unsafe_allow_html = True)
                    continue
                csv = StringIO(df_str)
                df_data = pd.read_csv(csv, sep=',')
                col1, col2 = st.columns(2)
                df_data.columns = df_data.columns.str.replace('_', ' ')
                headers = df_data.columns
                
                with col1:
                    st.markdown(tabulate(df_data, tablefmt="html",headers=headers,showindex=False), unsafe_allow_html = True) 
                    if len(df_data.index) >2 & len(df_data.columns) == 2:
                        title_name = df_data.columns[0]+'-'+df_data.columns[1]
                        with col2:
                                grph_ser_val_x1  = df_data.iloc[:,0]
                                grph_ser_val_y1  = df_data.iloc[:,1].apply(lambda x : float(x.replace(',','')))
                                frame = {df_data.columns[0] : grph_ser_val_x1,
                                         df_data.columns[1] : grph_ser_val_y1}
                                df_final1 = pd.DataFrame(frame)
                                plot_financials(df_final1,df_data.columns[0],df_data.columns[1], cutoff,title_name)
        
        if prompt := str_input:
            st.chat_message("user").markdown(prompt, unsafe_allow_html = True)
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})

            try:
                #st.write(str_input)
                output = fs_chain(str_input)
                #st.write(output)
                #st.write(output['result'])
                try:
                    # if the output doesn't work we will try one additional attempt to fix it
                    query_result = sf_query(output['result'])
                    if len(query_result) >= 1:
                      with st.chat_message("assistant"):
                        df_2 = pd.DataFrame(query_result)
                        for name in df_2.columns:
                            if name in column_list:
                                new_name = f"{name} ($ thousands)"
                                df_2.rename(columns={name : new_name}, inplace=True)
                        
                            #st.bar_chart(df_2) 
                        col1, col2 = st.columns(2)
                        df_2.columns = df_2.columns.str.replace('_', ' ')
                        headers = df_2.columns
                        with col1:
                         st.markdown(tabulate(df_2, tablefmt="html",headers=headers,showindex=False), unsafe_allow_html = True) 
                        if len(df_2.index) >2 & len(df_2.columns) == 2:
                            title_name = df_2.columns[0]+'-'+df_2.columns[1]
                            with col2:
                                grph_ser_val_x  = df_2.iloc[:,0]
                                grph_ser_val_y  = df_2.iloc[:,1].apply(lambda x : float(x.replace(',','')))
                                frame = {df_2.columns[0] : grph_ser_val_x,
                                         df_2.columns[1] : grph_ser_val_y}
                                df_final = pd.DataFrame(frame)
                                plot_financials(df_final,df_2.columns[0],df_2.columns[1], cutoff,title_name)
                      #st.session_state.messages.append({"role": "assistant", "content": tabulate(df_2, tablefmt="html",headers=headers,showindex=False)})
                        st.session_state.messages.append({"role": "assistant", "content": df_2.to_csv(sep=',', index=False)})
                        
                    else:
                      with st.chat_message("assistant"):
                        st.write("Please try to improve your question.")
      
                except:                   
                      #st.session_state.messages.append({"role": "assistant", "content": "The first attempt didn't pull what you were needing. Trying again..."})
                      output = fs_chain(f'You need to fix the code but ONLY produce SQL code output. If the question is complex, consider using one or more CTE. Examine the DDL statements and answer this question: {output}')
                      st.write(sf_query(output['result']))
            except Exception as error:
              st.write(error)
              with st.chat_message("assistant"):
                st.markdown("Please try to improve your question.")
                #st.session_state.messages.append({"role": "assistant", "content": "Please try to improve your question. Note this tab is for financial statement questions. Use Tab 2 to ask from Annual Reports ."})
