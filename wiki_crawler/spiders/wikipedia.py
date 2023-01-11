import scrapy
from scrapy import Spider
import os
import json
from bs4 import BeautifulSoup

class Wikipedia(Spider):
    name="wikipedia"
    url="https://vi.wikipedia.org"
    start_urls = [
        r"https://vi.wikipedia.org/w/index.php?title=Đặc_biệt:Mọi_bài&from=A",
    ]
    data_dir="datas"
    
    def __init__(self, name=None, **kwargs):
        super(Wikipedia, self).__init__(name, **kwargs)
        if not os.path.exists(self.data_dir):
            os.mkdir(self.data_dir)
    
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url, callback=self.parse
            )
    
    def parse(self, response):
        table_content = response.xpath(
            '//*[@id="mw-content-text"]/div[3]'
        )
        
        article_links = table_content.css('a.mw-redirect::attr(href)').getall()
        
        for article in article_links:
            url = f'{self.url}/{article}'
            
            yield scrapy.Request(
                url=url, callback=self.parse_article
            )
            
        next_url = response.xpath('//*[@id="mw-content-text"]/div[4]/a/@href').getall()[-1]
        next_url = self.url + next_url
        print("next_url: ", next_url+url)
        
        yield scrapy.Request(
                url=next_url, callback=self.parse
            )
            
    def parse_article(self, response):
        title = response.xpath('//*[@id="firstHeading"]/span/text()').get()
        content = response.xpath('//*[@id="mw-content-text"]').extract_first()
        content = self.extract_text(content) 
        url = response.url
        article = {
            "url": url,
            "title":title,
            "content":content
        }
        
        file_name = title.replace(" ", "_")
        abs_path = f'{self.data_dir}/{file_name}.json'
        
        with open(abs_path, "w") as f:
            json_obj = json.dumps(article, indent=4, ensure_ascii=False)
            f.write(json_obj)
        print(f'saved: {abs_path}')
    
    def extract_text(self, html):
        soup = BeautifulSoup(html,'html.parser')
        try:
            # remove table tag
            table = soup.table
            table.decompose()
            
            # remove hide-when-compact class
            for rm in soup.find_all("div", {'class':'hide-when-compact'}): 
                rm.decompose()
                
            # remove mw-editsection
            for rm in soup.find_all("div", {'class':'mw-editsection'}): 
                rm.decompose()
                
            # remove reflist
            
            for rm in soup.find_all("div", {'class':'reflist'}): 
                rm.decompose()
                
            # remove navbox authority-control
            for rm in soup.find_all("div", {'class':'navbox authority-control'}): 
                rm.decompose()
                
            # remove navbox
            for rm in soup.find_all("div", {'class':'navbox'}): 
                rm.decompose()
        finally:

            text = []

            for tag in soup.find_all():
                if tag.name in set(["p", "a", "i", "div"]):
                    text.append(tag.text)
                    
            return " \n ".join(text)