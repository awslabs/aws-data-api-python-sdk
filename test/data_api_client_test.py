import sys
import os
import unittest
import shortuuid
import json

sys.path.append("..")
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir)

import src.parameters as params
from src.lib.data_api_control_plane import DataApiControlPlane
from src.exceptions import *
from src.data_api_client import DataAPIClient

data_type = "MyItem"
_item_id = "1234567890"
_master_id = "9999999999"
_log_level = 'INFO'
_uuid = shortuuid.uuid()
_resource = {params.RESOURCE: {"attr1": "abc", "attr2": "xyz", "attr3": _uuid}}
_metadata = {params.METADATA: {"meta1": "abc", "meta2": "xyz", "meta3": _uuid}}


class DataAPIClientTest(unittest.TestCase):
    client = None

    @classmethod
    def setUpClass(cls):
        region = os.getenv("AWS_REGION")

        if region is None:
            raise Exception("Must configure AWS_REGION environment variable")

        # bootstrapping the control plane
        control_plane = DataApiControlPlane(tls=True, region_name=region)
        access_key = None
        secret_key = None
        session_token = None

        a = "aws_access_key_id"
        if os.getenv(a) is not None:
            access_key = os.getenv(a)

        s = "aws_secret_access_key"
        if os.getenv(s) is not None:
            secret_key = os.getenv(s)

        t = "aws_session_token"
        if os.getenv(t) is not None:
            session_token = os.getenv(t)

        endpoint = os.getenv("API_ENDPOINT")
        if endpoint is None:
            raise Exception("Unable to connect to API Endpoint without environment variable API_ENDPOINT")

        control_plane.connect(from_url=endpoint,
                              access_key=access_key,
                              secret_key=secret_key,
                              session_token=session_token,
                              force_refresh=True)

        global _log_level
        set_logging = os.getenv('LOG_LEVEL')
        if set_logging is not None:
            _log_level = set_logging

        # create an API client in Dev stage
        cls.client = DataAPIClient(stage="dev", region_name=region, log_level=_log_level)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.client.delete_resource(data_type=data_type, item_id=_item_id, delete_mode=params.DELETE_MODE_SOFT)
        except ResourceNotFoundException:
            pass

        try:
            cls.client.delete_resource(data_type=data_type, item_id=_master_id, delete_mode=params.DELETE_MODE_SOFT)
        except ResourceNotFoundException:
            pass

    def _create_base_item(self, data_type: str, item_id: str):
        self.client.put_resource(data_type=data_type, item_id=item_id, resource=_resource,
                                 strict_schema=True)
        self.client.put_metadata(data_type=data_type, item_id=item_id, meta=_metadata, strict_schema=True)

    def setUp(self):
        try:
            self.client.remove_item_master(data_type=data_type, item_id=_item_id, item_master_id=_master_id)
        except ResourceNotFoundException:
            pass

        self._create_base_item(data_type=data_type, item_id=_item_id)

    def tearDown(self):
        try:
            self.client.delete_schema(data_type=data_type, schema_type=params.RESOURCE)
            self.client.delete_schema(data_type=data_type, schema_type=params.METADATA)
        except ResourceNotFoundException:
            pass

    def test_namespaces(self):
        namespaces = self.client.get_namespaces()
        self.assertIsNotNone(namespaces)

    def test_delete_attributes(self):
        d = "DataModified"

        def _do_update(attrs):
            update = self.client.delete_attributes(data_type=data_type, item_id=_item_id, resource_attributes=attrs)
            if d in update:
                return update.get(d)
            else:
                raise Exception(f"Unable to resolve expected response element {d}")

        self.assertTrue(_do_update(["attr3"]))

        # now load the object and determine that attr3 is gone
        item = self.client.get_resource(data_type=data_type, item_id=_item_id)
        self.assertIsNotNone(item)
        self.assertIsNone(item.get("attr3", None))

    def test_delete_resource(self):
        deletion = self.client.delete_resource(data_type=data_type, item_id=_item_id, delete_mode="soft").get(
            "DataModified")
        self.assertTrue(deletion)

        # now check that I can't fetch it
        with self.assertRaises(ResourceNotFoundException):
            item = self.client.get_resource(data_type=data_type, item_id=_item_id)

    def test_delete_metadata(self):
        self.assertTrue(self.client.delete_metadata(data_type=data_type, item_id=_item_id).get("DataModified"))

        # now check that I can't fetch metadata
        meta = self.client.get_metadata(data_type=data_type, item_id=_item_id)
        self.assertIsNone(meta)

    def _put_schema(self, schema_type):
        with open(f"test_{schema_type.lower()}_schema.json", 'r') as f:
            json_schema = json.load(f)

        # test that I can create the schema
        self.assertTrue(self.client.put_schema(data_type=data_type, schema_type=schema_type, json_schema=json_schema))

        return json_schema

    def _test_schema_type(self, schema_type):
        put_schema = self._put_schema(schema_type)

        # test that I can get the schema
        fetch_schema = self.client.get_schema(data_type=data_type, schema_type=schema_type)
        self.assertIsNotNone(fetch_schema)

        # assert that the schemas match
        self.assertEqual(put_schema, fetch_schema)

        # test that I can delete the schema
        deletion = self.client.delete_schema(data_type=data_type, schema_type=schema_type)
        self.assertEqual(True, deletion.get("DataModified", False))
        self.assertIsNone(self.client.get_schema(data_type=data_type, schema_type=schema_type))

    def test_schemas(self):
        self._test_schema_type(params.RESOURCE)
        self._test_schema_type(params.METADATA)

    def test_find_item(self):
        results = self.client.find(data_type=data_type, resource_attributes={"attr3": _uuid})
        self.assertIsNotNone(results)
        self.assertIsNotNone(results.get("Items"))
        self.assertEqual(len(results.get("Items")), 1)
        self.assertEqual(results.get("Items")[0].get("id"), _item_id)

        n = 10

        # find with index
        _id = "value1-1088"
        results = self.client.find(data_type=data_type, resource_attributes={"attr1": _id})
        self.assertIsNotNone(results)
        self.assertEqual(len(results.get("Items")), 1)
        self.assertEqual(results.get("Items")[0].get("attr1"), _id)

        # find with limit
        results = self.client.find(data_type=data_type, resource_attributes={"attr3": _uuid}, limit=n)
        self.assertIsNotNone(results)
        self.assertEqual(len(results.get("Items")), 1)
        self.assertEqual(results.get("Items")[0].get("id"), _item_id)

        results = self.client.find(data_type=data_type, metadata_attributes={"CostCenter": "7003"}, limit=n)
        self.assertIsNotNone(results)
        self.assertEqual(len(results.get("Items")), n)

        # find with secondary filter applied
        results = self.client.find(data_type=data_type, metadata_attributes={"CostCenter": "7003", "id": "1680-meta"},
                                   limit=n)
        self.assertIsNotNone(results)
        self.assertEqual(len(results.get("Items")), 1)

    def test_get_endpoints(self):
        endpoints = self.client.get_endpoints(data_type=data_type)
        self.assertIsNotNone(endpoints)

    def test_get_export_status(self):
        job_name = None
        job_run_id = None
        # self.assertTrue(self.client.get_export_status(job_name, job_run_id))

    def test_get_status(self):
        info = self.client.get_status(data_type=data_type)
        self.assertEqual(info.get("Status"), params.STATUS_ACTIVE)

    def test_get_info(self):
        info = self.client.get_info(data_type=data_type)
        self.assertIsNotNone(info)

    def test_get_metadata(self):
        self.assertIsNotNone(self.client.get_metadata(data_type=data_type, item_id=_item_id))

    def test_get_resource(self):
        # get the item as default
        item = self.client.get_resource(data_type=data_type, item_id=_item_id)
        self.assertEqual(item.get("Item").get("Resource").get("id"), _item_id)
        self.assertIsNotNone(item.get("Item").get("Metadata"))

        # get the item with metadata fetch suppressed
        item = self.client.get_resource(data_type=data_type, item_id=_item_id, suppress_metadata_fetch=True)
        self.assertIsNone(item.get("Item").get("Metadata"))

    def test_get_resource_whitelist_attribute(self):
        self._create_base_item(data_type=data_type, item_id=_master_id)

        # get the item with an attribute whitelist
        item = self.client.get_resource(data_type=data_type, item_id=_item_id, suppress_metadata_fetch=True,
                                        only_attributes=["attr1"]).get(
            params.ITEM).get(params.RESOURCE)

        # data structure should now not include attr2 and attr3
        msg = "Found non-whitelisted Attribute"
        self.assertIsNone(item.get("attr2"), msg)
        self.assertIsNone(item.get("attr3"), msg)

    def test_get_resource_blacklist_attribute(self):
        self._create_base_item(data_type=data_type, item_id=_master_id)
        # get the item with an attribute blacklist
        item = self.client.get_resource(data_type=data_type, item_id=_item_id, suppress_metadata_fetch=True,
                                        not_attributes=["attr1"]).get(
            params.ITEM).get(params.RESOURCE)

        msg = "Found blacklisted Attribute"
        self.assertIsNone(item.get("attr1"), msg)

    def test_get_resource_include_master(self):
        self._create_base_item(data_type=data_type, item_id=_master_id)
        self.client.set_item_master(data_type=data_type, item_id=_item_id, item_master_id=_master_id)
        item = self.client.get_resource(data_type=data_type, item_id=_item_id,
                                        item_master_option=params.ITEM_MASTER_INCLUDE)
        self.assertEqual(item.get("Master").get("Resource").get("id"), _master_id)
        self.assertIsNotNone(item.get("Item"))

    def test_get_resource_prefer_master(self):
        self._create_base_item(data_type=data_type, item_id=_master_id)
        self.client.set_item_master(data_type=data_type, item_id=_item_id, item_master_id=_master_id)
        item = self.client.get_resource(data_type=data_type, item_id=_item_id,
                                        item_master_option=params.ITEM_MASTER_PREFER)
        self.assertEqual(item.get("Master").get("Resource").get("id"), _master_id)
        self.assertIsNone(item.get("Item"))

    def test_remove_master(self):
        self._create_base_item(data_type=data_type, item_id=_master_id)
        self.client.set_item_master(data_type=data_type, item_id=_item_id, item_master_id=_master_id)

        with self.assertRaises(InvalidArgumentsException):
            self.client.remove_item_master(data_type=data_type, item_id=_item_id, item_master_id="00")

    def test_update_resource(self):
        res = self.client.get_resource(data_type=data_type, item_id=_item_id).get("Item").get("Resource")

        key = "attr4"
        val = f"Value4-{shortuuid.uuid()}"
        res[key] = val

        response = self.client.put_resource(data_type=data_type, item_id=_item_id, resource=res)
        self.assertTrue(response.get(params.DATA_MODIFIED))

        item = self.client.get_resource(data_type=data_type, item_id=_item_id)
        self.assertEqual(item.get("Item").get("Resource").get(key), val)

        # test that I can fail an update that doesn't match the schema
        self._put_schema(params.RESOURCE)
        del res["attr1"]
        with self.assertRaises(InvalidArgumentsException):
            response = self.client.put_resource(data_type=data_type, item_id=_item_id, resource=res, strict_schema=True)

    def test_update_metadata(self):
        meta = self.client.get_metadata(data_type=data_type, item_id=_item_id)

        key = "attr4"
        val = f"Value4-{shortuuid.uuid()}"
        meta[key] = val

        response = self.client.put_metadata(data_type=data_type, item_id=_item_id, meta=meta)
        self.assertTrue(response.get(params.DATA_MODIFIED))

        meta = self.client.get_metadata(data_type=data_type, item_id=_item_id)
        self.assertEqual(meta.get(key), val)

        # test that I can fail an update that doesn't match the schema
        self._put_schema(params.METADATA)
        del meta["meta1"]
        with self.assertRaises(InvalidArgumentsException):
            response = self.client.put_metadata(data_type=data_type, item_id=_item_id, meta=meta, strict_schema=True)

    def test_lineage_search(self):
        id = None
        direction = None
        max_depth = None
        # self.assertTrue(self.client.lineage_search(id, direction, max_depth))
        pass

    def test_list_items(self):
        c = 10
        self.assertEqual(len(self.client.list_items(data_type=data_type, page_size=c).get("Items")), c)

    def test_provision(self):
        data_type = None
        primary_key = None
        table_indexes = None
        metadata_indexes = None
        delete_mode = None
        crawler_rolename = None
        schema_validation_refresh_hitcount = None
        graph_endpoint = None
        allow_non_item_master_writes = None
        strict_occv = None
        catalog_database = None
        es_domain = None
        es_delivery_role_arn = None
        es_delivery_failure_s3 = None
        pitr_enabled = None
        kms_key_arn = None
        # self.assertTrue(self.client.provision(data_type, primary_key, table_indexes, metadata_indexes, delete_mode,
        #                                      crawler_rolename, schema_validation_refresh_hitcount, graph_endpoint,
        #                                      allow_non_item_master_writes, strict_occv, catalog_database, es_domain,
        #                                      es_delivery_role_arn, es_delivery_failure_s3, pitr_enabled, kms_key_arn))

    def test_put_info(self):
        magic = shortuuid.uuid()
        t = "TestValue"
        api_metadata = {t: magic}
        self.assertTrue(self.client.put_info(data_type=data_type, api_metadata=api_metadata))
        got = self.client.get_info(data_type=data_type, attribute_filters=[t])
        self.assertEqual(magic, got.get(t))

    def test_put_metadata(self):
        meta = {"Metadata": {"CostCenter": "100", "Owner": "meyersi@amazon.com"}}
        response = self.client.put_metadata(data_type=data_type, item_id=_item_id, meta=meta)
        self.assertIsNotNone(response)

    def test_put_references(self):
        r = None
        # self.assertTrue(self.client.put_references(r))

    def test_start_export(self):
        export_job_dpu = None
        read_pct = None
        s3_export_path = None
        log_path = None
        setup_crawler = None
        kms_key_arn = None
        # self.assertTrue(
        #    client.start_export(export_job_dpu, read_pct, s3_export_path, log_path, setup_crawler, kms_key_arn))

    def test_restore_item(self):
        self.test_delete_resource()

        restored = self.client.restore_item(data_type=data_type, item_id=_item_id)
        self.assertEqual(_resource.get(params.RESOURCE).get("attr1"), restored.get("attr1"))

    def test_understand(self):
        id = None
        storage_location_attribute = None
        # self.assertTrue(self.client.understand(id, storage_location_attribute))

    def test_validate_item(self):
        validate_response = self.client.validate_item(data_type=data_type, item_id=_item_id)
        self.assertTrue(validate_response)

        # test invalid item
        with self.assertRaises(ResourceNotFoundException):
            self.client.validate_item(data_type=data_type, item_id="-1")


if __name__ == '__main__':
    unittest.main()
