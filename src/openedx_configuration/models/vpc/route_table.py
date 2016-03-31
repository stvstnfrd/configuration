#!/usr/bin/env python
# -*- coding: utf-8 -*-
from boto.exception import EC2ResponseError

from openedx_configuration.models.model import Model


class RouteTable(Model):
    def __init__(self, environment, name, subnet, **kwargs):
        super(RouteTable, self).__init__(environment, name, **kwargs)
        self.subnet = subnet

    @staticmethod
    def from_boto(route_table):
        return RouteTable(environment=None, name=None, subnet=None, model=route_table)

    @classmethod
    def get_all(cls, vpc=None, subnet=None):
        api = cls.type_api()
        filters = {}
        if vpc:
            filters['vpc-id'] = vpc.id
            filters['tag:environment'] = vpc.environment
        if subnet:
            filters['association.subnet-id'] = subnet.id
            filters['tag:environment'] = subnet.environment
        route_tables = api.get_all_route_tables(
            filters=filters,
        )
        route_tables = [
            RouteTable.from_boto(route_table)
            for route_table in route_tables
        ]
        return route_tables

    def _get_one(self):
        environment = self.environment
        route_tables = self.api.get_all_route_tables(
            filters={
                # 'association.subnet-id': self.subnet.id,
                'tag:Name': self.name,
                'tag:environment': environment,
                # 'vpc-id': self.subnet.vpc.id,
            },
        )
        assert len(route_tables) <= 1
        if len(route_tables) == 1:
            route_table = route_tables[0]
        else:
            route_table = None
        return route_table

    def _create(self, gateway_id, cidr_block, *args, **kwargs):
        subnet_id = self.subnet.model.id
        vpc = self.subnet.vpc.model
        environment = vpc.tags['environment']
        environment = self.environment
        route_table = self.api.create_route_table(vpc.id)
        route_table.add_tag('Name', self.name)
        route_table.add_tag('environment', environment)
        self.api.create_route(
            route_table.id,
            cidr_block,
            gateway_id=gateway_id,
        )
        association_id = self.api.associate_route_table(route_table.id, subnet_id)
        return route_table

    def _destroy(self, *args, **kwargs):
        route_table = self.model
        for association in route_table.associations:
            self.api.disassociate_route_table(association.id)
        for route in route_table.routes:
            try:
                self.api.delete_route(
                    route_table.id,
                    route.destination_cidr_block,
                )
            except EC2ResponseError:
                pass
        self.api.delete_route_table(route_table.id)
