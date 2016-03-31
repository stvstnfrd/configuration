#!/usr/bin/env python
# TODO: add tags to network_acl
from boto.ec2.connection import EC2Connection
from boto.route53.connection import Route53Connection
from boto.vpc import VPCConnection

from openedx_configuration.models.vpc.vpc import Vpc


PUBLIC_CIDR_BLOCK = '0.0.0.0/0'


connection_vpc = VPCConnection()
connection_ec2 = EC2Connection()


def lookup_all_vpcs():
    vpcs = Vpc.all()
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


def lookup_hosted_zone(name):
    connection_route53 = Route53Connection()
    zone = connection_route53.get_zone(name)
    return zone


def create_hosted_zone(name):
    connection_route53 = Route53Connection()
    name = name + '.'
    zone = connection_route53.create_zone(name)
    return zone
