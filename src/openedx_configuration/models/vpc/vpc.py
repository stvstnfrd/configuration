#!/usr/bin/env python
# -*- coding: utf-8 -*-
from openedx_configuration.models.model import Model
from openedx_configuration.models.ec2.security_group import SecurityGroup
from openedx_configuration.models.vpc.gateway import Gateway
from openedx_configuration.models.vpc.route_table import RouteTable
from openedx_configuration.models.vpc.subnet import Subnet


class Vpc(Model):
    enable_dns_support = True
    enable_dns_hostnames = True

    def __init__(self, environment, name=None, **kwargs):
        """
        Initialize a new VPC

        Ideally, `environment` and `name` would always be equal.
        The terms `environment` and `VPC` should be considered generally
        interchangeable; the latter being an implementation of the
        former concept.
        """
        name = name or environment
        super(Vpc, self).__init__(environment, name, **kwargs)

    def get_gateways(self):
        gateways = Gateway.get_all(self)
        return gateways

    def get_subnets(self):
        subnets = Subnet.get_all(self)
        return subnets

    def get_security_groups(self):
        security_groups = SecurityGroup.get_all(self)
        return security_groups

    def get_route_tables(self):
        route_tables = RouteTable.get_all(self)
        return route_tables

    @staticmethod
    def from_boto(vpc):
        return Vpc(environment=None, model=vpc)

    @classmethod
    def get_all(cls):
        api = cls.type_api()
        vpcs = api.get_all_vpcs()
        vpcs = [
            Vpc.from_boto(vpc)
            for vpc in vpcs
        ]
        return vpcs

    def _create(self, cidr_block, *args, **kwargs):
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
        self.api.delete_vpc(self.id)

    def _get_one(self, *args, **kwargs):
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
