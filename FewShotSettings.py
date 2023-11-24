class few_shot_settings:
    
    @staticmethod
    def get_prefix():
        return f"""
		You are an agent designed to interact with a Snowflake with schema detail in Snowflake querying about Company Inventory & Item statements. You have to write syntactically correct Snowflake sql query based on a users question.
		No matter what the user asks remember your job is to produce relevant SQL and only include the SQL, not the through process. So if a user asks to display something, you still should just produce SQL.
        Never query for all the columns from a specific table, only ask for a the few relevant columns given the question.
		If you don't know the answer, provide what you think the sql should be but do not make up code if a column isn't available. Use snowflake aggregate functions like SUM, MIN, MAX, etc. if user ask to find total, minimum or maximum.
        DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database. 
		Few rules to follow are
		1. always interpret QUARTER_NMAE in the format YYYY-QQ from various inputs from user for example inputs like Q1'22 or 1st qtr 22 or 2022 quarter1 or 22Q1 or 22'Q1 or 22 Q1 should be translated as YYYY-QQ 
		2. Always use column aliases as per example
        """
    
    @staticmethod
    def get_suffix():
        return """Question: {question}
        Context: {context}

        SQL_cmd: ```sql ``` \n

        """, ["question", "context"]
    
    @staticmethod
    def get_examples():
        examples = [
            {
                "input": "Display Aggregated Amount for Each Quarter.?",
                "sql_cmd": '''SELECT QUARTER_NAME AS "QUARTER", SUM(AMOUNT) AS "TOTAL AMOUNT" FROM FINANCIALS.MARVELL_DEMO.INVENTORY_ACTUALS GROUP BY QUARTER_NAME;''',
            },
            {
                "input": "Display me count of distinct products as per BU for SPG Division",
                "sql_cmd": '''SELECT COUNT(*) AS "TOTAL COUNT", BU as "BU", DIVISION AS "DIVISION" FROM FINANCIALS.MARVELL_DEMO.ITEM_DETAILS WHERE DIVISION  = \'SPG\' GROUP BY BU ,DIVISION;''',
            },
            {
                "input": "Display Total Inventory Amount for each quarter in business unit BBA",
                "sql_cmd": '''SELECT B.BU AS "BU", A.QUARTER_NAME AS "QUARTER", SUM(A.AMOUNT) AS "TOTAL AMOUNT" FROM FINANCIALS.MARVELL_DEMO.PROJECTED_INVENTORY  A INNER JOIN FINANCIALS.MARVELL_DEMO.ITEM_DETAILS  B ON A.ITEM_WID = B.ITEM_WID WHERE B.BU = \'BBA\' GROUP BY B.BU, A.QUARTER_NAME,A.AMOUNT;''',
            },
            {
                "input": "Display projected Inventory for BBA organization in YEAR 2021 and Quarter Q4",
                "sql_cmd": '''SELECT A.ITEM_WID AS "ITEM WID", A.AMOUNT AS "AMOUNT" FROM FINANCIALS.MARVELL_DEMO.PROJECTED_INVENTORY A INNER JOIN FINANCIALS.MARVELL_DEMO.ITEM_DETAILS B ON A.ITEM_WID = B.ITEM_WID WHERE B.BU = \'BBA\' AND A.QUARTER_NAME = \'2021-Q4\';''',
            },
        ]
        return examples

    @staticmethod
    def get_example_template():
        template = """
        Input: {input}
        SQL_cmd: {sql_cmd}\n
        """
        example_variables = ["input", "sql_cmd"]
        return template, example_variables