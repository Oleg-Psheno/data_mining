import pymongo
import scrapy
from ..loaders import AutoyoulaLoader


class AutoyoulaSpider(scrapy.Spider):
    name = "autoyoula"
    allowed_domains = ["auto.youla.ru"]
    start_urls = ["https://auto.youla.ru/"]

    _xpath_selectors = {
        "brands": '//div[@data-target="transport-main-filters"]'
        '//div[contains(@class,"ColumnItemList_column")]'
        '//a[@data-target="brand"]/@href',
        "pagination": '//div[contains(@class, "Paginator_block")]'
        '//a[@data-target-id="button-link-serp-paginator"]/@href',
        "car": '//article[@data-target="serp-snippet"]'
        '//a[@data-target="serp-snippet-title"]/@href',
    }
    _xpath_data_selectors = {
        "title": "//div[@data-target='advert-title']/text()",
        "price": "//div[@data-target='advert-price']/text()",
        "photos": "//div[contains(@class, 'PhotoGallery_block')]//figure/picture/img/@src",
        "characteristics": "//div[contains(@class, 'AdvertCard_specs')]"
        "/div/div[contains(@class, 'AdvertSpecs_row')]",
        "description": "//div[@data-target='advert-info-descriptionFull']/text()",
        "author": '//body/script[contains(text(), "window.transitState = decodeURIComponent")]',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_client = pymongo.MongoClient()

    def _get_follow(self, response, selector_str, callback):
        for itm in response.xpath(selector_str):
            yield response.follow(itm, callback=callback)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(
            response, self._xpath_selectors["brands"], self.brand_parse,
        )

    def brand_parse(self, response):
        yield from self._get_follow(
            response, self._xpath_selectors["pagination"], self.brand_parse
        )
        yield from self._get_follow(
            response, self._xpath_selectors["car"], self.car_parse,
        )

    def car_parse(self, response):
        loader = AutoyoulaLoader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in self._xpath_data_selectors.items():
            loader.add_xpath(key, xpath)
        yield loader.load_item()