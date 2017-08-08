
# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from django.db import models
from core.models import Service, XOSBase, Slice, Instance, ServiceInstance, Node, Image, User, Flavor, NetworkParameter, NetworkParameterType, Port, AddressPool
from core.models.xosbase import StrippedCharField
import os
from django.db import models, transaction
from django.forms.models import model_to_dict
from django.db.models import *
from operator import itemgetter, attrgetter, methodcaller
from core.models import Tag
from core.models.service import LeastLoadedNodeScheduler
import traceback
from xos.exceptions import *
from models_decl import *


class ConfigurationError(Exception):
    pass


class VRouterService (VRouterService_decl):
    class Meta:
        proxy = True

    def ip_to_mac(self, ip):
        (a, b, c, d) = ip.split('.')
        return "02:42:%02x:%02x:%02x:%02x" % (int(a), int(b), int(c), int(d))

    def get_gateways(self):
        gateways = []
        aps = self.addresspools.all()
        for ap in aps:
            gateways.append({"gateway_ip": ap.gateway_ip, "gateway_mac": ap.gateway_mac})

        return gateways

    def get_address_pool(self, name):
        ap = AddressPool.objects.filter(name=name, service=self)
        if not ap:
            raise Exception("vRouter unable to find addresspool %s" % name)
        return ap[0]

    def get_tenant(self, **kwargs):
        address_pool_name = kwargs.pop("address_pool_name")

        ap = self.get_address_pool(address_pool_name)

        ip = ap.get_address()
        if not ip:
            raise Exception("AddressPool '%s' has run out of addresses." % ap.name)

        t = VRouterTenant(owner=self, **kwargs)
        t.public_ip = ip
        t.public_mac = self.ip_to_mac(ip)
        t.address_pool_id = ap.id
        t.save()

        return t


class VRouterDevice (VRouterDevice_decl):

    class Meta:
        proxy = True
    pass

class VRouterPort (VRouterPort_decl):

    class Meta:
        proxy = True
    pass

class VRouterApp (VRouterApp_decl):

    class Meta:
        proxy = True
    def _get_interfaces(self):
        app_interfaces = []
        devices = VRouterDevice.objects.filter(vrouter_service=self.vrouter_service)
        for device in devices:
            ports = VRouterPort.objects.filter(vrouter_device=device.id)
            for port in ports:
                interfaces = VRouterInterface.objects.filter(vrouter_port=port.id)
                for iface in interfaces:
                    app_interfaces.append(iface.name)
        return app_interfaces

class VRouterInterface (VRouterInterface_decl):

    class Meta:
        proxy = True
    pass

class VRouterIp (VRouterIp_decl):

    class Meta:
        proxy = True
    pass

class VRouterTenant (VRouterTenant_decl):

    class Meta:
        proxy = True
    @property
    def gateway_ip(self):
        if not self.address_pool:
            return None
        return self.address_pool.gateway_ip

    @property
    def gateway_mac(self):
        if not self.address_pool:
            return None
        return self.address_pool.gateway_mac

    @property
    def cidr(self):
        if not self.address_pool:
            return None
        return self.address_pool.cidr

    @property
    def netbits(self):
        # return number of bits in the network portion of the cidr
        if self.cidr:
            parts = self.cidr.split("/")
            if len(parts) == 2:
                return int(parts[1].strip())
        return None

    def cleanup_addresspool(self):
        if self.address_pool:
            ap = self.address_pool
            if ap:
                ap.put_address(self.public_ip)
                self.public_ip = None

    def delete(self, *args, **kwargs):
        self.cleanup_addresspool()
        super(VRouterTenant, self).delete(*args, **kwargs)

