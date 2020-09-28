import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.loader import ItemLoader
from Chewy.items import ChewyItem


class ChewySpider(scrapy.Spider):
    name = 'chewy_spider'
    allowed_domains = ['chewy.com']
    start_urls = ['https://www.chewy.com/b/food-387']
    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'raw_chewy_spider.csv'
    }
    PACK_WORDS = ['variety', 'collection', 'pack']
    TREAT_WORDS = ['treat', 'topping, topper, complement, mixer']

    def parse(self, response):
        product_pages = [i.strip() for i in response.css('article.product-holder a::attr(href)').getall()]
        yield from response.follow_all(product_pages, callback = self.parse_product)

        next_page = response.css('a.cw-pagination__next::attr(href)').get().strip()
        yield response.follow(next_page, self.parse)

    def parse_product(self, response):
        name = response.css('div#product-title h1::text').get() #.strip()
        attr = response.css('ul.attributes ::text').getall()

        if any(word in name.lower() for word in (ChewySpider.PACK_WORDS + ChewySpider.TREAT_WORDS)) \
        or any(word in str(attr).lower() for word in ChewySpider.TREAT_WORDS):
            return
        else:
            l = ItemLoader(item=ChewyItem(), response=response)
            l.add_value('name', name)
            l.add_value('url', response.request.url)
            l.add_css('our_price', 'li.our-price span.ga-eec__price ::text')
            l.add_css('list_price', 'li.list-price p.price ::text')
            l.add_css('calories', 'span.Caloric + p::text')
            l.add_css('ingredients', 'span.Ingredients-title + p::text')
            l.add_value('attr_dict', {row.css('div.title ::text').get() : ''.join(str(i) for i in row.css('div.value ::text').getall())
                                      for row in response.css('ul.attributes li')})
            l.add_value('ga_dict', {row.xpath('td[1]//text()').get() : row.xpath('td[2]//text()').get()
                                    for row in response.css('article#Nutritional-Info table:nth-of-type(1) tbody tr')})
            yield l.load_item()


# process = CrawlerProcess()
# process.crawl(ChewySpider)
# process.start()
