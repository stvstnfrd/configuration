#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Manage EC2 Instances
"""
import time

import boto.ec2.instance
from boto.ec2.blockdevicemapping import BlockDeviceMapping
from boto.ec2.blockdevicemapping import BlockDeviceType
from boto.ec2.connection import EC2Connection
from boto.ec2.networkinterface import NetworkInterfaceCollection
from boto.ec2.networkinterface import NetworkInterfaceSpecification

from openedx_configuration.models.model import Model


class Instance(Model):
    """
    Represent an EC2 Instance
    """
    def __init__(self, environment, name, **kwargs):
        """
        Initialize an EC2 Instance
        """
        super(Instance, self).__init__(environment, name, **kwargs)

    @property
    def ip_address(self):
        """
        Mirror the internal object's IP address
        """
        address = getattr(self.model, 'ip_address', None)
        return address

    @property
    def public_dns_name(self):
        """
        Mirror the internal object's public DNS name
        """
        dns_name = getattr(self.model, 'public_dns_name', None)
        return dns_name

    def wait_until_ready(self):
        """
        Block while instance is `pending`
        """
        if not self.exists:
            return
        while self.state != 'running':
            print(self.state, self)
            time.sleep(5)
            self.model.update()
        print(self.state, self)

    def _get_one(self):
        """
        Fetch exactly one running instance via name/environment
        """
        state = 'running'
        instances = self.api.get_only_instances(
            filters={
                'tag:Name': self.name,
                'tag:environment': self.environment,
                # 'instance-state-name': state,
            },
        )
        instance = None
        number_of_instances = len(instances)
        if number_of_instances == 1:
            instance = instances[0]
        elif number_of_instances > 1:
            pass  # warn to STDERR
        return instance

    def _create(self, role, security_group, subnet, disk_size, ami=None, **kwargs):
        """
        Create a new EC2 instance

        Base Ubuntu Image:
        - ubuntu-precise-12.04-amd64-server-20160201
        - ami-2b2f594b
        """
        ami = ami or 'ami-2b2f594b'
        interface = NetworkInterfaceSpecification(
            associate_public_ip_address=True,
            subnet_id=subnet.id,
            groups=[
                security_group.id,
            ],
        )
        interfaces = NetworkInterfaceCollection(interface)
        block_device_map = get_block_device_map(size=disk_size)
        reservation = self.api.run_instances(
            ami,
            key_name='deployment',
            instance_type='t2.large',
            network_interfaces=interfaces,
            block_device_map=block_device_map,
        )
        instance = reservation.instances[0]
        instance.add_tag('Name', self.name)
        instance.add_tag('environment', self.environment)
        instance.add_tag('role', role)
        instance.update()
        return instance

    def _destroy(self, *args, **kwargs):
        """
        Terminate an EC2 instance
        """
        deleted_ids = self.api.terminate_instances(
            instance_ids=[
                self.id,
            ],
        )
        return len(deleted_ids) == 1

    def start(self, dry_run=True):
        instance_ids = self.api.start_instances(
            instance_ids=[
                self.id,
            ],
            dry_run=dry_run,
        )
        return len(instance_ids) == 1

    def stop(self, dry_run=True):
        instance_ids = self.api.stop_instances(
            instance_ids=[
                self.id,
            ],
            dry_run=dry_run,
        )
        return len(instance_ids) == 1

    @property
    def state(self):
        return self.model.state

def get_block_device_map(size=16, device_path='/dev/sda1'):
    """
    Generate a standard EBS device
    """
    device = BlockDeviceType(
        delete_on_termination=True,
        size=size,
    )
    device_map = BlockDeviceMapping()
    device_map[device_path] = device
    return device_map
