from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose
import re
from scrapy import Selector
from urllib.parse import urljoin


def get_salary_info(str):
    pass
def clear_price(price):
    try:
        result = float(price.replace("\u2009", ""))
    except ValueError:
        result = None
    return result


def get_characteristics(item: str) -> dict:
    selector = Selector(text=item)
    data = {}
    data["name"] = selector.xpath(
        "//div[contains(@class, 'AdvertSpecs_label')]/text()"
    ).extract_first()
    data["value"] = selector.xpath(
        "//div[contains(@class, 'AdvertSpecs_data')]//text()"
    ).extract_first()
    return data


def get_author_id(text):
    re_pattern = re.compile(r"youlaId%22%2C%22([a-zA-Z|\d]+)%22%2C%22avatar")
    result = re.findall(re_pattern, text)
    try:
        user_link = f"https://youla.ru/user/{result[0]}"
    except IndexError:
        user_link = None
        pass
    return user_link

class AutoyoulaLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_out = TakeFirst()
    price_in = MapCompose(clear_price)
    price_out = TakeFirst()
    description_out = TakeFirst()
    characteristics_in = MapCompose(get_characteristics)
    author_in = MapCompose(get_author_id)
    author_out = TakeFirst()

class HhLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_out = TakeFirst()
    salary_out = MapCompose(get_salary_info)
    author_url_out = TakeFirst()





