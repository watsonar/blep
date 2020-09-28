import scrapy


class CatfoodSpider(scrapy.Spider):
    name = 'catfood'
    allowed_domains = ['chewy.com/b/food-387']
    start_urls = ['http://chewy.com/b/food-387/']

    def parse(self, response):
        allProducts = response.css('article.product-holder')

        for product in allProducts:
            link = 'http://chewy.com' + product.css('a::attr(href)').get()
            
            yield scrapy.Request(link, callback=self.parse_product, dont_filter=True)
    
        next_page_partial_url = response.xpath('//a[@class="cw-pagination__next"]/@href').extract_first()
        next_page_url = 'http://chewy.com' + next_page_partial_url
        
        yield scrapy.Request(next_page_url, callback=self.parse, dont_filter=True)


    def parse_product(self, response):
       
        title = response.xpath('//div[@id="product-title"]/h1/text()').extract_first().strip()
        
        multipack_words = ["variety", "collection", "pack"]

        if not any(s in title for s in multipack_words):
            name = title
            
            list_price  = response.xpath('//p[@class=" price"]/text() | //span[@class="list-price"]/text()').extract_first().strip()
            sale_price = response.xpath('//span[@class="ga-eec__price"]/text()').extract_first().strip()
            
            attribute_labels_unstripped = response.xpath('//ul[@class="attributes"]//div[@class="title"]//text()').extract()
            attribute_labels = [item.strip() for item in attribute_labels_unstripped]
           
            attribute_values_unstripped = response.xpath('//ul[@class="attributes"]').css('div.value').xpath('.//text()').extract()
            attribute_values = [item.strip() for item in attribute_values_unstripped]
            attribute_values = list(filter(None, attribute_values))
            attribute_values = [item.replace(",", ";") for item in attribute_values]

            attributes = dict(zip(attribute_labels, attribute_values))

            nutritional_info_labels_unstripped = response.xpath('//article[@id="Nutritional-Info"]//tbody/tr/td[1]/text()').extract()
            nutritional_info_labels = [item.strip() for item in nutritional_info_labels_unstripped]

            nutritional_info_values_unstripped  = response.xpath('//article[@id="Nutritional-Info"]//tbody/tr/td[2]/text()').extract()
            nutritional_info_values = [item.strip() for item in nutritional_info_values_unstripped]
            
            nutritional_info = dict(zip(nutritional_info_labels, nutritional_info_values))

            ingredients = response.xpath('//section[@class="cw-tabs__content--left"]/p/text()')[0].extract().strip()

            caloric_content = response.xpath('//section[@class="cw-tabs__content--left"]/p/text()')[1].extract().strip()

            yield {
                'name': name,
                'list_price': list_price,
                'sale_price': sale_price,
                'attributes': attributes,
                'nutritional_info': nutritional_info,
                'ingredients': ingredients,
                'caloric_content': caloric_content,
            }

            print(response.status)
