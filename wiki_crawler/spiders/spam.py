# https://shophso.com/
from scrapy import Spider
from tqdm import tqdm
import scrapy

class spam(Spider):
    name = "spam"
    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        print("hello")
        self._spam()
        
    def _spam(self):
        url = "https://shophso.com/"
        for i in tqdm(range(1000000000)):
            text = scrapy.Request(url=url, callback=self.parse)
            # print(text)
    
    def parse(self, response):
        text = response.xpath("/html/body/div[1]/div[2]/div[1]/div/div/h2/text()").get()
        return text