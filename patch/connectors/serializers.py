from rest_framework import serializers
from .models import Connector, ConnectorConf


class ConnectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Connector
        fields = '__all__'


class ConnectorConfSerializer(serializers.ModelSerializer):
    connector_name = serializers.CharField(source='connector.name', read_only=True)

    class Meta:
        model = ConnectorConf
        fields = '__all__'
        extra_fields = ['connector_name']
