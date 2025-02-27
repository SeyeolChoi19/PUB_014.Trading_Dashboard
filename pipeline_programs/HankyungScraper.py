import os, json 

import datetime as dt 
import pandas   as pd 

from threading import Lock

from config.SeleniumSettings             import SeleniumSettings 
from config.DBInterfacePostgres          import DBInterface
from concurrent.futures                  import ThreadPoolExecutor 
from custom_exceptions.custom_exceptions import database_upload_exception
from custom_exceptions.custom_exceptions import extraction_exception

class HankyungScraper:
    def __init__(self, driver_path: str, max_wait_time: int):
        self.driver_path   = driver_path 
        self.max_wait_time = max_wait_time
        
    def hankyung_scraper_settings_method(self, hankyung_news_table_name: str, target_date: str, sql_type: str, server_name: str, hostname: str, server_schema_name: str, hankyung_news_portals: list[str]):
        self.hankyung_news_table_name   = hankyung_news_table_name 
        self.target_date                = target_date
        self.server_schema_name         = server_schema_name 
        self.hankyung_news_portals      = hankyung_news_portals 
        self.article_dictionary_columns = ["article_date", "article_source", "article_link", "article_title", "article_text"]
        self.thread_lock_object         = Lock()
        self.news_articles_dictionary   = []
        self.__database_interface       = DBInterface()
        self.__database_interface.connection_settings(sql_type, os.getenv("ADMIN_NAME"), os.getenv("ADMIN_PWD"), hostname, server_name)
    
    @extraction_exception
    def collect_hankyung_news_urls(self):
        def save_article_data(article_dates: list[str], article_urls: list[str], titles_list: list[str]):
            for (article_date, article_url, article_title) in zip(article_dates, article_urls, titles_list):
                sub_date = str(article_date).replace(".", "-")[0:10]

                if ((sub_date >= self.target_date) and (self.__database_interface.check_if_data_exists_in_column(self.hankyung_news_table_name, "article_link", article_url, self.server_schema_name)[0][0] != 1)):
                    results_list = [sub_date, "hankyung", article_url, article_title]
                    
                    with self.thread_lock_object:
                        self.news_articles_dictionary.append(results_list)
            
            return min(article_dates)

        def multithreaded_collector(page_url: str):
            selenium_object, article_date, page_counter = SeleniumSettings(self.driver_path, self.max_wait_time), str(dt.datetime.now().date()), 1
            selenium_object.driver_settings()
            
            while (article_date >= self.target_date):
                selenium_object.driver.get(page_url.format(page_counter))
                article_dates = [element.text for element in selenium_object.find_nested_elements("txt-date", selenium_object.search_for_element("news-list"))]
                article_urls  = [selenium_object.search_for_element(f"/html/body/main/div[1]/div/div[1]/ul/li[{index}]/div/div/h2/a", "xpath").get_attribute("href") for index in range(1, 21)]
                titles_list   = [element.text for element in selenium_object.find_nested_elements("news-tit", selenium_object.search_for_element("news-list"))]
                page_counter += 1                    
                article_date  = save_article_data(article_dates, article_urls, titles_list)

            selenium_object.driver.close()

        with ThreadPoolExecutor(max_workers = 4) as executor:
            for page_url in self.hankyung_news_portals:
                executor.submit(multithreaded_collector, page_url)

    @extraction_exception
    def collect_article_texts(self):    
        def threaded_article_collector(sub_list: list[list[str]]):
            selenium_object = SeleniumSettings(self.driver_path, self.max_wait_time)
            selenium_object.driver_settings()
        
            for sub_list in sub_list:
                selenium_object.driver.get(sub_list[2])
                article_text = selenium_object.wait_for_element_and_return_element("article-body").text if (selenium_object.check_for_element("article-body")) else ""
                sub_list.append(article_text)

            selenium_object.driver.close()

            return sub_list

        segment_size, results_data = len(self.news_articles_dictionary) // 4, []

        with ThreadPoolExecutor(max_workers = 4) as executor:
            for index in range(0, len(self.news_articles_dictionary), segment_size):
                sub_dictionary = self.news_articles_dictionary[index : index + segment_size]
                results_data.append(executor.submit(threaded_article_collector, sub_dictionary))
        
        self.news_articles_dictionary = [future_object.result() for future_object in results_data]

    @database_upload_exception        
    def upload_data_to_database(self):
        output_dataframe = pd.DataFrame(self.news_articles_dictionary, columns = self.article_dictionary_columns)
        self.__database_interface.upload_to_database(self.hankyung_news_table_name, output_dataframe, schema_name = self.server_schema_name)

if (__name__ == "__main__"):
    with open("./config/BackendConfig.json", "r", encoding = "utf-8") as f:
        config_dict = json.load(f)

    hankyung_scraper = HankyungScraper(**config_dict["HankyungScraper"]["constructor"])
    hankyung_scraper.hankyung_scraper_settings_method(**config_dict["HankyungScraper"]["hankyung_scraper_settings_method"])
    hankyung_scraper.collect_hankyung_news_urls()
    hankyung_scraper.collect_article_texts()
    hankyung_scraper.upload_data_to_database()
