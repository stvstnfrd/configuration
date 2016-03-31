#!/usr/bin/env python
# -*- coding: utf-8 -*-
from boto.vpc import VPCConnection

from openedx_configuration.models.model import Model
from openedx_configuration.models.vpc.vpc import Vpc

class Gateway(Model):
    def __init__(self, environment, name, vpc=None, model=None, api=None, **kwargs):
        super(Gateway, self).__init__(environment, name, model)
        self.vpc = vpc or Vpc(environment)
        self.api = api or VPCConnection()

    @staticmethod
    def from_boto(gateway):
        return Gateway(environment=None, name=None, model=gateway)

    @staticmethod
    def all(vpc):
        api = VPCConnection()
        gateways = api.get_all_internet_gateways(
            filters={
                'attachment.vpc-id': vpc.id,
            },
        )
        gateways = [
            Gateway.from_boto(gateway)
            for gateway in gateways
        ]
        return gateways

    def _create(self):
        gateway = self.api.create_internet_gateway()
        gateway.add_tag('Name', self.name)
        gateway.add_tag('environment', self.environment)
        self.api.attach_internet_gateway(
            gateway.id,
            self.vpc.id
        )
        return gateway

    def _lookup(self):
        gateways = self.api.get_all_internet_gateways(
            filters={
                'attachment.vpc-id': self.vpc.id,
                'tag:Name': self.name,
                'tag:environment': self.environment,
            },
        )
        assert len(gateways) <= 1
        if len(gateways) == 1:
            gateway = gateways[0]
        else:
            gateway = None
        return gateway

    def _destroy(self):
        self.api.detach_internet_gateway(
            self.id,
            self.vpc.id
        )
        self.api.delete_internet_gateway(self.id)
