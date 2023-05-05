from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view
from rest_framework import serializers
from .serializers import BrowserPayloadSerializer
from .browser_controller import (
    create_browser, get_browser_status, get_realm_browsers,
    delete_browser, delete_realm
)

# Parameter definitions
post_payload_param = openapi.Parameter(
    name="payload",
    in_=openapi.IN_BODY,
    description="JSON payload containing required data",
    required=True,
    schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={
        'realm': openapi.Schema(type=openapi.TYPE_STRING, description='Realm name'),
        'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
        'apikey': openapi.Schema(type=openapi.TYPE_STRING, description='API key'),
    }),
)
request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['realm', 'username', 'apikey'],
    properties={
        'realm': openapi.Schema(type=openapi.TYPE_STRING, description='Realm name'),
        'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
        'apikey': openapi.Schema(type=openapi.TYPE_STRING, description='API key'),
    }
)

@api_view(['POST'])
@swagger_auto_schema(operation_description="Create browser instance",request_body=post_payload_param)
def create_browser_view(request):
    serializer = BrowserPayloadSerializer(data=request.data)
    if not serializer.is_valid():
        return JsonResponse({"error": "Invalid payload"}, status=400)
    host_header = request.headers.get('X-Forwarded-Host') or request.headers.get('Host')
    data = serializer.validated_data
    result = create_browser(data["realm"], data["username"], data["apikey"])
    result['url'] = "https://"+host_header+"/"+data["realm"]+"/"+data["username"]+"/"
    return JsonResponse(result)

@api_view(['POST'])
@swagger_auto_schema(operation_description="Get browser status",request_body=request_body)
def get_browser_status_view(request):
    serializer = BrowserPayloadSerializer(data=request.data)
    if not serializer.is_valid():
        return JsonResponse({"error": "Invalid payload"}, status=400)

    data = serializer.validated_data
    result = get_browser_status(data["realm"], data["username"], data["apikey"])
    return JsonResponse(result)

@api_view(['POST'])
@swagger_auto_schema(operation_description="Get realm browser instances",request_body=request_body)
def get_realm_browsers_view(request):
    serializer = BrowserPayloadSerializer(data=request.data)
    if not serializer.is_valid():
        return JsonResponse({"error": "Invalid payload"}, status=400)

    data = serializer.validated_data
    result = get_realm_browsers(data["realm"], data["apikey"])
    return JsonResponse(result)

@api_view(['DELETE'])
@swagger_auto_schema(operation_description="Delete browser instance",request_body=request_body)
def delete_browser_view(request):
    serializer = BrowserPayloadSerializer(data=request.data)
    if not serializer.is_valid():
        return JsonResponse({"error": "Invalid payload"}, status=400)

    data = serializer.validated_data
    result = delete_browser(data["realm"], data["username"], data["apikey"])
    return JsonResponse(result)

@api_view(['DELETE'])
@swagger_auto_schema(operation_description="Delete realm",request_body=request_body)
def delete_realm_view(request):
    serializer = BrowserPayloadSerializer(data=request.data)
    if not serializer.is_valid():
        return JsonResponse({"error": "Invalid payload"}, status=400)

    data = serializer.validated_data
    result = delete_realm(data["realm"], data["apikey"])
    return JsonResponse(result)

