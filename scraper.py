import cloudscraper
from lxml import html

class FragranticaScraper:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper(browser={'browser': 'firefox', 'platform': 'windows', 'desktop': True})

    def get_first_or_none(self, tree, xpath_query):
        result = tree.xpath(xpath_query)
        if result:
            return result[0].strip()
        else:
            return None


    def fetch_page(self, url):
        response = self.scraper.get(url)

        if response.status_code != 200:
            self.scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True})
            response = self.scraper.get(url)

        if response.status_code != 200:
            raise ConnectionError(f"Fragrantica rejected connection. Status code: {response.status_code}")
        
        return response.content
    
    def get_perfume_data(self, url):
        html_content = self.fetch_page(url)
        tree = html.fromstring(html_content)

        data = {
            "fragrance": self.get_first_or_none(tree, '//*[@id="toptop"]/h1/text()'),
            "gender": self.get_first_or_none(tree, '//*[@id="toptop"]/h1/span/text()'),
            "rating": self.get_first_or_none(tree, '//*[@id="app"]/main/div/div[1]/div[1]/div[4]/div[3]/p/span[1]/text()'),
            "amount_of_rates": self.get_first_or_none(tree, '//*[@id="app"]/main/div/div[1]/div[1]/div[4]/div[3]/p/span[3]/text()'),
            "acords": {acord: self.get_first_or_none(tree, f'//*[@id="app"]/main/div/div[1]/div[1]/div[2]/div[2]/div/div/div[{acord}]/div/span/text()') for acord in range(1, 11)},
            "url": url
        }
        return data
    

scraper = FragranticaScraper()
data = scraper.get_perfume_data("https://www.fragrantica.pl/perfumy/Guerlain/Guerlain-Homme-Eau-de-Parfum-2016--47793.html")

print(data)