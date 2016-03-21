#!/usr/bin/env python
# -*- coding: utf-8 -*-
from boto.vpc import VPCConnection


class Vpc(object):
    def __init__(self, environment, cidr_block, api_connection):
        self.environment = environment
        self.cidr_block = cidr_block
        self.api = api_connection or VPCConnection()
        self.__model = None

    def all(self):
        pass

    def __repr__(self):
        return unicode(self._model)

    def create(cidr_block):
        environment = self.environment
        cidr_block = self.cidr_block
        api = self.api
        vpc = api.create_vpc(cidr_block)
        api.modify_vpc_attribute(vpc.id, enable_dns_support=True)
        api.modify_vpc_attribute(vpc.id, enable_dns_hostnames=True)
        success = vpc.add_tag('Name', environment)
        success = vpc.add_tag('environment', environment)
        return vpc


    def destroy(self):
        model = self._model
        vpc_id = model.id
        api = self.api
        success = api.delete_vpc(vpc_id)
        return success

    def _model(self):
        model = self._update()
        self.__model = model
        return model

    def _update(self):
        environment = self.environment
        api = self.api
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
        return vpc
