""" """
from flask import (Flask, request)

class MultipleFieldLookUpMixin():
    """ """
    limit = 20
    page = 1

    def get_paginated_queryset(self):

        queryset = self.get_queryset()
        limit = int(request.args.get('limit', self.limit))
        page = int(request.args.get('page', self.page)) - 1

        return queryset.limit(limit).offset(page*limit)

    def filter_queryset(self):
        queryset = self.queryset
        try:
            filter = {}
            model_fields = self.filter_fields
            
            query_param = {
                x: request.args.get(x).split(',') \
                    if request.args.get(x) else '' for x in list(
                        model_fields.keys()
                    )
                }
            for field in query_param:
                if query_param[field]:
                    column = getattr(*model_fields[field])
                    queryset = queryset.filter(column.in_(query_param[field]))
        except Exception as e:
            pass
        return queryset

    def get_queryset(self):
        return self.filter_queryset()

    def get_object(self):
        return self.filter_queryset().first()
