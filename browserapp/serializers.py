from rest_framework import serializers

class BrowserPayloadSerializer(serializers.Serializer):
    realm = serializers.CharField()
    username = serializers.CharField()
    apikey = serializers.CharField()

