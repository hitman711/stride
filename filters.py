"""
Provides generic filtering backends that can be used to filter the results
returned by list views.
"""
from __future__ import unicode_literals

import operator
import warnings
from functools import reduce

import re
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models.constants import LOOKUP_SEP
from django.db.models.sql.constants import ORDER_PATTERN
from django.template import loader
from django.utils import six
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _


class SearchFilter():
    # The URL query parameter used for the search.
    search_param = api_settings.SEARCH_PARAM
    template = 'rest_framework/filters/search.html'
    lookup_prefixes = {
        '^': 'istartswith',
        '=': 'iexact',
        '@': 'search',
        '$': 'iregex',
    }
    search_title = _('Search')
    search_description = _('A search term.')

    def get_search_terms(self, request):
        """
        Search terms are set by a ?search=... query parameter,
        and may be comma and/or whitespace delimited.
        """
        params = request.query_params.get(self.search_param, '')
        if not params:
            return params
        else:
            params = re.split(r',|"(.*?)"', params)
            params = [x.strip() for x in params if x]
        return params

    def construct_search(self, field_name):
        lookup = self.lookup_prefixes.get(field_name[0])
        if lookup:
            field_name = field_name[1:]
        else:
            lookup = 'icontains'
        return LOOKUP_SEP.join([field_name, lookup])

    def must_call_distinct(self, queryset, search_fields):
        """
        Return True if 'distinct()' should be used to query the given lookups.
        """
        for search_field in search_fields:
            opts = queryset.model._meta
            if search_field[0] in self.lookup_prefixes:
                search_field = search_field[1:]
            parts = search_field.split(LOOKUP_SEP)
            for part in parts:
                field = opts.get_field(part)
                if hasattr(field, 'get_path_info'):
                    # This field is a relation, update opts to follow the relation
                    path_info = field.get_path_info()
                    opts = path_info[-1].to_opts
                    if any(path.m2m for path in path_info):
                        # This field is a m2m relation so we know we need to call distinct
                        return True
        return False

    def filter_queryset(self, request, queryset, view):
        search_fields = getattr(view, 'search_fields', None)
        search_terms = self.get_search_terms(request)

        if not search_fields or not search_terms:
            return queryset

        orm_lookups = [
            self.construct_search(six.text_type(search_field))
            for search_field in search_fields
        ]

        base = queryset
        conditions = []

        for search_term in search_terms:
            queries = [
                models.Q(**{orm_lookup: search_term})
                for orm_lookup in orm_lookups
            ]
            conditions.append(reduce(operator.or_, queries))
        # queryset = queryset.filter(reduce(operator.or_, conditions))
        queryset = queryset.filter(reduce(operator.and_, conditions))

        if self.must_call_distinct(queryset, search_fields):
            # Filtering against a many-to-many field requires us to
            # call queryset.distinct() in order to avoid duplicate items
            # in the resulting queryset.
            # We try to avoid this if possible, for performance reasons.
            queryset = distinct(queryset, base)
        return queryset

    def to_html(self, request, queryset, view):
        if not getattr(view, 'search_fields', None):
            return ''

        term = self.get_search_terms(request)
        term = term[0] if term else ''
        context = {
            'param': self.search_param,
            'term': term
        }
        template = loader.get_template(self.template)
        return template.render(context)
