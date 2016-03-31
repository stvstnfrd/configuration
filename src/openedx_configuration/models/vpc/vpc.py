#!/usr/bin/env python
# -*- coding: utf-8 -*-
from boto.vpc import VPCConnection

from openedx_configuration.models.model import Model


class Vpc(Model):
    _all = None
    def __init__(self, environment, name=None, api=None, model=None, **kwargs):
        name = name or environment
        super(Vpc, self).__init__(environment, name, model=model)
        self.api = api or VPCConnection()

    @staticmethod
    def from_boto(vpc):
        return Vpc(environment=None, model=vpc)

    @staticmethod
    def all():
        api = VPCConnection()
        vpcs = api.get_all_vpcs()
        vpcs = [
            Vpc.from_boto(vpc)
            for vpc in vpcs
        ]
        return vpcs

    def _create(
            self,
            cidr_block,
            enable_dns_support=True,
            enable_dns_hostnames=True,
            **kwargs
    ):
        if self.exists:
            print('VPC already exists')
            return False
        vpc = self.api.create_vpc(cidr_block)
        self.api.modify_vpc_attribute(
            vpc.id,
            enable_dns_support=enable_dns_support,
        )
        self.api.modify_vpc_attribute(
            vpc.id,
            enable_dns_hostnames=enable_dns_hostnames,
        )
        vpc.add_tag('Name', self.name)
        vpc.add_tag('environment', self.environment)
        return vpc

    def _lookup(self, **kwargs):
        print('hi')
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

    def _destroy(self, **kwargs):
        self.api.delete_vpc(self.id)
