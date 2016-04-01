#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Manage AWS SecurityGroups
"""
from boto.ec2.connection import EC2Connection

from openedx_configuration.models.model import Model


class SecurityGroup(Model):
    """
    Represent an AWS SecurityGroup
    """
    type_api = EC2Connection

    def __init__(self, environment, name, vpc, **kwargs):
        """
        Initialize a SecurityGroup
        """
        super(SecurityGroup, self).__init__(environment, name, **kwargs)
        self.vpc = vpc

    def _create(self, permissions=None, desciption=None, **kwargs):
        """
        Create a new security_group with permissions
        """
        permissions = permissions or []
        security_group = self.api.create_security_group(
            self.name,
            desciption,
            vpc_id=self.vpc.id,
        )
        security_group.add_tag('Name', self.name)
        security_group.add_tag('environment', self.environment)
        for cidr, permission, port, egress in permissions:
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

    def _destroy(self, *args, **kwargs):
        """
        Delete the SecurityGroup
        """
        self.api.delete_security_group(
            group_id=self.id,
        )

    @staticmethod
    def from_boto(security_group, vpc):
        """
        Initialize a SecurityGroup from a Boto object
        """
        return SecurityGroup(environment=None, name=None, vpc=vpc, model=security_group)

    @classmethod
    def get_all(cls, vpc):
        """
        Fetch all SecurityGroups associated with the VPC
        """
        api = cls.type_api()
        security_groups = api.get_all_security_groups(
            filters={
                'vpc-id': vpc.id,
                'tag:environment': vpc.environment,
            },
        )
        security_groups = [
            SecurityGroup.from_boto(security_group, vpc)
            for security_group in security_groups
        ]
        return security_groups

    def _get_one(self):
        """
        Fetch exactly one SecurityGroup via name/environment/vpc
        """
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
