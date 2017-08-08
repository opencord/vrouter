
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


from service import XOSService
from services.vrouter.models import *


class XOSVRouterService(XOSService):
    provides = "tosca.nodes.VRouterService"
    xos_model = VRouterService
    copyin_props = ["view_url", "icon_url", "enabled", "published", "public_key", "versionNumber",
                    "rest_hostname", "rest_port", "rest_user", "rest_pass"]


class XOSVRouterDevice(XOSService):
    provides = "tosca.nodes.VRouterDevice"
    xos_model = VRouterDevice
    copyin_props = ['openflow_id', 'config_key', 'driver']

    def get_xos_args(self):
        args = super(XOSVRouterDevice, self).get_xos_args()

        serviceName = self.get_requirement("tosca.relationships.MemberOfService", throw_exception=False)
        if serviceName:
            service = self.get_xos_object(Service, name=serviceName)
            args["vrouter_service_id"] = service.id
        return args


class XOSVRouterPort(XOSService):
    provides = "tosca.nodes.VRouterPort"
    xos_model = VRouterPort
    copyin_props = ['openflow_id']

    def get_xos_args(self):
        args = super(XOSVRouterPort, self).get_xos_args()

        deviceName = self.get_requirement("tosca.relationships.PortOfDevice", throw_exception=False)
        if deviceName:
            device = self.get_xos_object(VRouterDevice, name=deviceName)
            args["vrouter_device"] = device

        serviceName = self.get_requirement("tosca.relationships.MemberOfService", throw_exception=False)
        if serviceName:
            service = self.get_xos_object(Service, name=serviceName)
            args["vrouter_service_id"] = service.id

        return args


class XOSVRouterInterface(XOSService):
    provides = "tosca.nodes.VRouterInterface"
    xos_model = VRouterInterface
    copyin_props = ['name', 'mac', 'vlan']

    def get_xos_args(self):
        args = super(XOSVRouterInterface, self).get_xos_args()

        portName = self.get_requirement("tosca.relationships.InterfaceOfPort", throw_exception=False)
        if portName:
            port = self.get_xos_object(VRouterPort, name=portName)
            args["vrouter_port"] = port
        return args


class XOSVRouterIp(XOSService):
    provides = "tosca.nodes.VRouterIp"
    xos_model = VRouterIp
    copyin_props = ['ip']

    def get_xos_args(self):
        args = super(XOSVRouterIp, self).get_xos_args()

        interfaceName = self.get_requirement("tosca.relationships.IpOfInterface", throw_exception=False)
        if interfaceName:
            interface = self.get_xos_object(VRouterInterface, name=interfaceName)
            args["vrouter_interface"] = interface
        return args


class XOSVRouterApp(XOSService):
    provides = "tosca.nodes.VRouterApp"
    xos_model = VRouterApp
    copyin_props = ['name', 'control_plane_connect_point', 'ospf_enabled']

    def get_xos_args(self):
        args = super(XOSVRouterApp, self).get_xos_args()

        serviceName = self.get_requirement("tosca.relationships.MemberOfService", throw_exception=True)
        if serviceName:
            service = self.get_xos_object(Service, name=serviceName)
            args["vrouter_service_id"] = service.id
        return args
