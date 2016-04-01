#!/usr/bin/env python
# -*- coding: utf-8 -*-


def lookup_hosted_zone(name):
    connection_route53 = Route53Connection()
    zone = connection_route53.get_zone(name)
    return zone


def create_hosted_zone(name):
    connection_route53 = Route53Connection()
    name = name + '.'
    zone = connection_route53.create_zone(name)
    return zone
