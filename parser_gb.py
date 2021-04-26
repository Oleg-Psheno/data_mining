import bs4
import requests
from pymongo import MongoClient
from urllib.parse import urljoin
import time
import datetime


class ParserGB:

    def __init__(self, start_url, connection):
        self.start_url = start_url
        self.connection = connection
        self.done_url = set()
        self.tasks = []
        start_task = self._get_task(start_url, self._parse_feed)
        self.tasks.append(start_task)
        self.done_url.add(start_url)
        self.time = time.time()

    def _get_response(self, url, *args, **kwargs):
        responce = requests.get(url, *args, **kwargs)
        if self.time + 0.5 < time.time():
            time.sleep(0.5)
        self.time = time.time()
        print(url)
        return responce

    def _get_soup(self, url):
        html = self._get_response(url).text
        soup = bs4.BeautifulSoup(html, 'lxml')
        return soup

    def _get_task(self, url, callback):
        def task():
            soup = self._get_soup(url)
            return callback(url, soup)

        if url in self.done_url:
            return lambda *_, **__: None
        self.done_url.add(url)
        return task

    def _task_creator(self, url, tags, callback):
        links = set([urljoin(url, el.attrs.get('href')) for el in tags if el.attrs.get('href')])
        for link in links:
            task = self._get_task(link, callback)
            self.tasks.append(task)

    def _parse_feed(self, url, soup):
        pagination = soup.find('ul', attrs={'class': 'gb__pagination'})
        self._task_creator(url, pagination.find_all('a'), self._parse_feed)
        posts = soup.find('div', attrs={'class': 'post-items-wrapper'})
        self._task_creator(url, posts.find_all('a', attrs={'class': 'post-item__title'}), self._parse_post)

    def _parse_post(self, url, soup):
        article = soup.find('article', attrs={'class': 'blogpost__article-wrapper'})
        title = article.find('h1').text
        description = article.find('div', attrs={'class': 'blogpost-description'}).text
        raw_time = list(article.find('div', attrs={'class': 'blogpost-date-views'}).children)[0].get('datetime')
        time = datetime.datetime.strptime(raw_time,'%Y-%m-%dT%H:%M:%S+03:00')
        content = article.find('div', attrs={'class': 'blogpost-content'})
        image = content.find('img').get('src')
        text = content.text
        author = {'name': soup.find('div', attrs={'itemprop': 'author'}).text,
                  'link': urljoin('https://gb.ru/',
                                  soup.find('div', attrs={'itemprop': 'author'}).parent.attrs.get('href'))
                  }
        comments = self.get_comments(soup)
        data = {'url': url, 'title': title, 'description': description,
                'time': time, 'image': image, 'text': text, 'author': author,
                'comments': comments
                }
        return data

    def get_comments(self, soup):
        id = soup.find('div', attrs={'class': 'referrals-social-buttons-small-wrapper'}).attrs.get('data-minifiable-id')
        url = f'https://gb.ru/api/v2/comments?commentable_type=Post&commentable_id={id}&order=desc'
        responce = self._get_response(url).json()
        comments = []
        for comment in responce:
            comments.append(self.parse_comment(comment))

        return comments

    def parse_comment(self, comment):
        author = comment.get('comment').get('user').get('full_name')
        text = comment.get('comment').get('body')
        include = comment.get('comment').get('children')
        if include:
            for child in include:
                include = self.parse_comment(child)

        return {'author': author, 'text': text, 'include': include}

    def run(self):
        for task in self.tasks:
            result = task()
            if isinstance(result, dict):
                self.save(result)
                print('сохранили статью')

    def save(self, data):
        self.connection.insert_one(data)


if __name__ == '__main__':
    url = 'https://gb.ru/posts'
    connection = MongoClient()['parserGB']['parse_data']
    parser = ParserGB(url, connection)
    parser.run()
