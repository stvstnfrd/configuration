#!/usr/bin/env python
# -*- coding: utf-8 -*-
from boto.vpc import VPCConnection

from openedx_configuration.models.model import Model


class Vpc(Model):
    def __init__(self, environment, cidr_block, api_connection=None):
        self.cidr_block = cidr_block
        self.api = api_connection or VPCConnection()
        super(Vpc, self).__init__(environment)

    def create(self):
        if self.exists:
            print('VPC already exists')
            return False
        api = self.api
        cidr_block = self.cidr_block
        environment = self.environment
        vpc = api.create_vpc(cidr_block)
        api.modify_vpc_attribute(vpc.id, enable_dns_support=True)
        api.modify_vpc_attribute(vpc.id, enable_dns_hostnames=True)
        vpc.add_tag('Name', environment)
        vpc.add_tag('environment', environment)
        self._model = vpc
        return True

    def destroy(self):
        vpc = self._model
        vpc_id = vpc.id
        success = self.api.delete_vpc(vpc_id)
        self._model = False
        return success

    def fetch(self):
        environment = self.environment
        api = self.api
        cidr_block = self.cidr_block
        vpcs = api.get_all_vpcs(
            filters={
                'cidrBlock': cidr_block,
                'tag:Name': environment,
                'tag:environment': environment,
            },
        )
        len_vpcs = len(vpcs)
        if len_vpcs == 1:
            vpc = vpcs[0]
        else:
            vpc = None
            if len_vpcs > 1:
                print('Found muliple matches!')
        self._model = vpc
        return self
