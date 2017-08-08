
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


import os
import sys
import requests
import json
import urllib
from synchronizers.new_base.syncstep import SyncStep
from synchronizers.new_base.modelaccessor import *
from xos.logger import Logger, logging

from requests.auth import HTTPBasicAuth
logger = Logger(level=logging.INFO)


class SyncVRouterPort(SyncStep):
    provides = [VRouterPort]

    observes = VRouterPort

    requested_interval = 0

    def __init__(self, *args, **kwargs):
        super(SyncVRouterPort, self).__init__(*args, **kwargs)

    def get_onos_fabric_addr(self, app):
        vrouter_service = VRouterService.objects.get(id=app.vrouter_service_id)

        return "http://%s:%s/onos/v1/network/configuration/" % (vrouter_service.rest_hostname, vrouter_service.rest_port)

    def get_onos_fabric_auth(self, app):
        vrouter_service = VRouterService.objects.get(id=app.vrouter_service_id)

        return HTTPBasicAuth(vrouter_service.rest_user, vrouter_service.rest_pass)

    def sync_record(self, port):

        logger.info("Sync'ing Edited vRouterPort: %s" % port.name)

        # NOTE port is now related to service,
        # probably it makes more sense to relate them to a device (and device is related to service)
        onos_addr = self.get_onos_fabric_addr(port)

        # NOTE
        # from a port read all interfaces
        # from interfaces read all ips

        ifaces = []
        for interface in port.interfaces.all():
            iface = {
                'name': interface.name,
                'mac': interface.mac,
                'vlan': interface.vlan,
                'ips': []
            }

            for ip in interface.ips.all():
                iface["ips"].append(ip.ip)

            ifaces.append(iface)

        data = {}
        data[port.openflow_id] = {
            'interfaces': ifaces
        }

        url = onos_addr + "ports/"

        print "POST %s for port %s" % (url, port.name)

        auth = self.get_onos_fabric_auth(port)
        r = requests.post(url, data=json.dumps(data), auth=auth)
        if (r.status_code != 200):
            print r
            raise Exception("Received error from vrouter port update (%d)" % r.status_code)

    def delete_record(self, port):

        logger.info("Sync'ing Deleted vRouterPort: %s" % port.name)

        onos_addr = self.get_onos_fabric_addr()

        url = onos_addr + "ports/" + urllib.quote(port.openflow_id, safe='') + "/"

        print "DELETE %s for port %s" % (url, port.name)

        auth = self.get_onos_fabric_auth(port)
        r = requests.delete(url, auth=auth)
        if (r.status_code != 204):
            print r
            raise Exception("Received error from vrouter port deletion (%d)" % r.status_code)