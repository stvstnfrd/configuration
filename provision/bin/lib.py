#!/usr/bin/env python
from boto.vpc import VPCConnection
from boto.ec2.connection import EC2Connection
from boto.ec2.networkinterface import NetworkInterfaceCollection
from boto.ec2.networkinterface import NetworkInterfaceSpecification
from boto.route53.connection import Route53Connection

# sandbox
NAME_VPC = 'sandbox'
ENVIRONMENT = NAME_VPC
# sandbox-internet
NAME_GATEWAY = "{vpc}-internet".format(
    vpc=NAME_VPC,
)
# sandbox-public
NAME_SUBNET = "{vpc}-public".format(
    vpc=NAME_VPC,
)
# sandbox-public-openedx
NAME_SECURITY_GROUP = "{subnet}-openedx".format(
    vpc=NAME_VPC,
    subnet=NAME_SUBNET,
)
NAME_SECURITY_GROUP = 'public-sandbox-openedx'
# sandbox-internet-sandbox-public
NAME_ROUTE_TABLE = "{gateway}-{subnet}".format(
    gateway=NAME_GATEWAY,
    subnet=NAME_SUBNET,
)
# TODO:
NAME_ROUTE_TABLE = 'sandbox-routes'
NAME_NETWORK_ACL = NAME_SECURITY_GROUP
NAME_ZONE = 'sandbox.class.stanford.edu'

VPC_CIDR_BLOCK = '10.4.0.0/16'
SUBNET_CIDR_BLOCK = '10.4.0.0/24'
PUBLIC_CIDR_BLOCK = '0.0.0.0/0'
DESCRIPTION_SECURITY_GROUP = 'Blah blah blah'

PORTS = [
    # # cidr_block, permission, port, egress
    # (PUBLIC_CIDR_BLOCK, 'allow', 80, False),
    # (PUBLIC_CIDR_BLOCK, 'allow', 18010, False),
    (PUBLIC_CIDR_BLOCK, 'allow', 22, False),
    (PUBLIC_CIDR_BLOCK, 'allow', 22, True),
    # # (PUBLIC_CIDR_BLOCK, 'deny', None, False),
    # (PUBLIC_CIDR_BLOCK, 'allow', None, True),
]

connection_vpc = VPCConnection()
connection_ec2 = EC2Connection()

def create_instance(name, security_group_id, subnet_id):
    interface = NetworkInterfaceSpecification(
        associate_public_ip_address=True,
        subnet_id=subnet_id,
        groups=[
            security_group_id,
        ],
    )
    interfaces = NetworkInterfaceCollection(interface)
    reservation = connection_ec2.run_instances(
        'ami-b06717d0',  # image_id=TEMP-sandbox-dcadams
        # 'ami-2b2f594b',  # image_id=ubuntu-precise-12.04-amd64-server-20160201
        key_name='deployment',
        instance_type='t2.large',
        network_interfaces=interfaces,
    )
    instance = reservation.instances[0]
    instance.add_tag('Name', name)
    instance.add_tag('environment', ENVIRONMENT)
    instance.update()
    return instance


def create_vpc(environment, name, cidr_block):
    vpc = connection_vpc.create_vpc(cidr_block)
    connection_vpc.modify_vpc_attribute(vpc.id, enable_dns_support=True)
    connection_vpc.modify_vpc_attribute(vpc.id, enable_dns_hostnames=True)
    success = vpc.add_tag('Name', name)
    success = vpc.add_tag('environment', ENVIRONMENT)
    return vpc


def lookup_vpc(environment, name, cidr_block):
    vpcs = connection_vpc.get_all_vpcs(
        filters={
            'cidrBlock': cidr_block,
            'tag:Name': name,
            'tag:environment': ENVIRONMENT,
        },
    )
    assert len(vpcs) <= 1
    if len(vpcs) == 1:
        vpc = vpcs[0]
    else:
        vpc = None
    return vpc


def create_gateway(vpc_id, name):
    gateway = connection_vpc.create_internet_gateway()
    success = gateway.add_tag('Name', name)
    success = gateway.add_tag('environment', ENVIRONMENT)
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


def create_subnet(vpc_id, name, cidr_block):
    subnet = connection_vpc.create_subnet(vpc_id, cidr_block)
    success = subnet.add_tag('Name', name)
    success = subnet.add_tag('environment', ENVIRONMENT)
    return subnet


def lookup_subnet(vpc_id, name, cidr_block):
    subnets = connection_vpc.get_all_subnets(
        filters={
            'cidrBlock': SUBNET_CIDR_BLOCK,
            'vpcId': vpc_id,
            'tag:Name': name,
            'tag:environment': ENVIRONMENT,
        },
    )
    assert len(subnets) <= 1
    if len(subnets) == 1:
        subnet = subnets[0]
    else:
        subnet = None
    return subnet


def create_route_table(vpc_id, gateway_id, subnet_id, name, cidr_block):
    route_table = connection_vpc.create_route_table(vpc_id)
    route_table.add_tag('Name', name)
    success = route_table.add_tag('environment', ENVIRONMENT)
    success = connection_vpc.create_route(
        route_table.id,
        cidr_block,
        gateway_id=gateway_id,
    )
    association_id = connection_vpc.associate_route_table(route_table.id, subnet_id)
    return route_table


def lookup_route_table(vpc_id, gateway_id, subnet_id, name, cidr_block):
    route_tables = connection_vpc.get_all_route_tables(
        filters={
            # 'association.subnet-id': subnet_id,
            'tag:Name': name,
            'tag:environment': ENVIRONMENT,
            'vpc-id': vpc_id,
        },
    )
    assert len(route_tables) <= 1
    if len(route_tables) == 1:
        route_table = route_tables[0]
    else:
        route_table = None
    return route_table


def create_security_group(vpc_id, name, desciption):
    security_group = connection_ec2.create_security_group(
        name,
        desciption,
        vpc_id=vpc_id,
    )
    success = security_group.add_tag('Name', name)
    success = security_group.add_tag('environment', ENVIRONMENT)
    for cidr, permission, port, egress in PORTS:
        if not cidr or not port or permission != 'allow' or egress:
            continue
        success = connection_ec2.authorize_security_group(
            group_id=security_group.id,
            ip_protocol='tcp',
            to_port=port,
            from_port=port,
            cidr_ip=cidr,
        )
    return security_group


def lookup_security_group(vpc_id, name, description):
    security_groups = connection_ec2.get_all_security_groups(
        filters={
            # 'group-name': name,
            'vpc-id': vpc_id,
            # 'tag:Name': name,
            'tag:environment': ENVIRONMENT,
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
