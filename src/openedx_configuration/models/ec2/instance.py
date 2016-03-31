#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

import boto.ec2.instance
from boto.ec2.blockdevicemapping import BlockDeviceMapping
from boto.ec2.blockdevicemapping import BlockDeviceType
from boto.ec2.connection import EC2Connection
from boto.ec2.networkinterface import NetworkInterfaceCollection
from boto.ec2.networkinterface import NetworkInterfaceSpecification

from openedx_configuration.models.model import Model

class Instance(Model):
    def __init__(self, environment, name, connection=None):
        self._name = name
        self.connection = connection or EC2Connection()
        super(Instance, self).__init__(environment)


    @property
    def ip_address(self):
        address = getattr(self.model, 'ip_address', None)
        return address

    @property
    def public_dns_name(self):
        dns_name = getattr(self.model, 'public_dns_name', None)
        return dns_name

    def wait_until_ready(self):
        if not self.exists:
            return
        while self.model.state == 'pending':
            print(self.model.state, self)
            time.sleep(5)
            self.model.update()

    def lookup(self, state='running'):
        instances = self.connection.get_only_instances(
            filters={
                'tag:Name': self._name,
                'tag:environment': self.environment,
                'instance-state-name': state,
            },
        )
        instance = None
        number_of_instances = len(instances)
        if number_of_instances == 1:
            instance = instances[0]
        elif number_of_instances > 1:
            pass  # warn to STDERR
        self._model = instance
        return instance

    def create(self, role, security_group_id, subnet_id, disk_size):
        interface = NetworkInterfaceSpecification(
            associate_public_ip_address=True,
            subnet_id=subnet_id,
            groups=[
                security_group_id,
            ],
        )
        interfaces = NetworkInterfaceCollection(interface)
        block_device_map = get_block_device_map(size=disk_size)
        reservation = self.connection.run_instances(
            # TEMP-sandbox-dcadams
            # 'ami-b06717d0',
            # ubuntu-precise-12.04-amd64-server-20160201
            'ami-2b2f594b',
            key_name='deployment',
            instance_type='t2.large',
            network_interfaces=interfaces,
            block_device_map=block_device_map,
        )
        instance = reservation.instances[0]
        instance.add_tag('Name', self._name)
        instance.add_tag('environment', self.environment)
        instance.add_tag('role', role)
        instance.update()
        self._model = instance
        return instance

    def destroy(self):
        instance_id = self._model.id
        deleted_ids = self.connection.terminate_instances(
            instance_ids=[
                instance_id,
            ],
        )
        return len(deleted_ids) == 1


def get_block_device_map(size=16, device_path='/dev/sda1'):
    device = BlockDeviceType(
        delete_on_termination=True,
        size=size,
    )
    device_map = BlockDeviceMapping()
    device_map[device_path] = device
    return device_map
