from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose

def get_salary_info(str):
    pass


class HhLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_out = TakeFirst()
    salary_out = MapCompose(get_salary_info)
    author_url_out = TakeFirst()





