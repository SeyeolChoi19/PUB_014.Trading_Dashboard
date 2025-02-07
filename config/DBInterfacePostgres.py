import psycopg2

import pandas as pd 

from sqlalchemy import create_engine
from sqlalchemy import text

class DBInterface:
    def connection_settings(self, sql_type: str, username: str, password: str, hostname: str, server_name: str):
        self.sql_type    = sql_type
        self.username    = username
        self.password    = password 
        self.hostname    = hostname 
        self.server_name = server_name
        self.engine      = create_engine(f"{sql_type}://{username}:{password}@{hostname}/{server_name}", echo = False, max_overflow = 30, pool_size = 30)
    
    def upload_to_database(self, table_name: str, df: pd.core.frame.DataFrame, exist_option: str = "append", schema_name: str = "public"):
        with self.engine.begin() as connection:
            df.to_sql(table_name, con = connection, if_exists = exist_option, index = False, schema = schema_name, chunksize = 50000)
        
    def get_from_database(self, table_id: str, columns_list: list[str], filter_condition: str = None, schema_name: str = "public"):
        columns_list   = "*" if (columns_list == ["*"]) else [f'"{column}"' for column in columns_list]
        query_str      = (lambda x: x if (filter_condition == None) else f"{x} WHERE {filter_condition}")(f"SELECT {','.join(columns_list)} FROM \"{schema_name}\".\"{table_id}\"")
        retrieved_data = self.engine.connect().execute(text(query_str)).fetchall()

        return retrieved_data

    def check_if_data_exists_in_column(self, table_id: str, column_name: str, filter_value: str, schema_name: str = "public"):
        query_string = f"SELECT (CASE WHEN (SELECT SUM(1) FROM \"{schema_name}\".\"{table_id}\" WHERE \"{column_name}\" = '{filter_value}') > 0 THEN 1 ELSE 0 END)"
        query_result = self.engine.connect().execute(text(query_string)).fetchall()

        return query_result
        
    def delete_from_database(self, table_id: str, column_name: str,  filter_value: str, filter_condition: str = "equals", schema_name: str = "public"):
        filter_dict = {
            "equals" : "=",
            "gt"     : ">",
            "lt"     : "<",
            "gte"    : ">=",
            "lte"    : "<=",
            "in"     : "in"
        }

        query_str = f'DELETE FROM "{schema_name}"."{table_id}" WHERE "{column_name}" {filter_dict[filter_condition]} {filter_value}'
        
        with self.engine.connect() as connection:
            connection.execute(text(query_str))
            connection.commit()
    
    def create_schema(self, schema_name: str):
        confirmation_query  = f"SELECT (CASE WHEN (SELECT SUM(1) FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{schema_name}') > 0 THEN 1 ELSE 0 END)"
        creation_query      = f"CREATE SCHEMA {schema_name}"
        confirmation_result = self.engine.connect().execute(text(confirmation_query)).fetchall()

        if (confirmation_result[0][0] == 0):
            with self.engine.connect() as connection:
                connection.execute(text(creation_query)).fetchall()
                connection.commit()

        return confirmation_result
