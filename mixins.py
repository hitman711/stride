""" """
from flask import (Flask, request)

from settings import PAGE_LIMIT


class MultipleFieldLookUpMixin():
    """ View mixins to perform filter operation on model for
    retrieve data based on filter fileds
    """

    def filter_queryset(self):
        """ Return queryset with filter object """
        queryset = self.queryset
        try:
            model_fields = self.filter_fields
            query_param = {
                x: request.args.get(x)
                if request.args.get(x) else '' for x in list(
                    model_fields.keys())}
            for field in query_param:
                if query_param[field]:
                    column = getattr(*model_fields[field])
                    queryset = queryset.filter(
                        column.ilike(f"%{query_param[field]}%"))
        except Exception as AttributeError:
            pass
        return queryset

    def get_queryset(self):
        """ Generate basic queryset based on URL view """
        return self.filter_queryset()

    def get_object(self):
        """ Fetch individual object """
        return self.get_queryset().first()

    def pagination_response(self):
        """ Get paginated reponse """
        return self.pagination_format(
            self.get_queryset(),
            self.serializer_class).response()
