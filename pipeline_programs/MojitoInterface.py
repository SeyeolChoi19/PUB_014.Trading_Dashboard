import os, json, mojito

import datetime as dt 
import pandas   as pd 

from config.DBInterfacePostgres import DBInterface 

class MojitoInterface:
    def mojito_interface_settings_method(self, date_range: str, stocks_list: list[str]):
        self.date_range  = date_range 
        self.stocks_list = stocks_list 
        self.output_data = []

        self.__api_interface = mojito.KoreaInvestment(
            api_key    = os.getenv("MOJITO_API_KEY"),
            api_secret = os.getenv("MOJITO_API_SECRET"), 
            acc_no     = os.getenv("MOJITO_ACCOUNT_NO")
        )
