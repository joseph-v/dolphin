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

from flask import Flask


app = Flask(__name__)


# Simulate VMAX Unisphere v9.2 with following endpoints
#
# https://127.0.0.1:8199/univmax/restapi/version
# https://127.0.0.1:8199/univmax/restapi/<version>/system/symmetrix
# https://127.0.0.1:8199/univmax/restapi/<version>/system/symmetrix/<symmetrix_id>
# https://127.0.0.1:8199/univmax/restapi/<version>/sloprovisioning/symmetrix/<symmetrix_id>/srp
# https://127.0.0.1:8199/univmax/restapi/<version>/sloprovisioning/symmetrix/<symmetrix_id>/srp/<srp_id>
# https://127.0.0.1:8199/univmax/restapi/<version>/sloprovisioning/symmetrix/<symmetrix_id>/volume
# https://127.0.0.1:8199/univmax/restapi/<version>/sloprovisioning/symmetrix/<symmetrix_id>/volume/<volume_id>
# https://127.0.0.1:8199/univmax/restapi/<version>/system/symmetrix/<symmetrix_id>/director
# https://127.0.0.1:8199/univmax/restapi/<version>/system/symmetrix/<symmetrix_id>/director/<director_id>
# https://127.0.0.1:8199/univmax/restapi/<version>/system/symmetrix/<symmetrix_id>/director/<director_id>/port
# https://127.0.0.1:8199/univmax/restapi/<version>/system/symmetrix/<symmetrix_id>/director/<director_id>/port/<port_id>
#

VERSION = "/univmax/restapi/version"
ARRAY_ID = "/univmax/restapi/<version>/system/symmetrix/"
SYSTEM_ARRAY = "/univmax/restapi/<version>/system/symmetrix/<symmetrix_id>"
SLO_ARRAY = "/univmax/restapi/<version>/sloprovisioning/symmetrix/<symmetrix_id>"
SRP_LIST = "/univmax/restapi/<version>/sloprovisioning/symmetrix/<symmetrix_id>/srp"
SRP = "/univmax/restapi/<version>/sloprovisioning/symmetrix/<symmetrix_id>/srp/<srp_id>"
VOLUME_LIST = "/univmax/restapi/<version>/sloprovisioning/symmetrix/<symmetrix_id>/volume"
VOLUME = "/univmax/restapi/<version>/sloprovisioning/symmetrix/<symmetrix_id>/volume/<volume_id>"
CONTROLLER_LIST = "/univmax/restapi/<version>/system/symmetrix/<symmetrix_id>/director"
CONTROLLER = "/univmax/restapi/<version>/system/symmetrix/<symmetrix_id>/director/<director_id>"
PORT_LIST = "/univmax/restapi/<version>/system/symmetrix/<symmetrix_id>/director/<director_id>/port"
PORT = "/univmax/restapi/<version>/system/symmetrix/<symmetrix_id>/director/<director_id>/port/<port_id>"


@app.route(VERSION, methods=['GET'])
def get_version():
    version = {
        "version": "V9.2.0.1"
    }
    return version


@app.route(ARRAY_ID, methods=['GET'])
def get_array_id(version):
    if version != '92':
        print("Version in URL is wrong", version)
        return None

    array_ids = {
        # "symmetrixId": ["000196700153", "000197900256"]
        "symmetrixId": ["000196700153"]
    }
    return array_ids


@app.route(SYSTEM_ARRAY, methods=['GET'])
def get_system_array(version, symmetrix_id):
    array = {
        "symm_alert": "12/37",
        "rep_cache_usage": 0,
        "cache_partition": "Disabled",
        "service_level_rt_multiplier": "Low",
        "dynamic_rdf_config": "Enabled",
        "cache_size_mb": 858112,
        "access_control_config": "Enabled",
        "switched_rdf_config": "Enabled",
        "disk_count": 40,
        "max_hyper_per_disk": 128,
        "local": True,
        "disk_group_assignment": "In Use",
        "concurrent_dynamic_rdf_config": "Enabled",
        "spare_disk_count": 2,
        "max_dev_slot": 313205,
        "config_change_state": "Enabled",
        "model": "PowerMax_2000",
        "data_encryption": "Enabled",
        "ucode_registered_build": 0,
        "disk_service_state": "Deferred",
        "device_count": 9201,
        "last_ipl_time": "2020-09-24 07:59:54",
        "srdfa_max_throttle": 0,
        "dev_masking_aclx_config": "Mixed",
        "hot_swap_policy": "Permanent",
        "last_fast_ipl_time": "2021-02-04 14:26:04",
        "aclx_lun_addr": 0,
        "all_flash": True,
        "system_sized_property": [
            {
                "srp_name": "SRP_1",
                "sized_fba_data_reduction_ratio": "3.0:1",
                "sized_fba_capacity_tb": 183
            }
        ],
        "rdf_dir_count": 4,
        "fba_geo_emulation": "Native",
        "max_sys_slot": 6264111,
        "unconfig_disk_count": 0,
        "symmetrixId": symmetrix_id,
        "srdfa_cache_usage": 75,
        "sddf_state": "Enabled",
        "concurrent_rdf_config": "Enabled",
        "raid_config": "RAID-5 (7+1)",
        "num_ava_cache_slot": 8352148,
        "ucode_date": "02-04-2021",
        "fe_dir_count": 6,
        "be_dir_count": 4,
        "ucode": "5978.669.669",
        "pav_model": "DynamicStandardPAV",
        "pav_alias_limit": 255,
        "rdf_data_mobility_config": "Disabled"
    }
    return array


