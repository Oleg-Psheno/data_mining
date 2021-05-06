from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Table

Base = declarative_base()

tag_post = Table(
    'tag_post',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('post.id')),
    Column('tag_id', Integer, ForeignKey('tag.id')),
)


class IdMixin:
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)


class UrlMixin:
    url = Column(String, nullable=False, unique=True)


class Post(Base, UrlMixin):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    title = Column(String(250), nullable=False, unique=False)
    author_id = Column(Integer, ForeignKey('author.id'))
    author = relationship('Author', backref='posts')
    tags = relationship('Tag', secondary=tag_post, backref='posts')


class Author(Base, UrlMixin):
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String(150), nullable=False, unique=True)


class Tag(Base, UrlMixin):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)


class Comment(Base):
    __tablename__ = 'comment'
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String, nullable=True)
    author_id = Column(Integer, ForeignKey('user.id'))
    author = relationship('User', backref='comments')
    post_id = Column(Integer, ForeignKey('post.id'))


class User(Base):
    # Создаем таблицу авторов комментов
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)


