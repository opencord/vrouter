from header import *























#from core.models.service import Service
from core.models import Service



from core.models import AddressPool#from core.models.tenant import Tenant
from core.models import Tenant





class VRouterApp(XOSBase):

  KIND = "vROUTER"

  class Meta:
      app_label = "vrouter"
      name = "vrouter"
      verbose_name = "vRouter Service"

  # Primitive Fields (Not Relations)
  name = CharField( help_text = "application name", max_length = 50, null = False, db_index = False, blank = False )
  control_plane_connect_point = CharField( help_text = "port identifier in ONOS", max_length = 21, null = False, db_index = False, blank = False )
  ospf_enabled = BooleanField( default = True, help_text = "ospf enabled", null = False, db_index = False, blank = True )
  

  # Relations
  
  vrouter_service = ForeignKey(VRouterService, db_index = True, related_name = 'apps', null = False, blank = False )

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
  
  pass




class VRouterDevice(XOSBase):

  KIND = "vROUTER"

  class Meta:
      app_label = "vrouter"
      name = "vrouter"
      verbose_name = "vRouter Service"

  # Primitive Fields (Not Relations)
  name = CharField( help_text = "device friendly name", max_length = 20, null = True, db_index = False, blank = True )
  openflow_id = CharField( help_text = "device identifier in ONOS", max_length = 20, null = False, db_index = False, blank = False )
  config_key = CharField( default = "basic", max_length = 32, blank = False, help_text = "configuration key", null = False, db_index = False )
  driver = CharField( help_text = "driver type", max_length = 32, null = False, db_index = False, blank = False )
  

  # Relations
  
  vrouter_service = ForeignKey(VRouterService, db_index = True, related_name = 'devices', null = False, blank = False )

  
  pass




class VRouterInterface(XOSBase):

  KIND = "vROUTER"

  class Meta:
      app_label = "vrouter"
      name = "vrouter"
      verbose_name = "vRouter Service"

  # Primitive Fields (Not Relations)
  name = CharField( help_text = "interface name", max_length = 10, null = False, db_index = False, blank = False )
  mac = CharField( help_text = "interface mac", max_length = 17, null = False, db_index = False, blank = False )
  vlan = CharField( help_text = "interface vlan id", max_length = 10, null = True, db_index = False, blank = True )
  

  # Relations
  
  vrouter_port = ForeignKey(VRouterPort, db_index = True, related_name = 'interfaces', null = False, blank = False )

  
  pass




class VRouterIp(XOSBase):

  KIND = "vROUTER"

  class Meta:
      app_label = "vrouter"
      name = "vrouter"
      verbose_name = "vRouter Service"

  # Primitive Fields (Not Relations)
  name = CharField( help_text = "ip friendly name", max_length = 20, null = True, db_index = False, blank = True )
  ip = CharField( help_text = "interface ips", max_length = 19, null = False, db_index = False, blank = False )
  

  # Relations
  
  vrouter_interface = ForeignKey(VRouterInterface, db_index = True, related_name = 'ips', null = False, blank = False )

  
  pass




class VRouterPort(XOSBase):

  KIND = "vROUTER"

  class Meta:
      app_label = "vrouter"
      name = "vrouter"
      verbose_name = "vRouter Service"

  # Primitive Fields (Not Relations)
  name = CharField( help_text = "port friendly name", max_length = 20, null = True, db_index = False, blank = True )
  openflow_id = CharField( help_text = "port identifier in ONOS", max_length = 21, null = False, db_index = False, blank = False )
  

  # Relations
  
  vrouter_device = ForeignKey(VRouterDevice, db_index = True, related_name = 'ports', null = False, blank = False )
  vrouter_service = ForeignKey(VRouterService, db_index = True, related_name = 'device_ports', null = False, blank = False )

  
  pass




class VRouterService(Service):

  KIND = "vROUTER"

  class Meta:
      app_label = "vrouter"
      name = "vrouter"
      verbose_name = "vRouter Service"

  # Primitive Fields (Not Relations)
  rest_hostname = StrippedCharField( db_index = False, max_length = 255, null = True, blank = True )
  rest_port = IntegerField( default = 8181, null = False, blank = False, db_index = False )
  rest_user = StrippedCharField( default = "onos", max_length = 255, null = False, db_index = False, blank = False )
  rest_pass = StrippedCharField( default = "rocks", max_length = 255, null = False, db_index = False, blank = False )
  

  # Relations
  

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
  
      t = VRouterTenant(provider_service=self, **kwargs)
      t.public_ip = ip
      t.public_mac = self.ip_to_mac(ip)
      t.address_pool_id = ap.id
      t.save()
  
      return t
  
  pass




class VRouterTenant(Tenant):

  KIND = "vROUTER"

  class Meta:
      app_label = "vrouter"
      name = "vrouter"
      verbose_name = "vRouter Service"

  # Primitive Fields (Not Relations)
  public_ip = StrippedCharField( db_index = False, max_length = 30, null = True, blank = True )
  public_mac = StrippedCharField( db_index = False, max_length = 30, null = True, blank = True )
  

  # Relations
  
  address_pool = ForeignKey(AddressPool, db_index = True, related_name = 'vrouter_tenants', null = True, blank = True )

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
              ap[0].put_address(self.public_ip)
              self.public_ip = None
  
  def delete(self, *args, **kwargs):
      self.cleanup_addresspool()
      super(VRouterTenant, self).delete(*args, **kwargs)
  
  pass


