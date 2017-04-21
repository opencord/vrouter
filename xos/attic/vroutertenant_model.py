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

