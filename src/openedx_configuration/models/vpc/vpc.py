#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Manage AWS Virtual Private Clouds
"""
from openedx_configuration.models.ec2.security_group import SecurityGroup
from openedx_configuration.models.model import Model
from openedx_configuration.models.vpc.gateway import Gateway
from openedx_configuration.models.vpc.route_table import RouteTable
from openedx_configuration.models.vpc.subnet import Subnet


class Vpc(Model):
    """
    Represent an AWS Virtual Private Cloud
    """
    enable_dns_support = True
    enable_dns_hostnames = True

    def __init__(self, environment, name=None, **kwargs):
        """
        Initialize a VPC

        Ideally, `environment` and `name` would always be equal.
        The terms `environment` and `VPC` should be considered generally
        interchangeable; the latter being an implementation of the
        former concept. Of course, there are legacy exceptions..
        """
        name = name or environment
        super(Vpc, self).__init__(environment, name, **kwargs)

    def _create(self, cidr_block, *args, **kwargs):
        """
        Create a new VPC w/ the specified CIDR block
        """
        vpc = self.api.create_vpc(cidr_block)
        self.api.modify_vpc_attribute(
            vpc.id,
            enable_dns_support=self.enable_dns_support,
        )
        self.api.modify_vpc_attribute(
            vpc.id,
            enable_dns_hostnames=self.enable_dns_hostnames,
        )
        vpc.add_tag('Name', self.name)
        vpc.add_tag('environment', self.environment)
        return vpc

    def _destroy(self, *args, **kwargs):
        """
        Delete the VPC (does not touch dependents)
        """
        self.api.delete_vpc(self.id)

    @staticmethod
    def from_boto(vpc):
        """
        Initialize a VPC from a Boto object
        """
        return Vpc(environment=None, model=vpc)

    @classmethod
    def get_all(cls):
        """
        Fetch all VPCs associated with this account
        """
        api = cls.type_api()
        vpcs = api.get_all_vpcs()
        vpcs = [
            Vpc.from_boto(vpc)
            for vpc in vpcs
        ]
        return vpcs

    def get_all_gateways(self):
        """
        Get a list of of gateways attached to this VPC
        """
        gateways = Gateway.get_all(self)
        return gateways

    def get_all_route_tables(self):
        """
        Fetch all route tables in this VPC
        """
        route_tables = RouteTable.get_all(self)
        return route_tables

    def get_all_security_groups(self):
        """
        Fetch all security groups in this VPC
        """
        security_groups = SecurityGroup.get_all(self)
        return security_groups

    def get_all_subnets(self):
        """
        Fetch all subnets in this VPC
        """
        subnets = Subnet.get_all(self)
        return subnets

    def _get_one(self, *args, **kwargs):
        """
        Fetch exactly one VPC via name/environment
        """
        vpcs = self.api.get_all_vpcs(
            filters={
                'tag:Name': self.name,
                'tag:environment': self.environment,
            },
        )
        len_vpcs = len(vpcs)
        if len_vpcs == 1:
            vpc = vpcs[0]
        else:
            vpc = None
            if len_vpcs > 1:
                print('Found muliple matches!')
        return vpc
