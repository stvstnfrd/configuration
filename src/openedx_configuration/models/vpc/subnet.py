#!/usr/bin/env python
# -*- coding: utf-8 -*-
from boto.vpc import VPCConnection

from openedx_configuration.models.model import Model
from openedx_configuration.models.vpc.vpc import Vpc

class Subnet(Model):
    def __init__(self, environment, name, vpc=None, model=None, api=None):
        super(Subnet, self).__init__(environment, name, model)
        self.vpc = vpc or Vpc(environment)
        self.api = api or VPCConnection()

    @staticmethod
    def from_boto(subnet):
        return Subnet(environment=None, name=None, model=subnet)

    @staticmethod
    def all(vpc):
        api = VPCConnection()
        subnets = api.get_all_subnets(
            filters={
                'vpcId': vpc.id,
            },
        )
        subnets = [
            Subnet.from_boto(subnet)
            for subnet in subnets
        ]
        return subnets

    def _create(self, cidr_block):
        subnet = self.api.create_subnet(self.vpc.id, cidr_block)
        subnet.add_tag('Name', self.name)
        subnet.add_tag('environment', self.environment)
        return subnet

    def _lookup(self):
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

    def _destroy(self):
        self.api.delete_subnet(self.id)
