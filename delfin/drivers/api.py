# Copyright 2020 The SODA Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import six

from oslo_log import log
from oslo_utils import uuidutils

from delfin import db
from delfin.common import constants
from delfin import cryptor
from delfin.drivers import helper
from delfin.drivers import manager

LOG = log.getLogger(__name__)


class API(object):
    def __init__(self):
        self.driver_manager = manager.DriverManager()

    def discover_storage(self, context, access_info):
        """Discover a storage system with access information."""
        helper.encrypt_password(context, access_info)
        if 'storage_id' not in access_info:
            access_info['storage_id'] = six.text_type(
                uuidutils.generate_uuid())

        driver = self.driver_manager.get_driver(context,
                                                cache_on_load=False,
                                                **access_info)
        storage = driver.get_storage(context)

        # Need to validate storage response from driver
        helper.check_storage_repetition(context, storage)
        access_info = db.access_info_create(context, access_info)
        storage['id'] = access_info['storage_id']
        storage = db.storage_create(context, storage)

        LOG.info("Storage found successfully.")
        return storage

    def discover_storages(self, context, access_info):
        """Discover a centralized_manager system with access information."""
        print("------CM-------: In discover cm")
        helper.encrypt_password(context, access_info)
        if 'storage_id' not in access_info:
            cm_id = six.text_type(uuidutils.generate_uuid())
            access_info['storage_id'] = cm_id
        encode_str = access_info["vendor"] + access_info["model"]
        access_rest = access_info.get('rest')
        access_ssh = access_info.get('ssh')
        access_smis = access_info.get('smis')
        for access in [access_rest, access_ssh, access_smis]:
            if access:
                encode_str = encode_str +\
                             access["host"] +\
                             str(access["port"])
        print("------CM-------: encode_str ", encode_str)
        cm = {
            "id": cm_id,
            "derived_id": cryptor.encode(encode_str),
            "vendor": access_info["vendor"],
            "model": access_info["model"],
            "resources": {
                "storages": None
            }
        }
        print("------CM-------: call helper for cm repeatation", cm)

        helper.check_cm_repetition(context, cm)

        driver = self.driver_manager.get_driver(context,
                                                cache_on_load=False,
                                                **access_info)
        storages = driver.get_storages(context)

        # Need to validate storages response from driver
        storages_list = []
        for storage in storages:
            helper.check_storage_repetition(context, storage)
            storage['id'] = six.text_type(
                uuidutils.generate_uuid())
            access_info['storage_id'] = storage['id']
            db.access_info_create(context, access_info)
            storage_ret = db.storage_create(context, storage)
            storages_list.append(storage_ret)
        LOG.info("Storages from Centralized Mgr found successfully.")
        access_info['storage_id'] = cm_id
        db.access_info_create(context, access_info)
        cm['resources']['storages'] = storages
        cm = db.centralized_manager_create(context, cm)
        return cm

    def update_access_info(self, context, access_info):
        """Validate and update access information."""
        helper.encrypt_password(context, access_info)
        driver = self.driver_manager.get_driver(context,
                                                cache_on_load=False,
                                                **access_info)
        storage_new = driver.get_storage(context)

        # Need to validate storage response from driver
        storage_id = access_info['storage_id']
        helper.check_storage_consistency(context, storage_id, storage_new)
        access_info = db.access_info_update(context, storage_id, access_info)
        db.storage_update(context, storage_id, storage_new)

        LOG.info("Access information updated successfully.")
        return access_info

    def remove_storage(self, context, storage_id):
        """Clear driver instance from driver factory."""
        self.driver_manager.remove_driver(storage_id)

    def get_storage(self, context, storage_id):
        """Get storage device information from storage system"""
        driver = self.driver_manager.get_driver(context, storage_id=storage_id)
        return driver.get_storage(context)

    def list_storage_pools(self, context, storage_id):
        """List all storage pools from storage system."""
        driver = self.driver_manager.get_driver(context, storage_id=storage_id)
        return driver.list_storage_pools(context)

    def list_volumes(self, context, storage_id):
        """List all storage volumes from storage system."""
        driver = self.driver_manager.get_driver(context, storage_id=storage_id)
        return driver.list_volumes(context)

    def list_controllers(self, context, storage_id):
        """List all storage controllers from storage system."""

        driver = self.driver_manager.get_driver(context, storage_id=storage_id)
        return driver.list_controllers(context)

    def list_ports(self, context, storage_id):
        """List all ports from storage system."""

        driver = self.driver_manager.get_driver(context, storage_id=storage_id)
        return driver.list_ports(context)

    def list_disks(self, context, storage_id):
        """List all disks from storage system."""
        driver = self.driver_manager.get_driver(context, storage_id=storage_id)
        return driver.list_disks(context)

    def list_quotas(self, context, storage_id):
        """List all quotas from storage system."""
        driver = self.driver_manager.get_driver(context, storage_id=storage_id)
        return driver.list_quotas(context)

    def list_filesystems(self, context, storage_id):
        """List all filesystems from storage system."""
        driver = self.driver_manager.get_driver(context, storage_id=storage_id)
        return driver.list_filesystems(context)

    def list_qtrees(self, context, storage_id):
        """List all qtrees from storage system."""
        driver = self.driver_manager.get_driver(context, storage_id=storage_id)
        return driver.list_qtrees(context)

    def list_shares(self, context, storage_id):
        """List all shares from storage system."""
        driver = self.driver_manager.get_driver(context, storage_id=storage_id)
        return driver.list_shares(context)

    def add_trap_config(self, context, storage_id, trap_config):
        """Config the trap receiver in storage system."""
        pass

    def remove_trap_config(self, context, storage_id, trap_config):
        """Remove trap receiver configuration from storage system."""
        pass

    def parse_alert(self, context, storage_id, alert):
        """Parse alert data got from snmp trap server."""
        access_info = db.access_info_get(context, storage_id)
        driver = self.driver_manager.get_driver(context,
                                                invoke_on_load=False,
                                                **access_info)
        return driver.parse_alert(context, alert)

    def clear_alert(self, context, storage_id, sequence_number):
        """Clear alert from storage system."""
        driver = self.driver_manager.get_driver(context, storage_id=storage_id)
        driver.clear_alert(context, sequence_number)

    def list_alerts(self, context, storage_id, query_para=None):
        """List alert from storage system."""
        driver = self.driver_manager.get_driver(context, storage_id=storage_id)
        return driver.list_alerts(context, query_para)

    def collect_perf_metrics(self, context, storage_id,
                             resource_metrics, start_time, end_time):

        """Collect performance metrics"""
        driver = self.driver_manager.get_driver(context,
                                                storage_id=storage_id)
        return driver.collect_perf_metrics(context, storage_id,
                                           resource_metrics, start_time,
                                           end_time)

    def get_capabilities(self, context, storage_id,):
        """Get capabilities from supported driver"""
        driver = self.driver_manager.get_driver(context, storage_id=storage_id)
        return driver.get_capabilities(context)
