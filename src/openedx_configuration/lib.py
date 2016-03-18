#!/usr/bin/env python
# TODO: add tags to network_acl
from boto.ec2.blockdevicemapping import BlockDeviceMapping
from boto.ec2.blockdevicemapping import BlockDeviceType
from boto.ec2.connection import EC2Connection
from boto.route53.connection import Route53Connection
from boto.vpc import VPCConnection


PUBLIC_CIDR_BLOCK = '0.0.0.0/0'
PORTS = [
    # cidr_block, permission, port, egress
    (PUBLIC_CIDR_BLOCK, 'allow', 22, False),
    (PUBLIC_CIDR_BLOCK, 'allow', 80, False),
    (PUBLIC_CIDR_BLOCK, 'allow', 18010, False),
]


# sandbox
def generate_name_subnet(vpc):
    name = "{vpc}-public".format(
        vpc=vpc.tags['Name'],
    )
    return name


# sandbox-public-openedx
def generate_name_security_group(vpc):
    name = "{subnet}-openedx".format(
        vpc=vpc.tags['Name'],
        subnet=generate_name_subnet(vpc),
    )
    name = 'public-sandbox-openedx'
    return name


# sandbox-internet
def generate_name_gateway(vpc):
    name = "{vpc}-internet".format(
        vpc=vpc.tags['Name'],
    )
    return name


# sandbox-internet-sandbox-public
# sandbox-internet-route
def generate_name_route_table(vpc):
    name = "{gateway}-{subnet}".format(
        gateway=generate_name_gateway(vpc),
        subnet=generate_name_subnet(vpc),
    )
    name = 'sandbox-routes'
    return name


connection_vpc = VPCConnection()
connection_ec2 = EC2Connection()


def create_vpc(environment, cidr_block):
    vpc = connection_vpc.create_vpc(cidr_block)
    connection_vpc.modify_vpc_attribute(vpc.id, enable_dns_support=True)
    connection_vpc.modify_vpc_attribute(vpc.id, enable_dns_hostnames=True)
    success = vpc.add_tag('Name', environment)
    success = vpc.add_tag('environment', environment)
    return vpc


def lookup_all_vpcs():
    vpcs = connection_vpc.get_all_vpcs()
    print('Host *')
    print('    ForwardAgent yes')
    print('    User GITHUB_USERNAME_GOES_HERE')
    for vpc in vpcs:
        vpc_name = vpc.tags.get('Name', '')
        if vpc_name.endswith('-vpc'):
            vpc_name = vpc_name[:-4]
        print('')
        instances = connection_ec2.get_only_instances(
            filters={
                'vpc-id': vpc.id,
            },
        )
        jumpbox = [
            instance
            for instance in instances
            if instance.tags.get('Name', '').startswith('jumpbox.')
        ]
        if len(jumpbox):
            jumpbox = jumpbox[0]
        for instance in instances:
            name = instance.tags.get('Name', '')
            if not name:
                continue
            if jumpbox and jumpbox.id != instance.id:
                jumpbox_name = 'jump.' + vpc_name
                print('Host ' + name)
                print('    ProxyCommand ssh -W ' + instance.private_ip_address + ':%p ' + jumpbox_name)
            elif jumpbox:
                name = 'jump.' + vpc_name
                print('Host ' + name)
                print('    HostName ' + jumpbox.ip_address)
            else:
                print('Host ' + name)
                print('    HostName ' + instance.ip_address)
            # if jumpbox:
            #     pass
            # print(name, instance, instance.tags)

def lookup_vpc(environment, cidr_block):
    vpcs = connection_vpc.get_all_vpcs(
        filters={
            'cidrBlock': cidr_block,
            'tag:Name': environment,
            'tag:environment': environment,
        },
    )
    assert len(vpcs) <= 1
    if len(vpcs) == 1:
        vpc = vpcs[0]
    else:
        vpc = None
    return vpc


