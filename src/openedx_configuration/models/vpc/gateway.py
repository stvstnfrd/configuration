#!/usr/bin/env python
# -*- coding: utf-8 -*-
from boto.vpc import VPCConnection

from openedx_configuration.models.model import Model

class Gateway(Model):
    def __init__(self, vpc, name=None, api_connection=None):
        self.api = api_connection or VPCConnection()
        self.vpc = vpc
        self._name = name or self._generate_name()
        environment = vpc.tags.get('environment')
        super(Gateway, self).__init__(environment)

    def create(self):
        vpc = self.vpc.model
        vpc_id = vpc.id
        name = self._name
        environment = vpc.tags['environment']
        gateway = self.api.create_internet_gateway()
        success = gateway.add_tag('Name', name)
        success = gateway.add_tag('environment', environment)
        success = self.api.attach_internet_gateway(
            gateway.id,
            vpc_id
        )
        self._model = gateway
        return gateway

    def destroy(self):
        print('noop')

    def fetch(self):
        vpc_id = self.vpc.model.id
        gateways = self.api.get_all_internet_gateways(
            filters={
                'attachment.vpc-id': vpc_id,
            },
        )
        assert len(gateways) <= 1
        if len(gateways) == 1:
            gateway = gateways[0]
        else:
            gateway = None
        self._model = gateway
        return self

    # sandbox-internet
    def _generate_name(self):
        name_vpc = self.vpc.name
        name = "{vpc}-internet".format(
            vpc=name_vpc,
        )
        return name
