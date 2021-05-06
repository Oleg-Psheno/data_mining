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
        comments = self._add_comment(data['comment_data'], session, id_post=data['post_data']['id'])
        for comment in comments:
            session.add(comment)
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
            session.add(models.Post(**post, author=author))

    def _add_author(self, session, author):
        if not session.query(models.Author).filter_by(name=author['name']).first():
            return models.Author(**author)
        else:
            return session.query(models.Author).filter_by(name=author['name']).first()

    def _add_comment(self, data, session, id_post):
        comment_list = []
        if isinstance(data,list):
            for comment in data:
                author = self._add_user(comment['author'], session)
                if comment['include']:
                    self._add_comment(comment['include'],session,id_post)
                comment_inst = models.Comment(author=author, text=comment['text'], post_id=id_post)
                comment_list.append(comment_inst)
        else:
            author = self._add_user(data['author'], session)
            if data['include']:
                self._add_comment(data['include'], session, id_post)
            comment_inst = models.Comment(author=author, text=data['text'], post_id=id_post)
            comment_list.append(comment_inst)
        return comment_list


    def _add_user(self, user, session):
        instance = session.query(models.User).filter_by(name=user).first()
        if not instance:
            instance = models.User(name=user)
        return instance
