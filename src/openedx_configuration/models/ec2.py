import boto.ec2.instance
from boto.ec2.connection import EC2Connection
from boto.ec2.networkinterface import NetworkInterfaceCollection
from boto.ec2.networkinterface import NetworkInterfaceSpecification
connection_ec2 = EC2Connection()

class Instance(boto.ec2.instance.Instance):
    def __init__(self, environment, name, state='running', connection=None):
        super(Instance, self).__init__(connection)
        self.environment = environment
        self.name = name
        self.state = running

    def lookup(self):
        instances = connection_ec2.get_only_instances(
            filters={
                'tag:Name': self.name,
                'tag:environment': self.environment,
                'instance-state-name': self.state,
            },
        )
        instance = None
        number_of_instances = len(instances)
        if number_of_instances == 1:
            instance = instances[0]
        elif number_of_instances > 1:
            pass  # warn to STDERR
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
        reservation = connection_ec2.run_instances(
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
        instance.add_tag('Name', self.name)
        instance.add_tag('environment', self.environment)
        instance.add_tag('role', role)
        instance.update()
        return instance

    def destroy(self):
        instance_id = self.id
        deleted_ids = connection_ec2.terminate_instances(
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
