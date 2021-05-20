import scrapy
import json
from ..loaders import InstaLoader
from datetime import datetime


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    _login_url = 'https://www.instagram.com/accounts/login/ajax/'
    _tag_path = '/explore/tags/'
    api_url = 'https://i.instagram.com/api/v1/tags/'

    def __init__(self, login, password, tags, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login = login
        self.password = password
        self.tags = tags

    def parse(self, response, *args, **kwargs):
        try:
            js_data = self.get_js_data(response)
            yield scrapy.FormRequest(
                self._login_url,
                method='POST',
                callback=self.parse,
                formdata={'username': self.login, 'enc_password': self.password},
                headers={'X-CSRFToken': js_data['config']['csrf_token']}
            )
        except AttributeError as e:
            print(e)
            data = response.json()
            if data['authenticated']:
                print('User is authenticated')
                for tag in self.tags:
                    yield response.follow(f'{self._tag_path}{tag}/', callback=self.tag_page_parse)

    def tag_page_parse(self, response):
        data = self.get_js_data(response)
        sections = data['entry_data']['TagPage'][0]['data']['recent']['sections']
        for section in sections:
            block = section['layout_content']['medias']
            for post in block:
                yield from self.post_parse(post)
        try:
            next_data = {
                'url':'https://i.instagram.com/api/v1/tags/summer/sections/',
                'max_id': data['entry_data']['TagPage'][0]['data']['recent']['next_max_id']

            }
            yield scrapy.FormRequest(
                next_data['url'],
                method='POST',
                callback=self.tag_page_parse,
                formdata={'max_id': next_data['max_id'],},
                headers={'X-CSRFToken': data['config']['csrf_token']}
            )
        except Exception as e:
            print('fail')
        else:
            print(1)

    def post_parse(self, data):
        loader = InstaLoader(item=data)
        loader.add_value('time',datetime.now())
        for k,v in data.items():
            loader.add_value(k,v)
        yield loader.load_item()



    def get_js_data(self, response):
        data = response.xpath('//script[contains(text(),"window._sharedData =")]'
                              '/text()').extract_first().replace('window._sharedData = ', '')[:-1]
        return json.loads(data)
