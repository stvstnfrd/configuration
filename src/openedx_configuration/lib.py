#!/usr/bin/env python
# TODO: add tags to network_acl
from boto.ec2.connection import EC2Connection
from boto.route53.connection import Route53Connection
from boto.vpc import VPCConnection

from openedx_configuration.models.vpc.vpc import Vpc


PUBLIC_CIDR_BLOCK = '0.0.0.0/0'


