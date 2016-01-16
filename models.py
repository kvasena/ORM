from entity import *


class Section(Entity):
    _columns  = ['title']
    _parents  = []
    _children = {'categories': 'Category'}
    _siblings = {}


class Category(Entity):
    _columns  = ['title']
    _parents  = ['section']
    _children = {'articles': 'Article'}
    _siblings = {}


class Article(Entity):
    _columns  = ['text', 'title']
    _parents  = ['category']
    _children = {'comments': 'Comment'}
    _siblings = {'tags': 'Tag'}


class Comment(Entity):
    _columns  = ['text']
    _parents  = ['article', 'user']
    _children = {}
    _siblings = {}


class Tag(Entity):
    _columns  = ['name']
    _parents  = []
    _children = {}
    _siblings = {'articles': 'Article'}


class User(Entity):
    _columns  = ['name', 'email', 'age']
    _parents  = []
    _children = {'comments': 'Comment'}
    _siblings = {}


if __name__ == "__main__":
    db = psycopg2.connect(database='shop', user='shop', password='shop', host="127.0.0.1", port="5432")
    Entity.db = db
    category = Category(61)
    article = Article(3)
    c = article.category
    print c.title
    c.title = 'zalupa2 ERSTG'
    c.save()
    print c.title
    # article._set_parent('category', 61)
    # article.save()
    # print article.category.title
    # article.category.title = 'zalupa'
    # article.category.save()
    # category = Category(61)
    # print category.title

