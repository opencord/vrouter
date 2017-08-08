
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
from synchronizers.new_base.syncstep import SyncStep
from synchronizers.new_base.modelaccessor import *
from xos.logger import Logger, logging

from requests.auth import HTTPBasicAuth
logger = Logger(level=logging.INFO)


class SyncVRouterDevice(SyncStep):
    provides = [VRouterDevice]

    observes = VRouterDevice

    requested_interval = 0

    def __init__(self, *args, **kwargs):
        super(SyncVRouterDevice, self).__init__(*args, **kwargs)

    def get_onos_fabric_addr(self, app):
        vrouter_service = VRouterService.objects.get(id=app.vrouter_service_id)

        return "http://%s:%s/onos/v1/network/configuration/" % (vrouter_service.rest_hostname, vrouter_service.rest_port)

    def get_onos_fabric_auth(self, app):
        vrouter_service = VRouterService.objects.get(id=app.vrouter_service_id)

        return HTTPBasicAuth(vrouter_service.rest_user, vrouter_service.rest_pass)

    def sync_record(self, device):

        logger.info("Sync'ing Edited vRouterDevice: %s" % device.name)

        onos_addr = self.get_onos_fabric_addr(device)

        data = {}
        data["driver"] = device.driver

        url = onos_addr + "devices/" + device.openflow_id + "/" + device.config_key + "/"

        print "POST %s for device %s" % (url, device.name)

        auth = self.get_onos_fabric_auth(device)
        r = requests.post(url, data=json.dumps(data), auth=auth)
        if (r.status_code != 200):
            print r
            raise Exception("Received error from vrouter device update (%d)" % r.status_code)

    def delete_record(self, device):

        logger.info("Sync'ing Deleted vRouterDevice: %s" % device.name)

        onos_addr = self.get_onos_fabric_addr()

        url = onos_addr + "devices/" + device.openflow_id + "/"

        print "DELETE %s for device %s" % (url, device.name)

        auth = self.get_onos_fabric_auth(device)
        r = requests.delete(url, auth=auth)
        if (r.status_code != 204):
            print r
            raise Exception("Received error from vrouter device deletion (%d)" % r.status_code)