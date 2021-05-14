import scrapy
import pymongo
from ..loaders import HhLoader


class HhSpider(scrapy.Spider):
    name = 'hh'
    allowed_domains = ['hh.ru']
    start_urls = ['https://krasnoznamensk.hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']

    _xpath_selectors = {'pagination': '//div[@data-qa="pager-block"]//a[@data-qa="pager-page"]/@href',
                        'vacancy': '//div[@data-qa="vacancy-serp__results"]//a[@data-qa="vacancy-serp__vacancy-title"]'
                                   '/@href',
                        'vacancy_author': '//a[@data-qa="vacancy-serp__vacancy-title"]/@href'
                        }
    _xpath_data_selectors = {'title':'//h1[@data-qa="vacancy-title"]/text()',
                             'salary':'//p[@class="vacancy-salary"]/span[@data-qa="bloko-header-2"]/text()',
                             'description':'//div[@data-qa="vacancy-description"]//text()',
                             'req_skills':'//div[@class="bloko-tag-list"]//span[@data-qa="bloko-tag__text"]/text()',
                             'author_url': '//div[contains(@class,"vacancy-company__details")]//a[@data-qa="vacancy-company-name"]/@href'
                             }
    _xpath_author_selectors = {'name':'//span[@data-qa="company-header-title-name"]/text()',
                               'areas': '//div[@class="employer-sidebar-content"]/div[@class="employer-sidebar-block"]'
                                        '/p/text()',
                               'description':'//div[@data-qa="company-description-text"]//text()'
                               }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_client = pymongo.MongoClient()

    def _get_follow(self, response, selector, callback):
        for itm in response.xpath(selector):
            yield response.follow(itm, callback=callback)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(response,self._xpath_selectors['pagination'],self.parse)

        yield from self._get_follow(response, self._xpath_selectors['vacancy'],self.parse_vacancy)


    def parse_vacancy(self, response):
        loader = HhLoader(response=response)
        loader.add_value("url", response.url)
        yield from self._get_follow(response,self._xpath_data_selectors['author_url'],self.parse_author)
        for key, selector in self._xpath_data_selectors.items():
            loader.add_xpath(key,selector)
        yield loader.load_item()

    def parse_author(self, response):
        loader = HhLoader(response=response)
        loader.add_value('url', response.url)
        yield from self._get_follow(response,self._xpath_selectors['vacancy_author'], self.parse_vacancy)
        for key, selector in self._xpath_author_selectors.items():
            loader.add_xpath(key,selector)
        yield loader.load_item()
