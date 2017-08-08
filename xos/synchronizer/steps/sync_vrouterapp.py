
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


class SyncVRouterApp(SyncStep):
    provides = [VRouterApp]

    observes = VRouterApp

    requested_interval = 0

    def __init__(self, *args, **kwargs):
        super(SyncVRouterApp, self).__init__(*args, **kwargs)

    def get_onos_fabric_addr(self, app):
        vrouter_service = VRouterService.objects.get(id=app.vrouter_service_id)

        return "http://%s:%s/onos/v1/network/configuration/" % (vrouter_service.rest_hostname, vrouter_service.rest_port)

    def get_onos_fabric_auth(self, app):
        vrouter_service = VRouterService.objects.get(id=app.vrouter_service_id)

        return HTTPBasicAuth(vrouter_service.rest_user, vrouter_service.rest_pass)

    def sync_record(self, app):

        logger.info("Sync'ing Edited vRouterApps: %s" % app.name)

        onos_addr = self.get_onos_fabric_addr(app)

        data = {}
        data["controlPlaneConnectPoint"] = app.control_plane_connect_point
        data["ospfEnabled"] = app.ospf_enabled
        data["interfaces"] = app.interfaces

        url = onos_addr + "apps/" + app.name + "/router/"

        print "POST %s for app %s" % (url, app.name)

        # XXX fixme - hardcoded auth
        auth = self.get_onos_fabric_auth(app)
        r = requests.post(url, data=json.dumps(data), auth=auth)
        if (r.status_code != 200):
            print r
            raise Exception("Received error from vrouter app update (%d)" % r.status_code)

    def delete_record(self, app):

        logger.info("Sync'ing Deleted vRouterApps: %s" % app.name)

        onos_addr = self.get_onos_fabric_addr()

        url = onos_addr + "apps/" + app.name + "/"

        print "DELETE %s for app %s" % (url, app.name)

        auth = self.get_onos_fabric_auth(app)
        r = requests.delete(url, auth=auth)
        if (r.status_code != 204):
            print r
            raise Exception("Received error from vrouter app deletion (%d)" % r.status_code)