from django.db.models import Q
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
)
from rest_framework.permissions import IsAuthenticated

from bonds.models import Bond
from bonds.serializers import BondSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView


class HelloWorld(APIView):
    def get(self, request):
        return Response("Hello World!")


class BondsViewset(viewsets.ModelViewSet):
    serializer_class = BondSerializer
    queryset = Bond.objects.all()
    authentication_classes = (BasicAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    def filter_queryset(self, queryset):
        for field in ['legal_name', 'isin', 'currency', 'lei']:
            value = self.request.query_params.get(field, None)
            if value:
                queryset = queryset.filter(**{'{}__exact'.format(field): value})
        return queryset
