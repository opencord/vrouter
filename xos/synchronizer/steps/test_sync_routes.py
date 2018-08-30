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

import unittest

import functools
from mock import patch, call, Mock, PropertyMock
import requests_mock
import multistructlog
from multistructlog import create_logger

import os, sys

# Hack to load synchronizer framework
test_path=os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
xos_dir=os.path.join(test_path, "../../..")
if not os.path.exists(os.path.join(test_path, "new_base")):
    xos_dir=os.path.join(test_path, "../../../../../../orchestration/xos/xos")
    services_dir = os.path.join(xos_dir, "../../xos_services")
sys.path.append(xos_dir)
sys.path.append(os.path.join(xos_dir, 'synchronizers', 'new_base'))
# END Hack to load synchronizer framework

# generate model from xproto
def get_models_fn(service_name, xproto_name):
    name = os.path.join(service_name, "xos", xproto_name)
    if os.path.exists(os.path.join(services_dir, name)):
        return name
    else:
        name = os.path.join(service_name, "xos", "synchronizer", "models", xproto_name)
        if os.path.exists(os.path.join(services_dir, name)):
            return name
    raise Exception("Unable to find service=%s xproto=%s" % (service_name, xproto_name))
# END generate model from xproto

def match_json(desired, req):
    if desired!=req.json():
        raise Exception("Got request %s, but body is not matching" % req.url)
        return False
    return True

class TestSyncRoutes(unittest.TestCase):

    def setUp(self):

        self.sys_path_save = sys.path
        sys.path.append(xos_dir)
        sys.path.append(os.path.join(xos_dir, 'synchronizers', 'new_base'))

        # Setting up the config module
        from xosconfig import Config
        config = os.path.join(test_path, "../test_config.yaml")
        Config.clear()
        Config.init(config, "synchronizer-config-schema.yaml")
        # END Setting up the config module

        from synchronizers.new_base.mock_modelaccessor_build import build_mock_modelaccessor
        build_mock_modelaccessor(xos_dir, services_dir, [get_models_fn("vrouter", "vrouter.xproto")])
        import synchronizers.new_base.modelaccessor

        from sync_routes import SyncRoutes, model_accessor

        # import all class names to globals
        for (k, v) in model_accessor.all_model_classes.items():
            globals()[k] = v


        self.sync_step = SyncRoutes
        self.sync_step.log = Mock()


        # mock onos-fabric
        onos_fabric = Mock()
        onos_fabric.name = "onos-fabric"
        onos_fabric.rest_hostname = "onos-fabric"
        onos_fabric.rest_port = "8181"
        onos_fabric.rest_username = "onos"
        onos_fabric.rest_password = "rocks"

        onos_fabric_base = Mock()
        onos_fabric_base.leaf_model = onos_fabric

        self.fabric = Mock()
        self.fabric.name = "fabric"
        self.fabric.provider_services = [onos_fabric_base]

        self.vrouter = Mock()
        self.vrouter.name = "vrouter"
        self.vrouter.provider_services = [self.fabric]

        # create a mock VRouterStaticRoute instance
        self.o = Mock()
        self.o.id = 1
        self.o.vrouter.owner = self.vrouter
        self.o.tologdict.return_value = {}




    def tearDown(self):
        self.o = None
        sys.path = self.sys_path_save

    @requests_mock.Mocker()
    def test_sync_route(self, m):

        self.o.next_hop = "192.168.0.254"
        self.o.prefix = "0.0.0.0/0"

        expected_conf = {
          "prefix": self.o.prefix,
          "nextHop": self.o.next_hop
        }

        m.post("http://onos-fabric:8181/onos/routeservice/routes",
               status_code=204,
               additional_matcher=functools.partial(match_json, expected_conf))

        self.sync_step().sync_record(self.o)

        self.assertTrue(m.called)

    @requests_mock.Mocker()
    def test_delete_route(self, m):

        self.o.next_hop = "192.168.0.254"
        self.o.prefix = "0.0.0.0/0"

        expected_conf = {
            "prefix": self.o.prefix,
            "nextHop": self.o.next_hop
        }

        m.delete("http://onos-fabric:8181/onos/routeservice/routes",
            status_code=204,
            additional_matcher=functools.partial(match_json, expected_conf))

        self.sync_step().delete_record(self.o)

        self.assertTrue(m.called)