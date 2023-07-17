import pyodbc

class DBConnector:
    def __init__(self, db_type, server, database, username, password):
        self.db_type = db_type
        self.server = server
        self.database = database
        self.username = username
        self.password = password

    def get_conn_str(self):
        # Generate the connection string based on the database type
        if self.db_type == "sql_server":
            return f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}"
        elif self.db_type == "mysql":
            return f"DRIVER={{MySQL ODBC 8.0 Unicode Driver}};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}"
        elif self.db_type == "postgresql":
            return f"DRIVER={{PostgreSQL Unicode}};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}"

    def connect(self):
        # Establish a connection to the database using the connection string
        conn_str = self.get_conn_str()
        self.connection = pyodbc.connect(conn_str)
        return self.connection
    
    def get_db_structure(self):
        # Retrieve the structure of the database (table names, column names, and data types)
        cursor = self.connection.cursor()
        db_type = self.db_type.lower()

        if db_type == "sql_server":
            query = """
                SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
                FROM INFORMATION_SCHEMA.COLUMNS
                ORDER BY TABLE_NAME, ORDINAL_POSITION
            """
        elif db_type == "mysql":
            query = """
                SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = '{}'
                ORDER BY TABLE_NAME, ORDINAL_POSITION
            """.format(self.database)
        elif db_type == "postgresql":
            query = """
                SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_CATALOG = %s
                ORDER BY TABLE_NAME, ORDINAL_POSITION
            """
        
        cursor.execute(query)
        structure = {}
        
        for row in cursor.fetchall():
            table_name = row.TABLE_NAME
            column_name = row.COLUMN_NAME
            data_type = row.DATA_TYPE
            if table_name not in structure:
                structure[table_name] = []
            structure[table_name].append((column_name, data_type))

        return structure

    def close(self):
        # Close the database connection if it is open
        if self.connection:
            self.connection.close()
