import os
import sys
import requests
import json
from django.db.models import Q, F
from services.vrouter.models import *
from synchronizers.base.syncstep import SyncStep
from xos.logger import Logger, logging

# from core.models import Service
from requests.auth import HTTPBasicAuth

parentdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, parentdir)

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