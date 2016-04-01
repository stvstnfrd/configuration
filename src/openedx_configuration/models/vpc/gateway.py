#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Manage AWS Internet Gateways
"""
from openedx_configuration.models.model import Model


class Gateway(Model):
    """
    Represent an AWS Internet Gateway
    """
    def __init__(self, environment, name, vpc, **kwargs):
        """
        Initialize a gateway
        """
        super(Gateway, self).__init__(environment, name, **kwargs)
        self.vpc = vpc

    def _create(self, *args, **kwargs):
        """
        Create a new gateway and attach it to the VPC
        """
        gateway = self.api.create_internet_gateway()
        gateway.add_tag('Name', self.name)
        gateway.add_tag('environment', self.environment)
        self.api.attach_internet_gateway(
            gateway.id,
            self.vpc.id
        )
        return gateway

    def _destroy(self, *args, **kwargs):
        """
        Detach from the VPC and delete the gateway
        """
        self.api.detach_internet_gateway(
            self.id,
            self.vpc.id
        )
        self.api.delete_internet_gateway(self.id)

    @staticmethod
    def from_boto(gateway, vpc):
        """
        Initialize a gateway from a Boto object
        """
        return Gateway(environment=None, name=None, vpc=vpc, model=gateway)

    @classmethod
    def get_all(cls, vpc):
        """
        Find all gateways associated with the VPC
        """
        api = cls.type_api()
        gateways = api.get_all_internet_gateways(
            filters={
                'attachment.vpc-id': vpc.id,
            },
        )
        gateways = [
            Gateway.from_boto(gateway, vpc)
            for gateway in gateways
        ]
        return gateways

    def _get_one(self):
        """
        Find exactly one Gateway via name/environment/vpc
        """
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
