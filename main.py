from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_parse.spiders.autoyola import AutoyoulaSpider
from gb_parse.spiders.hh import HhSpider
from gb_parse.spiders.avito import AvitoSpider
from gb_parse.spiders.instagram import InstagramSpider
import dotenv
import os


if __name__ == "__main__":
    dotenv.load_dotenv('.env')
    crawler_settings = Settings()
    crawler_settings.setmodule("gb_parse.settings")
    crawler_process = CrawlerProcess(settings=crawler_settings)
    # crawler_process.crawl(HhSpider)
    # crawler_process.crawl(AutoyoulaSpider)
    # crawler_process.crawl(AvitoSpider)
    tags = ['js','moscow']
    crawler_process.crawl(InstagramSpider, login=os.getenv('INST_LOG'), password=os.getenv('INST_PSW'), tags=tags)

    crawler_process.start()