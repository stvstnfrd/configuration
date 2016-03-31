#!/usr/bin/env python
# -*- coding: utf-8 -*-
from boto.ec2.connection import EC2Connection

from openedx_configuration.lib import *
from openedx_configuration.models.model import Model
from openedx_configuration.models.vpc.vpc import Vpc

PORTS = [
    # cidr_block, permission, port, egress
    (PUBLIC_CIDR_BLOCK, 'allow', 22, False),
    (PUBLIC_CIDR_BLOCK, 'allow', 80, False),
    (PUBLIC_CIDR_BLOCK, 'allow', 18010, False),
]


class SecurityGroup(Model):
    def __init__(self, environment, name, vpc=None, model=None, api=None):
        super(SecurityGroup, self).__init__(
            environment,
            name,
            model,
        )
        self.api = api or EC2Connection()
        self.vpc = vpc or Vpc(environment)

    @staticmethod
    def from_boto(security_group):
        return SecurityGroup(environment=None, name=None, model=security_group)

    @staticmethod
    def all(vpc):
        api = EC2Connection()
        security_groups = api.get_all_security_groups(
            filters={
                'vpc-id': vpc.id,
            },
        )
        security_groups = [
            SecurityGroup.from_boto(security_group)
            for security_group in security_groups
        ]
        return security_groups

    def _lookup(self):
        security_groups = self.api.get_all_security_groups(
            filters={
                'group-name': self.name,
                'vpc-id': self.vpc.id,
                'tag:Name': self.name,
                'tag:environment': self.environment,
            },
        )
        assert len(security_groups) <= 1
        if len(security_groups) == 1:
            security_group = security_groups[0]
        else:
            security_group = None
        return security_group

    def _create(self, desciption):
        security_group = connection_ec2.create_security_group(
            self.name,
            desciption,
            vpc_id=self.vpc.id,
        )
        security_group.add_tag('Name', self.name)
        security_group.add_tag('environment', self.environment)
        for cidr, permission, port, egress in PORTS:
            if not cidr or not port or permission != 'allow':
                continue
            self.api.authorize_security_group(
                group_id=security_group.id,
                ip_protocol='tcp',
                to_port=port,
                from_port=port,
                cidr_ip=cidr,
            )
        return security_group

    def _destroy(self):
        self.api.delete_security_group(
            group_id=self.id,
        )