def create_gateway(vpc, name):
    vpc_id = vpc.id
    environment = vpc.tags['environment']
    gateway = connection_vpc.create_internet_gateway()
    success = gateway.add_tag('Name', name)
    success = gateway.add_tag('environment', environment)
    success = connection_vpc.attach_internet_gateway(gateway.id, vpc_id)
    return gateway


def lookup_gateway(vpc_id, name):
    gateways = connection_vpc.get_all_internet_gateways(
        filters={
            'attachment.vpc-id': vpc_id,
        },
    )
    assert len(gateways) <= 1
    if len(gateways) == 1:
        gateway = gateways[0]
    else:
        gateway = None
    return gateway


def create_subnet(vpc, name, cidr_block):
    environment = vpc.tags['environment']
    subnet = connection_vpc.create_subnet(vpc.id, cidr_block)
    success = subnet.add_tag('Name', name)
    success = subnet.add_tag('environment', environment)
    return subnet


def lookup_subnet(vpc, environment, name, cidr_block):
    vpc_id = vpc.id
    subnets = connection_vpc.get_all_subnets(
        filters={
            'cidrBlock': cidr_block,
            'vpcId': vpc_id,
            'tag:Name': name,
            'tag:environment': environment,
        },
    )
    assert len(subnets) <= 1
    if len(subnets) == 1:
        subnet = subnets[0]
    else:
        subnet = None
    return subnet


def create_route_table(vpc, gateway_id, subnet_id, name, cidr_block):
    vpc_id = vpc.id
    environment = vpc.tags['environment']
    route_table = connection_vpc.create_route_table(vpc_id)
    route_table.add_tag('Name', name)
    success = route_table.add_tag('environment', environment)
    success = connection_vpc.create_route(
        route_table.id,
        cidr_block,
        gateway_id=gateway_id,
    )
    association_id = connection_vpc.associate_route_table(route_table.id, subnet_id)
    return route_table


def lookup_route_table(vpc, gateway_id, subnet_id, name, cidr_block):
    vpc_id = vpc.id
    environment = vpc.tags['environment']
    route_tables = connection_vpc.get_all_route_tables(
        filters={
            # 'association.subnet-id': subnet_id,
            'tag:Name': name,
            'tag:environment': environment,
            'vpc-id': vpc_id,
        },
    )
    assert len(route_tables) <= 1
    if len(route_tables) == 1:
        route_table = route_tables[0]
    else:
        route_table = None
    return route_table


def create_security_group(vpc, name, desciption):
    vpc_id = vpc.id
    environment = vpc.tags['environment']
    security_group = connection_ec2.create_security_group(
        name,
        desciption,
        vpc_id=vpc_id,
    )
    success = security_group.add_tag('Name', name)
    success = security_group.add_tag('environment', environment)
    for cidr, permission, port, egress in PORTS:
        if not cidr or not port or permission != 'allow':
            continue
        success = connection_ec2.authorize_security_group(
            group_id=security_group.id,
            ip_protocol='tcp',
            to_port=port,
            from_port=port,
            cidr_ip=cidr,
        )
    return security_group


def lookup_security_group(vpc, name, description):
    vpc_id = vpc.id
    environment = vpc.tags['environment']
    security_groups = connection_ec2.get_all_security_groups(
        filters={
            # 'group-name': name,
            'vpc-id': vpc_id,
            # 'tag:Name': name,
            'tag:environment': environment,
        },
    )
    assert len(security_groups) <= 1
    if len(security_groups) == 1:
        security_group = security_groups[0]
    else:
        security_group = None
    return security_group


def lookup_hosted_zone(name):
    connection_route53 = Route53Connection()
    zone = connection_route53.get_zone(name)
    return zone


def create_hosted_zone(name):
    connection_route53 = Route53Connection()
    name = name + '.'
    zone = connection_route53.create_zone(name)
    return zone
