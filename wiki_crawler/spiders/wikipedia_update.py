import scrapy
from scrapy import Spider
import os
import json
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import regex

class Wikipedia_Update(Spider):
    name="wikipedia_update"
    url="https://vi.wikipedia.org"
    start_urls = [
        r"https://vi.wikipedia.org/w/index.php?title=%C4%90%E1%BA%B7c_bi%E1%BB%87t:Trang_m%E1%BB%9Bi&offset=&limit=500",

    ]
    data_dir="datas"
    
    def __init__(self, num_day=5, name=None, **kwargs):
        super(Wikipedia_Update, self).__init__(name, **kwargs)
        if not os.path.exists(self.data_dir):
            os.mkdir(self.data_dir)
        
        self.num_day = int(num_day)
    
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url, callback=self.parse
            )
    
    def parse(self, response):
        table_content = response.xpath(
            '//*[@id="mw-content-text"]/ul'
        )
        # li.mw-tag-visualeditor a.mw-newpages-pagename::attr(href)
        article_links = table_content.css('li')
        print("length: ",  len(article_links))
        
        for art in article_links:
            time = art.css('a span.mw-newpages-time::text').get()
            print(time)
            time = self.parse_time(time)
            time = datetime(time["year"], time["month"], time["day"], time["hour"], time["minute"], 00)  
                     
            if (datetime.now() - time) >= timedelta(days=self.num_day):
                print("Done !")
                print(f"lastest datetime: {time}")
                return None
            else:
                print(timedelta(days=self.num_day))
                print(datetime.now()- timedelta(days=self.num_day))
                print(time) 
            
            article = art.css('a.mw-newpages-pagename::attr(href)').get()
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
        
    def parse_time(self, text):
        # time = parse_time(text="05:03, ngày 15 tháng 12 năm 2022")
        # 05:03, ngày 15 tháng 12 năm 2022
        rg = "(\d{1,2}):(\d{1,2})\,\sngày\s(\d{1,2})\stháng\s(\d{1,2})\snăm\s(\d{4})"
        
        pattern = regex.compile(rg)
        matched = pattern.findall(text)[0]
        
        return {
            "year":int(matched[4]),
            "month":int(matched[3]),
            "day":int(matched[2]),
            "minute":int(matched[1]),
            "hour":int(matched[0])
        }
            
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
        if title is not None:
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