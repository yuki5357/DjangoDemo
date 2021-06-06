# -*- coding:utf-8 -*-
from django.views import View
from django.http import HttpResponse
from django.db import DatabaseError, IntegrityError, transaction

import json
import logging
from datetime import datetime

from .models import Author, Book


# Create your views here.

logger = logging.getLogger('app')


class Record(View):
    @staticmethod
    def check_year(year):
        if year and int(year) > datetime.now().year:
            return True
        return False


    @staticmethod
    def check_author(author):
        if author.get('name', '') and Author.objects.filter(name=author['name']):
            return True
        return False


    def post(self, request):
        bookinfo = json.loads(request.body)
        title = bookinfo.get('title', '')
        authors = bookinfo.get('authors', '')
        year = bookinfo.get('year', '')

        if not title or not authors:
            return HttpResponse(json.dumps({'code': 400, 'message': 'Book title or authors are missing.'}),
                                    content_type='application/json')

        if self.check_year(year):
            return HttpResponse(json.dumps({'code': 400, 'message': 'Incorrect year.'}),
                                    content_type='application/json')

        try:
            with transaction.atomic():  # 写入失败则回滚
                book = Book.objects.create(title=title, year=year)
                for author in authors:
                    if not self.check_author(author):
                        continue
                    cur_author = Author.objects.create(name=author['name'], email=author.get('email', ''))
                    book.authors.add(cur_author)
                    cur_author.save()
                book.save()
                # raise DatabaseError
        except DatabaseError:
            logger.error('An error occurred while recording book info.')
            return HttpResponse(json.dumps({'code': 400, 'message': 'Failed in recording book info.'}),
                                    content_type='application/json')

        logger.info('Succeeded in recording book info.')
        return HttpResponse(json.dumps({'code': 200, 'message': 'OK.'}), content_type='application/json')


class Search(View):
    def post(self, request):
        search_params = json.loads(request.body)
        title = search_params.get('title', '')

        if not title:
            return HttpResponse(json.dumps({'code': 400, 'message': 'Book title is missing.'}),
                                content_type='application/json')

        bookinfo = Book.objects.filter(title=title).first()
        if not bookinfo:
            return HttpResponse(json.dumps({'code': 400, 'message': 'Not found book titled <{}>.'.format(title)}),
                                content_type='application/json')

        if authors := bookinfo.authors.all():
            author_list = list()
            for author in authors:
                author_list.append(author.name)

        result = {
            'title': bookinfo.title,
            'authors': author_list,
            'year': bookinfo.year
        }
        return HttpResponse(json.dumps({'code': 200, 'message': 'OK.', 'bookinfo': result}), content_type='application/json')