import os, json 

import datetime as dt 
import pandas   as pd 

from config.SeleniumSettings    import SeleniumSettings 
from config.DBInterfacePostgres import DBInterface

class HankyungScraper:
    def __init__(self, selenium_object: SeleniumSettings):
        self.selenium_object = selenium_object 
        self.selenium_object.driver_settings()

    def hankyung_scraper_settings_method(self, hankyung_news_portal: str, hankyung_news_table_name: str, target_date: str, sql_type: str, server_name: str, hostname: str, server_schema_name: str):
        self.hankyung_news_portal       = hankyung_news_portal 
        self.hankyung_news_table_name   = hankyung_news_table_name 
        self.target_date                = target_date
        self.server_schema_name         = server_schema_name 
        self.article_dictionary_columns = ["article_date", "article_source", "article_link", "article_title", "article_text"]
        self.news_articles_dictionary   = []
        self.__database_interface       = DBInterface()
        self.__database_interface.connection_settings(sql_type, os.getenv("ADMIN_NAME"), os.getenv("ADMIN_PWD"), hostname, server_name)
    
    def collect_hankyung_news_urls(self):
        def save_article_data():
            for (article_date, article_url, article_title) in zip(article_dates, article_urls, titles_list):
                sub_date = str(article_date)[0:10]

                if ((sub_date >= self.target_date) and (self.__database_interface.check_if_data_exists_in_column(self.hankyung_news_table_name, "article_link", article_url, self.server_schema_name)[0][0] != 1)):
                    results_list = [sub_date.replace(".", "-"), "hankyung", article_url, article_title]
                    self.news_articles_dictionary.append(results_list)
            
            return min(article_dates)

        article_date, page_counter = str(dt.datetime.now().date()), 1

        while (article_date >= self.target_date):
            self.selenium_object.driver.get(self.hankyung_news_portal.format(page_counter))
            elements_list = self.selenium_object.find_nested_elements("div.txt-cont h3.news-tit a", hankyung_scraper.selenium_object.search_for_element("news-list"), "css")
            article_dates = [element.text for element in self.selenium_object.find_nested_elements("txt-date", self.selenium_object.search_for_element("news-list"))]
            article_urls  = [element.get_attribute("href") for element in elements_list]
            titles_list   = [element.text for element in elements_list]
            article_date  = save_article_data()
            page_counter += 1

    def collect_article_texts(self):
        for sub_list in self.news_articles_dictionary:
            self.selenium_object.driver.get(sub_list[2])
            article_text = self.selenium_object.wait_for_element_and_return_element("article-body").text if (self.selenium_object.check_for_element("article-body")) else ""
            sub_list.append(article_text)

    def upload_data_to_database(self):
        output_dataframe = pd.DataFrame(self.news_articles_dictionary, columns = self.article_dictionary_columns)
        self.__database_interface.upload_to_database(self.hankyung_news_table_name, output_dataframe, schema_name = self.server_schema_name)

if (__name__ == "__main__"):
    with open("./config/BackendConfig.json", "r", encoding = "utf-8") as f:
        config_dict = json.load(f)

    hankyung_scraper = HankyungScraper(SeleniumSettings(**config_dict["HankyungScraper"]["constructor"]))
    hankyung_scraper.hankyung_scraper_settings_method(**config_dict["HankyungScraper"]["hankyung_scraper_settings_method"])
    hankyung_scraper.collect_hankyung_news_urls()
    hankyung_scraper.collect_article_texts()
    hankyung_scraper.upload_data_to_database()
