# Copyright 2021 The SODA Authors.
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
import copy

from oslo_log import log
# from oslo_utils import timeutils

from delfin import db
from delfin.api import api_utils
from delfin.api.common import wsgi
from delfin.api.v1.storages import \
    create_performance_monitoring_task, set_synced_if_ok
from delfin.api.views import storage_pools as storage_pool_view
from delfin.api import validation
from delfin.api.schemas import storages as schema_storages
from delfin.common import constants
from delfin.i18n import _
from delfin import coordination
from delfin import exception
from delfin.api.views import centralized_managers as cm_view
from delfin.drivers import api as driverapi
from delfin.task_manager.tasks import resources
from delfin.task_manager import rpcapi as task_rpcapi
from delfin.task_manager.tasks import telemetry as task_telemetry

LOG = log.getLogger(__name__)


class CentralizedManagerController(wsgi.Controller):
    def __init__(self):
        super(CentralizedManagerController, self).__init__()
        self.task_rpcapi = task_rpcapi.TaskAPI()
        self.driver_api = driverapi.API()
        self.search_options = ['driver_id', 'name', 'vendor',
                               'model', 'status', 'serial_number']

    def _get_cms_search_options(self):
        """Return storage_pools search options allowed ."""
        return self.search_options

    def _storage_exist(self, context, access_info):
        access_info_dict = copy.deepcopy(access_info)

        # Remove unrelated query fields
        unrelated_fields = ['username', 'password']
        for access in constants.ACCESS_TYPE:
            if access_info_dict.get(access):
                for key in unrelated_fields:
                    access_info_dict[access].pop(key)

        # Check if storage is registered
        access_info_list = db.access_info_get_all(context,
                                                  filters=access_info_dict)
        for _access_info in access_info_list:
            try:
                cm = db.storage_get(context, _access_info['driver_id'])
                if cm:
                    LOG.error("CM %s has same access "
                              "information." % cm['driver_id'])
                    return True
                storage = db.storage_get(context, _access_info['storage_id'])
                if storage:
                    LOG.error("Storage %s has same access "
                              "information." % storage['id'])
                    return True
            except exception.StorageNotFound:
                # Suppose storage was not saved successfully after access
                # information was saved in database when registering storage.
                # Therefore, removing access info if storage doesn't exist to
                # ensure the database has no residual data.
                LOG.debug("Remove residual access information.")
                db.access_info_delete(context, _access_info['storage_id'])

        return False

    def show(self, req, id):
        ctxt = req.environ['delfin.context']
        cm = db.centralized_manager_get(ctxt, id)
        return cm_view.build_centralized_manager(cm)

    def index(self, req):
        ctxt = req.environ['delfin.context']
        query_params = {}
        query_params.update(req.GET)
        # update options  other than filters
        sort_keys, sort_dirs = api_utils.get_sort_params(query_params)
        marker, limit, offset = api_utils.get_pagination_params(query_params)
        # strip out options except supported search  options
        api_utils.remove_invalid_options(ctxt, query_params,
                                         self._get_cms_search_options())

        cms = db.centralized_manager_get_all(ctxt, marker, limit, sort_keys,
                                             sort_dirs, query_params, offset)
        return cm_view.build_centralized_managers(cms)

    @wsgi.response(201)
    @validation.schema(schema_storages.create)
    def create(self, req, body):
        """Register a new storage device."""
        ctxt = req.environ['delfin.context']
        access_info_dict = body
        print("------CM-------: CREATE ")

        # Lock to avoid synchronous creating.
        for access in constants.ACCESS_TYPE:
            if access_info_dict.get(access) is not None:
                host = access_info_dict.get(access).get('host')
                break
        lock_name = 'storage-create-' + host
        lock = coordination.Lock(lock_name)

        with lock:
            if self._storage_exist(ctxt, access_info_dict):
                raise exception.CMAlreadyExists()
            cm = self.driver_api.discover_storages(ctxt,
                                                   access_info_dict)

        # Registration success, sync resource collection for this storage
        storages = cm['resources']['storages']
        print('---------------CM----------storages', storages)
        for storage in storages:
            try:
                self.sync(req, storage['id'])

                # Post registration, trigger alert sync
                self.task_rpcapi.sync_storage_alerts(ctxt, storage['id'],
                                                     query_para=None)
            except Exception as e:
                # Unexpected error occurred, while syncing resources.
                msg = _('Failed to sync resources for storage: %(storage)s. '
                        'Error: %(err)s') % \
                      {'storage': storage['id'], 'err': e}
                LOG.error(msg)

            try:
                # Trigger Performance monitoring
                capabilities = self.driver_api.get_capabilities(
                    context=ctxt, storage_id=storage['id'])
                validation.validate_capabilities(capabilities)
                create_performance_monitoring_task(ctxt, storage['id'],
                                                   capabilities)
            except exception.EmptyResourceMetrics:
                msg = _("Resource metric provided by "
                        "capabilities is empty for "
                        "storage: %s") % storage['id']
                LOG.info(msg)
            except Exception as e:
                # Unexpected error occurred, while performance monitoring.
                msg = _('Failed to trigger performance '
                        'monitoring for storage: '
                        '%(storage)s. Error: %(err)s') \
                      % {'storage': storage['id'], 'err': six.text_type(e)}
                LOG.error(msg)
        return cm_view.build_centralized_manager(cm)

    @wsgi.response(202)
    def delete(self, req, id):
        ctxt = req.environ['delfin.context']
        print("------CM-------: DELETE ")
        cm = db.centralized_manager_get(ctxt, id)
        for storage in cm['resources']['storages']:
            for subclass in resources.StorageResourceTask.__subclasses__():
                self.task_rpcapi.remove_storage_resource(
                    ctxt,
                    storage['id'],
                    subclass.__module__ + '.' + subclass.__name__)

            for subclass in task_telemetry.TelemetryTask.__subclasses__():
                self.task_rpcapi.remove_telemetry_instances(ctxt,
                                                            storage['id'],
                                                            subclass.__module__ +
                                                            '.'
                                                            + subclass.__name__)
            self.task_rpcapi.remove_storage_in_cache(ctxt, storage['id'])

    @wsgi.response(202)
    def sync_all(self, req):
        """
        :param req:
        :return: it's a Asynchronous call. so return 202 on success. sync_all
        api performs the storage device info, storage_pool,
         volume etc. tasks on each registered storage device.
        """
        ctxt = req.environ['delfin.context']

        storages = db.storage_get_all(ctxt)
        LOG.debug("Total {0} registered storages found in database".
                  format(len(storages)))
        resource_count = len(resources.StorageResourceTask.__subclasses__())

        for storage in storages:
            try:
                set_synced_if_ok(ctxt, storage['id'], resource_count)
            except exception.InvalidInput as e:
                LOG.warn('Can not start new sync task for %s, reason is %s'
                         % (storage['id'], e.msg))
                continue
            else:
                for subclass in \
                        resources.StorageResourceTask.__subclasses__():
                    self.task_rpcapi.sync_storage_resource(
                        ctxt,
                        storage['id'],
                        subclass.__module__ + '.' + subclass.__name__)

    @wsgi.response(202)
    def sync(self, req, id):
        """
        :param req:
        :param id:
        :return:
        """
        print("------CM-------: SYNC ")
        ctxt = req.environ['delfin.context']
        storage = db.storage_get(ctxt, id)
        resource_count = len(resources.StorageResourceTask.__subclasses__())
        set_synced_if_ok(ctxt, storage['id'], resource_count)
        for subclass in resources.StorageResourceTask.__subclasses__():
            self.task_rpcapi.sync_storage_resource(
                ctxt,
                storage['id'],
                subclass.__module__ + '.' + subclass.__name__)


def create_resource():
    return wsgi.Resource(CentralizedManagerController())
