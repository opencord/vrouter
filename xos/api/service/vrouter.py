from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import serializers
from rest_framework import generics
from rest_framework import status
from core.models import *
from django.forms import widgets
from services.vrouter.models import *
from xos.apibase import XOSListCreateAPIView, XOSRetrieveUpdateDestroyAPIView, XOSPermissionDenied
from api.xosapi_helpers import PlusModelSerializer, XOSViewSet, ReadOnlyField
import json

BASE_NAME = 'vrouter'


class VRouterServiceSerializer(PlusModelSerializer):
    id = ReadOnlyField()
    name = serializers.CharField(required=False)
    kind = serializers.CharField(required=False)
    service_specific_attribute = serializers.CharField(required=False)
    humanReadableName = serializers.SerializerMethodField("getHumanReadableName")

    class Meta:
        model = VRouterService
        fields = ('humanReadableName', 'id', 'name', 'kind', 'service_specific_attribute')

    def getHumanReadableName(self, obj):
        return obj.__unicode__()


class VRouterDeviceSerializer(PlusModelSerializer):
    id = ReadOnlyField()
    name = serializers.CharField(required=False)
    openflow_id = serializers.CharField(required=False)
    config_key = serializers.CharField(required=False)
    driver = serializers.CharField(required=False)
    vrouter_service = serializers.PrimaryKeyRelatedField(read_only=True)

    ports = serializers.SerializerMethodField("getDevicePorts")

    def getDevicePorts(self, device):
        ports = VRouterPort.objects.filter(vrouter_device=device.id)
        return VRouterPortSerializer(ports, many=True).data

    class Meta:
        model = VRouterDevice
        fields = ('id', 'name', 'openflow_id', 'config_key', 'driver', 'vrouter_service', 'ports')


class VRouterPortSerializer(PlusModelSerializer):
    id = ReadOnlyField()
    name = serializers.CharField(required=False)
    openflow_id = serializers.CharField(required=False)
    interfaces = serializers.SerializerMethodField("getPortInterfaces")

    def getPortInterfaces(self, port):
        interfaces = VRouterInterface.objects.filter(vrouter_port=port.id)
        return VRouterInterfaceSerializer(interfaces, many=True).data

    class Meta:
        model = VRouterPort
        fields = ('id', 'name', 'openflow_id', 'interfaces')


class VRouterInterfaceSerializer(PlusModelSerializer):
    id = ReadOnlyField()
    name = serializers.CharField(required=False)
    mac = serializers.CharField(required=False)
    vlan = serializers.CharField(required=False)
    ips = serializers.SerializerMethodField("getInterfaceIps")

    def getInterfaceIps(self, interface):
        interfaces = VRouterIp.objects.filter(vrouter_interface=interface.id)
        return VRouterIpSerializer(interfaces, many=True).data

    class Meta:
        model = VRouterPort
        fields = ('id', 'name', 'mac', 'vlan', 'ips')


class VRouterIpSerializer(PlusModelSerializer):
    id = ReadOnlyField()
    ip = serializers.CharField(required=False)
    name = serializers.CharField(required=False)

    class Meta:
        model = VRouterIp
        fields = ('id', 'ip', 'name')


class VRouterAppSerializer(PlusModelSerializer):
    id = ReadOnlyField()
    name = serializers.CharField(required=False)
    control_plane_connect_point = serializers.CharField(required=False)
    ospf_enabled = serializers.BooleanField(required=False)
    interfaces = serializers.SerializerMethodField("dumpInterfaces")

    def dumpInterfaces(self, app):
        return json.dumps(app.interfaces)

    class Meta:
        model = VRouterApp
        fields = ('id', 'name', 'control_plane_connect_point', 'ospf_enabled', 'interfaces')


class VRouterServiceViewSet(XOSViewSet):
    base_name = BASE_NAME
    method_name = "vrouter"
    method_kind = "viewset"
    queryset = VRouterService.objects.filter(kind='vROUTER')
    serializer_class = VRouterServiceSerializer

    @classmethod
    def get_urlpatterns(self, api_path="^"):
        patterns = super(VRouterServiceViewSet, self).get_urlpatterns(api_path=api_path)

        patterns.append(self.detail_url("devices/$", {
            "get": "get_devices"
        }, "vrouter_devices"))

        patterns.append(self.detail_url("apps/$", {
            "get": "get_apps"
        }, "vrouter_apps"))

        return patterns

    def get_devices(self, request, pk=None):
        if (not request.user.is_authenticated()):
            raise XOSPermissionDenied("You must be authenticated in order to use this API")
        else:
            if(pk is not None):
                devices = VRouterDevice.objects.filter(vrouter_service=pk)
            else:
                devices = VRouterDevice.objects.all()
            return Response(VRouterDeviceSerializer(devices, many=True).data)

    def get_apps(self, request, pk=None):
        if (not request.user.is_authenticated()):
            raise XOSPermissionDenied("You must be authenticated in order to use this API")
        else:
            if(pk is not None):
                apps = VRouterApp.objects.filter(vrouter_service=pk)
            else:
                apps = VRouterApp.objects.all()
            return Response(VRouterAppSerializer(apps, many=True).data)