@app.route(SLO_ARRAY, methods=['GET'])
def get_sloprovisioning_array(version, symmetrix_id):
    array = {
        "symmetrixId": symmetrix_id,
        "device_count": 9137,
        "ucode": "5978.669.669",
        "model": "PowerMax_2000",
        "local": True,
        "default_fba_srp": "SRP_1",
        "system_capacity": {
            "subscribed_allocated_tb": 15.45,
            "subscribed_total_tb": 250.85,
            "snapshot_modified_tb": 0.01,
            "snapshot_total_tb": 1006.27,
            "usable_used_tb": 17.27,
            "usable_total_tb": 61.12,
            "subscribed_usable_capacity_percent": 411
        },
        "system_efficiency": {
            "overall_efficiency_ratio_to_one": 85.4,
            "data_reduction_ratio_to_one": 2.9,
            "data_reduction_enabled_percent": 7,
            "virtual_provisioning_savings_ratio_to_one": 16.3,
            "snapshot_savings_ratio_to_one": 7340204.8,
            "unreducible_data_tb": 0,
            "reducible_data_tb": 0,
            "deduplication_and_compression_savings_tb": 0,
            "pattern_detection_savings_tb": 0,
            "drr_on_reducible_only_to_one": 0
        },
        "meta_data_usage": {
            "system_meta_data_used_percent": 37,
            "replication_cache_used_percent": 0,
            "frontend_meta_data_used_percent": 21,
            "backend_meta_data_used_percent": 47
        },
        "sloCompliance": {
            "slo_stable": 364,
            "slo_marginal": 0,
            "slo_critical": 21,
            "no_slo": 285
        },
        "physicalCapacity": {
            "used_capacity_gb": 76290.38,
            "total_capacity_gb": 76290.38
        },
        "host_visible_device_count": 8800,
        "tags": "aa, Two, Three, aaa"
    }
    return array


@app.route(SRP_LIST, methods=['GET'])
def get_sloprovisioning_srps(version, symmetrix_id):
    srps = {
        "srpId": [
            "SRP_1",
        ]
    }
    return srps


@app.route(SRP, methods=['GET'])
def get_sloprovisioning_srp(version, symmetrix_id, srp_id):
    srp = {
        "srpId": srp_id,
        "num_of_disk_groups": 1,
        "description": "First SRP - FBA - not mixed",
        "emulation": "FBA",
        "reserved_cap_percent": 0,
        "total_srdf_dse_allocated_cap_gb": 0,
        "rdfa_dse": True,
        "diskGroupId": [
            "2"
        ],
        "srp_capacity": {
            "subscribed_allocated_tb": 35.66,
            "subscribed_total_tb": 347.88,
            "snapshot_modified_tb": 0,
            "snapshot_total_tb": 133.76,
            "usable_used_tb": 36.96,
            "usable_total_tb": 62.87,
            "effective_used_capacity_percent": 54
        },
        "srp_efficiency": {
            "compression_state": "Enabled",
            "overall_efficiency_ratio_to_one": 13.5,
            "data_reduction_ratio_to_one": 38.2,
            "data_reduction_enabled_percent": 0,
            "virtual_provisioning_savings_ratio_to_one": 9.8
        }
    }
    return srp


