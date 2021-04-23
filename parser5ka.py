import requests
import json
from pathlib import Path
import time


class Parser:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) Gecko/20100101 Firefox/88.0"
    }
    params = {
        "records_per_page": 20
    }

    def __init__(self, start_url: str, save_path: Path):
        self.start_url = start_url
        self.save_path = save_path

    def _get_response(self, url, *args, **kwargs):
        while True:
            response = requests.get(url, *args, **kwargs)
            if response.status_code == 200:
                print(f'переходим по странице {url}')
                return response
            time.sleep(3)
            print('Ожидаем')

    def _parse(self, url: str):
        while url:
            time.sleep(0.05)
            response = self._get_response(url, headers=self.headers, params=self.params)
            data = response.json()
            url = data['next']
            if url:
                url = url.replace('monolith', '5ka.ru')
            for product in data['results']:
                yield product

    def start(self):
        for product in self._parse(self.start_url):
            file_path = self.save_path.joinpath(f'{product["id"]}.json')
            self._save(product, file_path)

    def _save(self, data: dict, file_path):
        file_path.write_text(json.dumps(data, ensure_ascii=False))


def get_save_path(dir_name):
    save_path = Path(__file__).parent.joinpath(dir_name)
    if not save_path.exists():
        save_path.mkdir()
    return save_path


class ParserWithCategories(Parser):
    categories_url = 'https://5ka.ru/api/v2/categories/'

    def _get_categories(self):
        responce = self._get_response(self.categories_url)
        self.categories = responce.json()

    def run(self):
        self._get_categories()
        for category in self.categories:
            self.params['categories'] = int(category['parent_group_code'])
            products = []
            for product in self._parse(self.start_url):
                products.append(product)
            data = {'name': category['parent_group_name'],
                    'code': category['parent_group_code'],
                    'products': products}
            file_path = self.save_path.joinpath(f'{category["parent_group_name"]}.json')
            self._save(data, file_path)


if __name__ == '__main__':
    url = "http://5ka.ru/api/v2/special_offers/"
    save_path = get_save_path('products')
    # parser = Parser(url, save_path)
    # parser.start()
    parser2 = ParserWithCategories(url, save_path)
    parser2.run()
