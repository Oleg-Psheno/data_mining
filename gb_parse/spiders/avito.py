import scrapy
from ..loaders import AvitoLoader


class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru']
    start_urls = ['https://avito.ru/moskva_i_mo/kvartiry/prodam-ASgBAgICAUSSA8YQ']

    _xpath_selectors = {
        'pagination': '//div[contains(@class,"pagination-pages")]/a[@class="pagination-page"]/@href',
        'advert': '//div[@data-marker="catalog-serp"]/div[@data-marker="item"]//a[@data-marker="item-title"]/@href',
    }
    _xpath_data = {
        'title': '//h1[@class="title-info-title"]/span/text()',
        'price': '//div[@id="price-value"]//span[@itemprop="price"]/text()',
        'address': '//div[@class="item-address"]//span/text()',
        'parameters': '//div[@class="item-params"]//li[@class="item-params-list-item"]',
        'author_url': '//div[@data-marker="seller-info/name"]/a/@href',
        # 'phone':'',
    }

    def _get_follow(self, response, xpath, callback):
        for url in response.xpath(xpath):
            yield response.follow(url, callback=callback)

    def parse(self, response, *args, **kwargs):
        callbacks = {'pagination': self.parse, 'advert': self.parse_advert}
        for key, xpath in self._xpath_selectors.items():
            yield from self._get_follow(response, xpath, callbacks[key])

    def parse_advert(self, response):
        loader = AvitoLoader(response=response)
        loader.add_value('url', response.url)
        for key, xpath in self._xpath_data.items():
            loader.add_xpath(key, xpath)
        yield loader.load_item()
