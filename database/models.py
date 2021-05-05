from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, BigInteger, Table

Base = declarative_base()

tag_post = Table(
    'tag_post',
    Base.metadata,
    Column('post_id', BigInteger, ForeignKey('post.id')),
    Column('tag_id', BigInteger, ForeignKey('tag.id')),
)


class IdMixin:
    id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True)


class UrlMixin:
    url = Column(String, nullable=False, unique=True)


class Post(Base, UrlMixin):
    __tablename__ = 'post'
    id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True)
    title = Column(String(250), nullable=False, unique=False)
    author_id = Column(BigInteger, ForeignKey('author.id'))
    author = relationship('Author', backref='posts')
    tags = relationship('Tag', secondary=tag_post, backref='posts')


class Author(Base, UrlMixin):
    __tablename__ = 'author'
    id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String(150), nullable=False, unique=True)


class Tag(Base, UrlMixin):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
