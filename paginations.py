import urllib
from copy import deepcopy

from flask import jsonify, request

from settings import PAGE_LIMIT


class BasePagination():
    """ Base class to generate pagination response for list API
    """

    def __init__(self, queryset, schema):
        """
        Parameter
        ---------
        `queryset`: <sql_queryset>
            Sql query

        `schema`: <pagination_schema>
            Queryset result pagination response

        `limit`: <int>
            Limit of record display per page

        `page`: <int>
            Current page number

        `count`: <int>
            Total record count
        """
        self.next = ''
        self.previous = ''
        self.queryset = queryset
        self.schema = schema
        self.url_parameter = dict(request.args)
        self.limit = int(request.args.get('limit', PAGE_LIMIT))
        self.page = int(request.args.get('page', 1))
        self.total = queryset.count()

    def get_paginated_queryset(self):
        """ Return paginated queryset """
        queryset = self.queryset
        page = self.page - 1
        return queryset.limit(self.limit).offset(page*self.limit)

    def next_url(self):
        """ Generate next page url from limit, page and request path value """
        if not self.total:
            return ''

        if self.total <= (self.page * self.limit):
            return ''

        url_parameter = deepcopy(self.url_parameter)
        url_parameter['limit'] = self.url_parameter.get(
            'limit', self.limit)
        url_parameter['page'] = int(
            self.url_parameter.get('page', self.page)) + 1
        url_parameter = urllib.parse.urlencode(url_parameter)
        return f'{request.base_url}{url_parameter}'

    def previous_url(self):
        """ Generate previous page url from limit, page and request path value """
        if not self.total:
            return ''

        if not self.page > 1:
            return ''

        url_parameter = deepcopy(self.url_parameter)
        url_parameter['limit'] = self.url_parameter.get(
            'limit', self.limit)
        url_parameter['page'] = int(self.url_parameter.get(
            'page', self.page)) - 1
        url_parameter = urllib.parse.urlencode(url_parameter)
        return f'{request.base_url}{url_parameter}'

    def response(self):
        """ Generate pagination format """
        return jsonify({
            'next': self.next_url(),
            'previous': self.previous_url(),
            'count': self.total,
            'results': self.schema(many=True).dump(
                self.get_paginated_queryset())[0]
        })


class IndexPagination(BasePagination):
    """ Pagination class to generation pagination response for index API """

    def response(self):
        """ """
        return jsonify({
            'next': self.next_url(),
            'previous': self.previous_url(),
            'count': self.total,
            'results': self.schema(many=True).dump(
                self.get_paginated_queryset())[0]
        })
