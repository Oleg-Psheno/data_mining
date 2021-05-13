import scrapy
import pymongo
import re


class AutoyolaSpider(scrapy.Spider):
    name = 'autoyola'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']
    data_query = {
        "title": lambda resp: resp.css("div.AdvertCard_advertTitle__1S1Ak::text").get(),
        "price": lambda resp: float(
            resp.css("div.AdvertCard_price__3dDCr::text").get().replace("\u2009", "")
        ),
        "photos": lambda resp: [
            itm.attrib.get("src") for itm in resp.css("figure.PhotoGallery_photo__36e_r img")
        ],
        "characteristics": lambda resp: [
            {
                "name": itm.css(".AdvertSpecs_label__2JHnS::text").extract_first(),
                "value": itm.css(".AdvertSpecs_data__xK2Qx::text").extract_first()
                or itm.css(".AdvertSpecs_data__xK2Qx a::text").extract_first(),
            }
            for itm in resp.css("div.AdvertCard_specs__2FEHc .AdvertSpecs_row__ljPcX")
        ],
        "descriptions": lambda resp: resp.css(
            ".AdvertCard_descriptionInner__KnuRi::text"
        ).extract_first(),
        "author": lambda resp: AutoyolaSpider.get_author_id(resp),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_client = pymongo.MongoClient()


    def _get_follow(self, response, selector_str, callback):
        for itm in response.css(selector_str):
            url = itm.attrib["href"]
            yield response.follow(url, callback=callback)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow(
            response,
            ".TransportMainFilters_brandsList__2tIkv .ColumnItemList_column__5gjdt a.blackLink",
            self.brand_parse,
        )

    def brand_parse(self, response):
        yield from self._get_follow(
            response, ".Paginator_block__2XAPy a.Paginator_button__u1e7D", self.brand_parse
        )
        yield from self._get_follow(
            response,
            "article.SerpSnippet_snippet__3O1t2 a.SerpSnippet_name__3F7Yu.blackLink",
            self.car_parse,
        )

    def car_parse(self, response):
        data = {}
        for key, selector in self.data_query.items():
            try:
                data[key] = selector(response)
            except (ValueError, AttributeError):
                continue
        self.db_client["gb_parse_20_04_2021"][self.name].insert_one(data)

    @staticmethod
    def get_author_id(resp):
        marker = "window.transitState = decodeURIComponent"
        for script in resp.css("script"):
            try:
                if marker in script.css("::text").extract_first():
                    re_pattern = re.compile(r"youlaId%22%2C%22([a-zA-Z|\d]+)%22%2C%22avatar")
                    result = re.findall(re_pattern, script.css("::text").extract_first())
                    return (
                        resp.urljoin(f"/user/{result[0]}").replace("auto.", "", 1)
                        if result
                        else None
                    )
            except TypeError:
                pass

