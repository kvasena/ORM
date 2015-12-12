from entity import *


class Section(Entity):
    _columns  = ['title']
    _parents  = []
    _children = {'categories': 'Category'}
    _siblings = {}


class Category(Entity):
    _columns  = ['title']
    _parents  = ['section']
    _children = {'posts': 'Post'}
    _siblings = {}


class Article(Entity):
    _columns  = ['text', 'title']
    # _parents  = ['category']
    _children = {'comments': 'Comment'}
    _siblings = {'tags': 'Tag'}


class Comment(Entity):
    _columns  = ['text']
    _parents  = ['post', 'user']
    _children = {}
    _siblings = {}


class Tag(Entity):
    _columns  = ['name']
    _parents  = []
    _children = {}
    _siblings = {'posts': 'Post'}


class User(Entity):
    _columns  = ['name', 'email', 'age']
    _parents  = []
    _children = {'comments': 'Comment'}
    _siblings = {}


if __name__ == "__main__":
    db = psycopg2.connect(database='shop', user='shop', password='shop', host="127.0.0.1", port="5432")
    Entity.db = db

    # article = Article(14)
    # article.text = "ira"
    # article.save()
    # print article.text

    category = Category()
    category.title = "fhfjg"
    category.save()
    # print category.title
    # category1 = Category()
    # category1._set_column('title', '123456')
    # print category1._get_column('title')
    # category1.save()

    # print category.id
    # print category.created
    # print category.updated
    for i in Category.all():
        print i.title
    # a = Article(12)
    # print a.title
    # print a.category.title
    # for article in a.category.articles:
    #     print article.category.title

