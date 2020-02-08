__author__ = 'anuj'

from rest_framework.pagination import BasePagination, PageNumberPagination
from rest_framework.response import Response
from django.template import loader
from rest_framework.compat import template_render
from collections import OrderedDict


class PageNumberPaginationDataOnly(BasePagination):
    # Set any other options you want here like page_size
    template = 'rest_framework/pagination/numbers.html'

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', None),
            ('next', None),
            ('previous', None),
            ('results', data)
        ]))

    def paginate_queryset(self, queryset, request, view=None):
        self.request = request
        return list(queryset)

    def to_html(self):
        template = loader.get_template(self.template)
        context = self.get_html_context()
        return template_render(template, context)

    def get_html_context(self):
        base_url = self.request.build_absolute_uri()

        return {
            'previous_url': None,
            'next_url': None,
            'page_links': None
        }


class PaginationWithCreditSum(PageNumberPagination):
    def paginate_queryset(self, queryset, request, view=None):
        from django.db.models import Sum, Case, When, DecimalField
        from core.models.users import CreditTransaction
        credit_sums = queryset.aggregate(total_earned_credits=Sum(
                                             Case(When(trans_type=CreditTransaction.TRANSACTION_TYPE_CREDIT,
                                                      then='amount'),
                                                  output_field=DecimalField())),
                                         total_used_credits=Sum(
                                             Case(When(trans_type=CreditTransaction.TRANSACTION_TYPE_DEBIT,
                                                       then='amount'),
                                                  output_field=DecimalField())))
        self.total_earned_credits = credit_sums['total_earned_credits']
        self.total_used_credits = credit_sums['total_used_credits']
        return super(PaginationWithCreditSum, self).paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        paginated_response = super(PaginationWithCreditSum, self).get_paginated_response(data)
        paginated_response.data['total_earned_credits'] = self.total_earned_credits
        paginated_response.data['total_used_credits'] = self.total_used_credits
        return paginated_response