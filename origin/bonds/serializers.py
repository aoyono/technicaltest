# -*- coding: utf-8 -*-
import requests
from bonds.models import Bond
from rest_framework import serializers


class BondSerializer(serializers.HyperlinkedModelSerializer):
    lei_api = "https://leilookup.gleif.org/api/v2/leirecords?lei={}"

    def __init__(self, *args, **kwargs):
        super(BondSerializer, self).__init__(*args, **kwargs)
        self.session = requests.Session()

    class Meta:
        model = Bond
        fields = '__all__'
        read_only_fields = ('legal_name',)

    def create(self, validated_data):
        instance = super(BondSerializer, self).create(validated_data)
        instance.legal_name = self.get_legal_name(instance.lei)
        instance.save()
        return instance

    def get_legal_name(self, lei):
        lei_api_response = self.session.get(self.lei_api.format(lei))
        lei_api_response.raise_for_status()
        legal_name = lei_api_response.json()[0]["Entity"]["LegalName"]["$"]
        return legal_name.replace(' ', '')
