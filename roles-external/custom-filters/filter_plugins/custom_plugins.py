__author__ = 'jez'

import collections
import hashlib
import re


class FilterModule(object):
    ''' Custom filters are loaded by FilterModule objects '''

    def filters(self):
        ''' FilterModule objects return a dict mapping filter names to
            filter functions. '''
        return {
            'sha256': self.sha256,
            'split': self.split,
            'slugify': self.slugify,
            'app_versions_string': self.app_versions_string,
            'app_versions_all_latest': self.app_versions_all_latest,
            'contains': self.contains,
            'ec2_elb_dns_name': self.ec2_elb_dns_name,
            'ec2_security_group_id': self.ec2_security_group_id,
            'ec2_security_group_ids': self.ec2_security_group_ids,
            'ec2_security_group_ids_all': self.ec2_security_group_ids_all,
            'ec2_subnet_id': self.ec2_subnet_id,
            'ec2_subnet_ids': self.ec2_subnet_ids,
            'ec2_subnet_ids_all': self.ec2_subnet_ids_all,
            'ec2_ami_id': self.ec2_ami_id,
            'ec2_ami_first_id': self.ec2_ami_first_id,
            'ec2_instance_private_dns': self.ec2_instance_private_dns,
            'ec2_instance_private_ip': self.ec2_instance_private_ip,
        }

    def split(self, value, delimiter):
        return value.split(delimiter)

    def slugify(self, text):
        return text.replace('-', '_')

    def app_version_string(self, app_package):
        return app_package['name'] + "=" + app_package['version']

    def app_versions_string(self, app_packages):
        if isinstance(app_packages, collections.Iterable):
            app_packages_sorted = sorted(app_packages, key=lambda k: k['name'])
            versions_string = "|".join(map(self.app_version_string, app_packages_sorted))
        else:
            versions_string = self.app_version_string(app_packages)

        return versions_string

    def app_versions_all_latest(self, app_packages):
        app_packages_latest = filter(lambda app: app['version'] == 'latest', app_packages)
        return len(app_packages_latest) == len(app_packages)

    def sha256(self, plain_text):
        hash_object = hashlib.sha256(plain_text)
        return hash_object.hexdigest()

    def contains(self, value, regex):
        return re.search(regex, value) is not None

    def ec2_elb_dns_name(self, value, elb_name):

        dns_name = ''

        for elb in value:
            if elb['item']['name'] == elb_name:
                dns_name = elb['elb']['dns_name']
                break

        return dns_name

    def ec2_security_group_id(self, value, security_group_name):

        group_id = ''

        for sg in value:
            if sg['item']['name'] == security_group_name:
                group_id = sg['group_id']
                break

        return group_id

    def ec2_security_group_ids(self, value, security_group_names):

        return [sg['group_id'] for sg in value if sg['item']['name'] in security_group_names]

    def ec2_security_group_ids_all(self, value):

        return [sg['group_id'] for sg in value]

    def ec2_subnet_id(self, value, subnet_name):

        subnet_id = ''

        for subnet in value:
            if subnet['item']['item']['name'] == subnet_name:
                subnet_id = subnet['subnet']['id']
                break

        return subnet_id

    def ec2_subnet_ids(self, value, subnet_names):

        return [subnet['subnet']['id'] for subnet in value if subnet['item']['item']['name'] in subnet_names]

    def ec2_subnet_ids_all(self, value):

        return [subnet['id'] for subnet in value]

    def ec2_ami_id(self, value, ami_name):

        print(ami_name)
        ami_id = ''

        for ami in value:
            if ami['item']['item']['item']['name'].startswith(ami_name):
                ami_id = ami['image_id']
                break

        return ami_id

    def ec2_ami_first_id(self, value):

        return value[0].get('image_id', None)


    def ec2_instance_private_dns(self, value, instance_name):

        return [str(instance['instances'][0]['private_dns_name']) for instance in value if instance['item']['name'] == instance_name]

    def ec2_instance_private_ip(self, value, instance_name):

        return [instance['instances'][0]['private_ip'] for instance in value if instance['item']['name'] == instance_name]
