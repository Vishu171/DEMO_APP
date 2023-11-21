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

FS_TEMPLATE = """ You are an expert SQL developer querying about financials statements. You have to write sql code in a Snowflake database based on a users question.
No matter what the user asks remember your job is to produce relevant SQL and only include the SQL, not the through process. So if a user asks to display something, you still should just produce SQL.
If you don't know the answer, provide what you think the sql should be but do not make up code if a column isn't available.

As an example, a user will ask "Display the last 5 years of net income.?" The SQL to generate this would be:

select year, net_income
from financials.marvell_prod.income_statement_annual
where ticker = 'TICKER'
order by year desc
limit 5;

Questions about income statement fields should query financials.prod.income_statement_annual
Questions about balance sheet fields (assets, liabilities, etc.) should query  financials.prod.balance_sheet_annual
Questions about cash flow fields (operating cash, investing activities, etc.) should query financials.prod.cash_flow_statement_annual

If question doesn't have company name or ticker mentioned, use default ticker value of 'MRVL'.

The financial figure column names include underscores _, so if a user asks for free cash flow, make sure this is converted to FREE_CASH_FLOW. 
Some figures may have slightly different terminology, so find the best match to the question. For instance, if the user asks about Sales and General expenses, look for something like SELLING_AND_GENERAL_AND_ADMINISTRATIVE_EXPENSES

If the user asks about multiple figures from different financial statements, create join logic that uses the ticker and year columns. Don't use SQL terms for the table alias though. Just use a, b, c, etc.
The user may use a company name so convert that to a ticker.

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
    return FAISS.load_local("/content/drive/MyDrive/streamlit-buffett-main/faiss_index", embeddings)

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
column_list = ['CASH_AND_CASH_EQUIVALENTS','SHORT_TERM_INVESTMENTS','RECEIVABLES','INVENTORY','OTHER_CURRENT_ASSETS','TOTAL_CURRENT_ASSETS','PROPERTY_PLANT_AND_EQUIPMENT','GOODWILL','INTANGIBLE_ASSETS','ACCUMULATED_AMORTIZATION','OTHER_ASSETS','TOTAL_ASSETS','ACCOUNTS_PAYABLE_AND_ACCRUED_EXPENSES','SHORT_OR_CURRENT_LONG_TERM_DEBT','OTHER_CURRENT_LIABILITIES','TOTAL_CURRENT_LIABILITIES','LONG_TERM_DEBT','OTHER_LIABILITIES','DEFERRED_LONG_TERM_LIABILITY_CHARGES','MINORITY_INTEREST','NEGATIVE_GOODWILL','TOTAL_LIABILITIES','MISC_STOCKS_OPTIONS_WARRANTS','REDEEMABLE_PREFERRED_STOCK','PREFERRED_STOCK','COMMON_STOCK','RETAINED_EARNINGS','TREASURY_STOCK','CAPITAL_SURPLUS','OTHER_STOCKHOLDER_EQUITY','TOTAL_STOCKHOLDER_EQUITY','NET_TANGIBLE_ASSETS','NET_INCOME','DEPRECIATION','CHANGES_IN_ACCOUNTS_RECEIVABLES','CHANGES_IN_ASSETS_AND_LIABILITIES','CHANGES_IN_INVENTORIES','CHANGES_IN_OTHER_OPERATING_ACTIVITIES','TOTAL_CASH_FLOW_FROM_OPERATING_ACTIVITIES','CAPITAL_EXPENDITURES','INVESTMENTS','OTHER_CASH_FLOWS_FROM_INVESTING_ACTIVITIES','TOTAL_CASH_FLOWS_FROM_INVESTING_ACTIVITIES','DIVIDENDS_PAID','SALE_OR_PURCHASE_OF_STOCK','NET_BORROWINGS','OTHER_CASH_FLOWS_FROM_FINANCING_ACTIVITIES','TOTAL_CASH_FLOWS_FROM_FINANCING_ACTIVITIES','CHANGE_IN_CASH_AND_CASH_EQUIVALENTS','TOTAL_REVENUE','COST_OF_REVENUE','GROSS_PROFIT','RESEARCH_DEVELOPMENT','SELLING_GENERAL_AND_ADMINISTRATIVE','NON_RECURRING','OTHERS','TOTAL_OPERATING_EXPENSES','OPERATING_INCOME_OR_LOSS','TOTAL_OTHER_INCOME_OR_EXPENSES_NET','EARNINGS_BEFORE_INTEREST_AND_TAXES','INTEREST_EXPENSE','INCOME_BEFORE_TAX','INCOME_TAX_EXPENSE','MINORITY_INTEREST','NET_INCOME_FROM_CONTINUING_OPS','DISCONTINUED_OPERATIONS','EXTRAORDINARY_ITEMS','EFFECT_OF_ACCOUNTING_CHANGES','OTHER_ITEMS','NET_INCOME','PREFERRED_STOCK_AND_OTHER_ADJUSTMENTS','NET_INCOME_APPLICABLE_TO_COMMON_SHARES']
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
      
          - What is the net income of Marvell in 2022?
          - What is the gross profit in last 3 years?
        
        
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
                        st.write("Please try to improve your question. Note this tab is for financial statement questions. Use Tab 2 to ask from Annual Reports .")
      
                except:                   
                      #st.session_state.messages.append({"role": "assistant", "content": "The first attempt didn't pull what you were needing. Trying again..."})
                      output = fs_chain(f'You need to fix the code but ONLY produce SQL code output. If the question is complex, consider using one or more CTE. Examine the DDL statements and answer this question: {output}')
                      st.write(sf_query(output['result']))
            except Exception as error:
              st.write(error)
              with st.chat_message("assistant"):
                st.markdown("Please try to improve your question. Note this tab is for financial statement questions. Use Tab 2 to ask from Annual Reports .")
                #st.session_state.messages.append({"role": "assistant", "content": "Please try to improve your question. Note this tab is for financial statement questions. Use Tab 2 to ask from Annual Reports ."})
