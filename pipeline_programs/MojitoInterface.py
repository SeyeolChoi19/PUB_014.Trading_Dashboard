import os, json, mojito

import datetime as dt 
import pandas   as pd 

from threading import Lock 

from config.DBInterfacePostgres          import DBInterface 
from concurrent.futures                  import ThreadPoolExecutor 
from custom_exceptions.custom_exceptions import extraction_exception, database_upload_exception

class MojitoInterface:
    def mojito_interface_settings_method(self, sql_type: str, hostname: str, server_name: str, schema_name: str, mojito_table: str):
        self.schema_name  = schema_name 
        self.mojito_table = mojito_table
        self.thread_lock  = Lock()
        self.__db_object  = DBInterface()
        self.__db_object.connection_settings(sql_type, os.getenv("ADMIN_NAME"), os.getenv("ADMIN_PWD"), hostname, server_name)

        self.__api_object = mojito.KoreaInvestment(
            acc_no     = "",
            api_key    = "",
            api_secret = "",
        )

    def get_stock_data(self, date_range: str, stocks_list: list[str]):
        @extraction_exception
        def extract_data(start_date: dt.datetime.date, end_date: dt.datetime.date, symbol: str):
            extraction_date = start_date

            while (str(extraction_date) <= str(end_date)):
                start_day_string = str(extraction_date.date()).replace("-", "")
                end_day_string   = str((extraction_date + dt.timedelta(30)).date()).replace("-", "")
                output_dataframe = pd.DataFrame(self.__api_object.fetch_ohlcv(symbol = symbol, timeframe = "D", start_day = start_day_string, end_day = end_day_string)["output2"])
                extraction_date += dt.timedelta(days = 30)
                
                if (len(output_dataframe.columns) > 0):
                    with self.thread_lock:
                        output_dataframe["company_code"] = symbol
                        self.output_data.append(output_dataframe)
                        print(output_dataframe)
            
        start_date, end_date = [dt.datetime.strptime(date_string.strip(), "%Y-%m-%d") for date_string in date_range.split("~")]
        self.output_data     = []

        with ThreadPoolExecutor(max_workers = 4) as executor:
            for symbol in stocks_list: 
                executor.submit(extract_data, start_date, end_date, symbol)
