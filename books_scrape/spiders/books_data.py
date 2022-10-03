import scrapy
import re


class BooksSpider(scrapy.Spider):

    name = 'books_extraction'
    start_urls = ['https://books.toscrape.com']

    def parse(self, response, **kwargs):
        list_of_books = response.css('ol.row li a::attr(href)').getall()
        yield from response.follow_all(list_of_books, callback=self.items)

        next_page_url = response.css('li.next a::attr(href)').get()
        if next_page_url:
            yield response.follow(next_page_url, callback=self.parse)

    def categories(self, response):
        category = response.css('ul.breadcrumb li a::text').getall()
        category = category[1:]
        category = ' > '.join(category)
        return category

    def number_of_available_products(self, response):
        product_info = response.xpath('//i[@class="icon-ok"]/following-sibling::text()').get()
        product_info = re.findall(r'\d+', product_info)
        return product_info[0]

    def stock_availability (self, response):
        availability_stock = response.xpath('//i[@class="icon-ok"]/following-sibling::text()').get()
        availability_stock = re.findall(r'\b[A-z]{2}\s[a-z]{5}\b', availability_stock)
        return availability_stock

    def fetch_product_info(self, response):
        product_info = {}
        for info in response.css(".table-striped tr"):
            product_info_heading = info.css("th::text").get()
            product_info_value = info.css("td::text").get()
            product_info[product_info_heading] = product_info_value
        return product_info

    def items(self, response):
        yield {
                'category': self.categories(response),
                'name': response.css('div.product_main h1::text').get().strip('#').strip('"'),
                'price': response.css('p.price_color::text').get().replace('£', ''),
                'number_of_available_products': self.number_of_available_products(response),
                'in_stock': bool(self.stock_availability(response)),
                'description': response.css('#product_description + p::text').get(),
                'production_information': self.fetch_product_info(response),
                'url': response.url
            }