@app.route(VOLUME_LIST, methods=['GET'])
def get_sloprovisioning_volumes(version, symmetrix_id):
    volumes = {
        "expirationTime": 1574165391027,
        # "count": 2316,
        "count": 10,
        "maxPageSize": 1000,
        "id": "38082a53-4e07-4349-a160-ce75cd838ba2_0",
        "resultList": {
            "result": [
                {
                    "volumeId": "00001"
                },
                {
                    "volumeId": "00002"
                },
                {
                    "volumeId": "00003"
                },
                {
                    "volumeId": "00004"
                },
                {
                    "volumeId": "00005"
                },
                {
                    "volumeId": "00006"
                },
                {
                    "volumeId": "00007"
                },
                {
                    "volumeId": "00008"
                },
                {
                    "volumeId": "00009"
                },
                {
                    "volumeId": "0000A"
                }
            ],
            "from": 1,
            "to": 10
        }
    }
    return volumes


@app.route(VOLUME, methods=['GET'])
def get_sloprovisioning_volume(version, symmetrix_id, volume_id):
    volume = {
        "effective_wwn": "60000970000197900049533030334536",
        "pinned": False,
        "snapvx_target": False,
        "allocated_percent": 0,
        "emulation": "FBA",
        "num_of_front_end_paths": 0,
        "type": "TDEV",
        "cap_cyl": 3,
        "has_effective_wwn": False,
        "ssid": "FFFFFFFF",
        "wwn": "60000970000197900049533030334536",
        "cap_gb": 0.01,
        "reserved": False,
        "encapsulated": False,
        "num_of_storage_groups": 0,
        "volumeId": volume_id,
        "cap_mb": 6,
        "snapvx_source": False,
        "status": "Ready"
    }
    return volume


@app.route(CONTROLLER_LIST, methods=['GET'])
def get_system_directors(version, symmetrix_id):
    directors = {
        "directorId": [
            "DF-1C",
            "DF-2C",
            "DF-3C",
            "DF-4C",
            "DX-1F",
            "DX-2F",
            "DX-3F",
            "DX-4F",
            "ED-1B",
            "ED-2B",
            "ED-3B",
            "ED-4B",
            "FA-1D",
            "FA-2D",
            "FA-3D",
            "FA-4D",
            "IM-1A",
            "IM-2A",
            "IM-3A",
            "IM-4A",
            "RE-2G",
            "RF-1E",
            "RF-3E",
            "SE-2E",
            "SE-4E"
        ]
    }
    return directors


@app.route(CONTROLLER, methods=['GET'])
def get_system_director(version, symmetrix_id, director_id):
    director = {
        "availability": "ON",
        "director_number": 1,
        "director_slot_number": 10,
        "directorId": director_id,
        "num_of_ports": 2,
        "srdf_groups": [{
            "rdf_group_number": 1,
            "label": "label_1",
        }],
        "num_of_cores": 64,
    }

    return director


@app.route(PORT_LIST, methods=['GET'])
def get_system_ports(version, symmetrix_id, director_id):
    ports = {
        "symmetrixPortKey": [
            {
                "directorId": director_id,
                "portId": "30"
            },
            {
                "directorId": director_id,
                "portId": "0"
            },
            {
                "directorId": director_id,
                "portId": "1"
            },
            {
                "directorId": director_id,
                "portId": "2"
            }
        ]
    }
    return ports


@app.route(PORT, methods=['GET'])
def get_system_port(version, symmetrix_id, director_id, port_id):
    port = {
        "symmetrixPort": {
            "symmetrixPortKey": {
                "directorId": director_id,
                "portId": port_id
            },
            "port_status": "PendOn",
            "director_status": "Offline",
            "type": "GigE",
            "num_of_cores": 6,
            "num_of_port_groups": 0,
            "num_of_masking_views": 0,
            "num_of_mapped_vols": 0,
            "aclx": False,
            "common_serial_number": True,
            "volume_set_addressing": False,
            "vnx_attached": False,
            "avoid_reset_broadcast": False,
            "negotiate_reset": False,
            "enable_auto_negotiate": False,
            "environ_set": False,
            "disable_q_reset_on_ua": False,
            "soft_reset": False,
            "scsi_3": False,
            "scsi_support1": False,
            "spc2_protocol_version": False,
            "hp_3000_mode": False,
            "sunapee": False,
            "siemens": False,
            "max_speed": "10",
            "iscsi_target": False,
            "ip_addresses": [
                "192.168.0.51"
            ]
        }
    }

    return port


@app.route("/")
def default_endpoint():
    return "VMAX Simulator!"


if __name__ == '__main__':
    app.run(ssl_context='adhoc',
            host='127.0.0.1',
            port=8199)
