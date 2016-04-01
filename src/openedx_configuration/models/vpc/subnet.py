#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Manage AWS Subnets
"""
from openedx_configuration.models.model import Model
from openedx_configuration.models.vpc.route_table import RouteTable


class Subnet(Model):
    """
    Represent an AWS Subnet
    """
    def __init__(self, environment, name, vpc, **kwargs):
        """
        Initialize a Subnet
        """
        super(Subnet, self).__init__(environment, name, **kwargs)
        self.vpc = vpc

    def _create(self, cidr_block, **kwargs):
        """
        Create a new subnet with the specified CIDR block
        """
        subnet = self.api.create_subnet(self.vpc.id, cidr_block)
        subnet.add_tag('Name', self.name)
        subnet.add_tag('environment', self.environment)
        return subnet

    def _destroy(self, *args, **kwargs):
        """
        Detach subnet from route tables and delete subnet
        """
        for route_table in self.get_route_tables():
            for association in route_table.associations:
                self.api.disassociate_route_table(association.id)
        self.api.delete_subnet(self.id)

    @staticmethod
    def from_boto(subnet, vpc):
        """
        Initialize a Subnet from a Boto object
        """
        return Subnet(environment=None, name=None, vpc=vpc, model=subnet)

    def get_route_tables(self):
        route_tables = RouteTable.get_all(subnet=self)
        return route_tables

    @classmethod
    def get_all(cls, vpc):
        """
        Fetch all Subnets associated with the VPC
        """
        api = cls.type_api()
        subnets = api.get_all_subnets(
            filters={
                'vpcId': vpc.id,
                'tag:environment': vpc.environment,
            },
        )
        subnets = [
            Subnet.from_boto(subnet, vpc)
            for subnet in subnets
        ]
        return subnets

    def _get_one(self):
        """
        Fetch exactly one Subnet via name/environment/vpc
        """
        subnets = self.api.get_all_subnets(
            filters={
                'vpcId': self.vpc.id,
                'tag:Name': self.name,
                'tag:environment': self.environment,
            },
        )
        assert len(subnets) <= 1
        if len(subnets) == 1:
            subnet = subnets[0]
        else:
            subnet = None
        return subnet
