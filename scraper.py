import cloudscraper
from lxml import html

class FragranticaScraper:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper(browser={'browser': 'firefox', 'platform': 'windows', 'desktop': True})

    def get_first_or_none(self, tree, xpath_query):
        result = tree.xpath(xpath_query)
        return result[0].strip() if result else None


    def get_acords(self, tree, xpath_query):
        accords = tree.xpath(xpath_query)
        return {i: accord for i, accord in enumerate(accords, start=1) if accord.strip()}


    def extract_notes_urls(self, tree, xpath_tier):
        notes_dict = {}
        tier_notes = tree.xpath(xpath_tier)

        for note in tier_notes:
            name_list = note.xpath('.//text()')
            img_list = note.xpath('.//img/@src')
            names = [n.strip() for n in name_list if n.strip()]

            if names and img_list:
                for name, img in zip(names, img_list):
                    notes_dict[name] = img

        return notes_dict

    def get_notes_urls(self, tree):
        top_xpath = '//*[@id="pyramid"]/div[2]/div[2]/pyramid-switch-new/div/div[1]/pyramid-level-new/div'
        heart_xpath = '//*[@id="pyramid"]/div[2]/div[2]/pyramid-switch-new/div/div[2]/pyramid-level-new/div'
        base_xpath = '//*[@id="pyramid"]/div[2]/div[2]/pyramid-switch-new/div/div[3]/pyramid-level-new/div'

        linear_xpath = '//*[@id="pyramid"]/div[2]/div[2]'

        if tree.xpath(top_xpath):
            return {"top": self.extract_notes_urls(tree, top_xpath),
                    "heart": self.extract_notes_urls(tree, heart_xpath),
                    "base": self.extract_notes_urls(tree, base_xpath)}
        elif tree.xpath(linear_xpath):
            return {"linear": self.extract_notes_urls(tree, linear_xpath)}
        else:
            return {}


    def fetch_page(self, url):
        response = self.scraper.get(url)

        if response.status_code != 200:
            self.scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True})
            response = self.scraper.get(url)

        if response.status_code != 200:
            raise ConnectionError(f"Fragrantica rejected connection. Status code: {response.status_code}")
        
        return response.content
    
    
    def get_data(self, url):
        html_content = self.fetch_page(url)
        tree = html.fromstring(html_content)

        data = {
            "fragrance": self.get_first_or_none(tree, '//*[@id="toptop"]/h1/text()'),
            "gender": self.get_first_or_none(tree, '//*[@id="toptop"]/h1/span/text()'),
            "rating": self.get_first_or_none(tree, '//*[@id="app"]/main/div/div[1]/div[1]/div[4]/div[3]/p/span[1]/text()'),
            "amount_of_rates": self.get_first_or_none(tree, '//*[@id="app"]/main/div/div[1]/div[1]/div[4]/div[3]/p/span[3]/text()'),
            "acords": self.get_acords(tree, '//*[@id="app"]/main/div/div[1]/div[1]/div[2]/div[2]/div/div//span/text()'),
            "notes": self.get_notes_urls(tree),
            "url": url
        }
        return data
    

scraper = FragranticaScraper()
data = scraper.get_data("https://www.fragrantica.pl/perfumy/Viktor-Rolf/Spicebomb-Extreme-30499.html")
print(data)