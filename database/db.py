from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from . import models


class Database:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        models.Base.metadata.create_all(bind=self.engine)
        self.maker = sessionmaker(bind=self.engine)

    def add_post(self, data):
        session = self.maker()
        self._add_post(data['post_data'], data['author_data'], session)
        [self._add_tag(tag, session) for tag in data['tags_data'] if data['tags_data']]
        try:
            session.commit()

        except IntegrityError as e:
            session.rollback()
            print(e)
            print('не сохранили запись')
        else:
            print('Запись сохранена')
        finally:
            session.close()

    def _add_tag(self, tag, session):
        if not session.query(models.Tag).filter_by(name=tag['name']).first():
            session.add(models.Tag(**tag))

    def _add_post(self, post, author, session):
        if not session.query(models.Post).filter_by(id=post['id']).first():
            author = self._add_author(session, author)
            session.add(models.Post(**post, author = author))


    def _add_author(self,session,author):
        if not session.query(models.Author).filter_by(name=author['name']).first():
            return models.Author(**author)
        else:
            return session.query(models.Author).filter_by(name=author['name']).first()
