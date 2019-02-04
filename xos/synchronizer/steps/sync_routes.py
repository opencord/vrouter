
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

import requests
from requests.auth import HTTPBasicAuth
from xossynchronizer.steps.syncstep import SyncStep, DeferredException
from xossynchronizer.modelaccessor import VRouterStaticRoute, model_accessor

from helpers import Helpers
from multistructlog import create_logger
from xosconfig import Config

log = create_logger(Config().get('logging'))

class SyncRoutes(SyncStep):
    provides = [VRouterStaticRoute]
    observes = VRouterStaticRoute

    # Get fabric service info
    def get_onos_fabric_service(self, model):
        vrouter_service = model.vrouter.owner
        fabric_service = vrouter_service.provider_services[0]
        onos_fabric_service = fabric_service.provider_services[0]

        return onos_fabric_service

    def sync_record(self, model):
        onos_fabric_service = self.get_onos_fabric_service(model)

        onos = Helpers.get_onos_info(onos_fabric_service.leaf_model)
        onos_basic_auth = HTTPBasicAuth(onos['user'], onos['pass'])

        data = {
          "prefix": model.prefix,
          "nextHop": model.next_hop
        }

        url = '%s:%s/onos/routeservice/routes' % (onos['url'], onos['port'])
        request = requests.post(url, json=data, auth=onos_basic_auth)

        if request.status_code != 204:
            log.error("Request failed", response=request.text)
            raise Exception("Failed to add static route %s via %s in ONOS" % (model.prefix, model.next_hop))
        else:
            try:
                print request.json()
            except Exception:
                print request.text

    def delete_record(self, model):
        onos_fabric_service = self.get_onos_fabric_service(model)

        onos = Helpers.get_onos_info(onos_fabric_service.leaf_model)
        onos_basic_auth = HTTPBasicAuth(onos['user'], onos['pass'])

        data = {
          "prefix": model.prefix,
          "nextHop": model.next_hop
        }

        url = '%s:%s/onos/routeservice/routes' % (onos['url'], onos['port'])
        request = requests.delete(url, json=data, auth=onos_basic_auth)

        if request.status_code != 204:
            log.error("Request failed", response=request.text)
            raise Exception("Failed to delete static route %s via %s in ONOS" % (model.prefix, model.next_hop))
        else:
            try:
                print request.json()
            except Exception:
                print request.text
