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
        self.article_dictionary_columns = ["article_date", "article_source", "article_title", "article_text"]
        self.news_articles_dictionary   = []
        self.__database_interface       = DBInterface()
        self.__database_interface.connection_settings(sql_type, os.getenv("ADMIN_NAME"), os.getenv("ADMIN_PWD"), hostname, server_name)
    
    def collect_hankyung_news_urls(self):
        def save_article_data():
            for (article_date, article_url, article_title) in zip(article_dates, article_urls, titles_list):
                sub_date = str(article_date)[0:10]

                if ((sub_date >= self.target_date) and (self.__database_interface.check_if_data_exists_in_column(self.hankyung_news_table_name, "article_source", article_url, self.server_schema_name))):
                    results_list = [sub_date, article_url, article_title]
                    self.news_articles_dictionary.append(results_list)
            
            return min(article_dates)

        article_date, page_counter = str(dt.datetime.now().date()), 1

        while (article_date >= self.target_date):
            self.selenium_object.driver.get(self.hankyung_news_portal.format(page_counter))
            elements_list = self.selenium_object.find_nested_elements("news-tit", self.selenium_object.wait_for_element_and_return_element("news-list"), "css")
            article_dates = [element.text.replace(".", "-") for element in self.selenium_object.find_nested_elements("txt-date", self.selenium_object.search_for_element("news-list"))]
            article_urls  = [element.get_attribute("href") for element in elements_list]
            titles_list   = [element.text for element in elements_list]
            article_date  = save_article_data()
            page_counter += 1

    def collect_article_texts(self):
        for sub_list in self.news_articles_dictionary:
            self.selenium_object.driver.get(sub_list[1])
            article_text = self.selenium_object.wait_for_element_and_return_element("article-body").text if (self.selenium_object.check_for_element("article-body")) else ""
            sub_list.append(article_text)



# selenium_object = SeleniumSettings("./config/chromedriver.exe", 30)
# selenium_object.driver_settings()
# selenium_object.driver.get("https://www.hankyung.com/financial-market")
# len([element.text for element in selenium_object.search_for_elements("news-tit")])

# selenium_object.search_for_element("/html/body/div/div[2]/div/div[1]/div[3]/div/div[2]/ul/li[1]/div[1]/h3/a", "xpath").text



# import selenium

# isinstance(selenium_object.search_for_element("/html/body/div/div[2]/div/div[1]/div/div/div[2]/ul/li[1]/div[1]/h3/a", "xpath"), selenium.webdriver.remote.webelement.WebElement)


# from selenium.webdriver.common.by import By

# [element.text for element in selenium_object.search_for_element("news-list").find_elements(By.CLASS_NAME, "news-tit")]




# selenium_object.search_for_element("/html/body/div/div[2]/div/div[1]/div[3]/div/div[2]/ul/li[1]/div[1]/h3/a", "xpath").get_attribute("href")

# len([element.text for element in selenium_object.driver.find_element(By.CLASS_NAME, "news-list").find_elements(By.CSS_SELECTOR, "div.txt-cont h3.news-tit a")])

# [element for element in selenium_object.find_nested_elements("div.txt-cont h3.news-tit a", selenium_object.search_for_element("news-list"), "css")]

# selenium_object.search_for_element("article-body").text


# new_list = [[1,2,3,4], [1,2,3,4], [1,2,3,4], [1,2,3,4]]

# for sub_list in new_list:
#     sub_list.append(5)


# new_list
