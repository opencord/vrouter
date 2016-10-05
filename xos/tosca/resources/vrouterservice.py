from service import XOSService
from services.vrouter.models import VRouterService

class XOSVRouterService(XOSService):
    provides = "tosca.nodes.VRouterService"
    xos_model = VRouterService
    copyin_props = ["view_url", "icon_url", "enabled", "published", "public_key", "versionNumber"]

