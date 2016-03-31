class Vpc():
    def __init__(self, environment, name, api=None):
        pass
    def create(self, cidr_block, enable_dns_support, enable_dns_hostnames):
        pass
    def lookup(self):
        pass
    def destroy(self):
        pass

class Gateway():
    def __init__(self, environment, name, api=None):
        pass
    def create(self):
        pass
    def lookup(self):
        pass
    def destroy(self):
        pass

class RouteTable():
    def __init__(self, environment, name, subnet, api=None):
        pass
        pass
    def create(self, gateway_id, cidr_block):
        pass
    def lookup(self):
        pass
    def destroy(self):
        pass

class Subnet():
    def __init__(self, environment, cidr_block, name, api=None):
        pass
    def create(self):
        pass
    def lookup(self):
        pass
    def destroy(self):
        pass

class SecurityGroup():
    def __init__(self, environment, name, vpc=None, api=None):
        pass
    def create(self, desciption):
        pass
    def lookup(self):
        pass
    def destroy(self):
        pass

class Instance():
    def __init__(self, environment, api=None):
        pass
    def create(self):
        pass
    def lookup(self):
        pass
    def destroy(self):
        pass
