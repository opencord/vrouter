from django.db import models
from core.models import Service, PlCoreBase, Slice, Instance, Tenant, TenantWithContainer, Node, Image, User, Flavor, NetworkParameter, NetworkParameterType, Port, AddressPool
from core.models.plcorebase import StrippedCharField
import os
from django.db import models, transaction
from django.forms.models import model_to_dict
from django.db.models import *
from operator import itemgetter, attrgetter, methodcaller
from core.models import Tag
from core.models.service import LeastLoadedNodeScheduler
import traceback
from xos.exceptions import *
from xos.config import Config


class ConfigurationError(Exception):
    pass


VROUTER_KIND = "vROUTER"
APP_LABEL = "vrouter"

# NOTE: don't change VROUTER_KIND unless you also change the reference to it
#   in tosca/resources/network.py

CORD_USE_VTN = getattr(Config(), "networking_use_vtn", False)

