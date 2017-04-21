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

