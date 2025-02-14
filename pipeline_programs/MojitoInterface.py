import os, json, mojito

import datetime as dt 
import pandas   as pd 

from threading import Lock 

from config.DBInterfacePostgres          import DBInterface 
from concurrent.futures                  import ThreadPoolExecutor 
from custom_exceptions.custom_exceptions import extraction_exception

class MojitoInterface:
    def mojito_interface_settings_method(self, sql_type: str, hostname: str, server_name: str, schema_name: str):
        self.schema_name = schema_name 
        self.output_data = []
        self.thread_lock = Lock()
        self.__db_object = DBInterface()
        self.__db_object.connection_settings(sql_type, os.getenv("ADMIN_NAME"), os.getenv("ADMIN_PWD"), hostname, server_name)

        self.__api_interface = mojito.KoreaInvestment(
            api_key    = os.getenv("MOJITO_API_KEY"),
            api_secret = os.getenv("MOJITO_API_SECRET"), 
            acc_no     = os.getenv("MOJITO_ACCOUNT_NO")
        )

    def get_stock_data(self, date_range: str, stocks_list: list[str]):
        @extraction_exception
        def extract_data(start_date: str, end_date: str, symbol: str):
            company_dataframe = pd.DataFrame(self.__api_interface.fetch_ohlcv(symbol = symbol, timeframe = "D", start_day = start_date, end_day = end_date)["output2"])

            if (len(company_dataframe.columns) > 0):
                with self.thread_lock:
                    self.output_data.append(company_dataframe)
            
        start_date, end_date = [date_string.strip() for date_string in date_range.split("~")]

        with ThreadPoolExecutor(max_workers = 4) as executor:
            for symbol in stocks_list: 
                executor.submit(extract_data, start_date, end_date, symbol)

            executor.shutdown(True)
            
