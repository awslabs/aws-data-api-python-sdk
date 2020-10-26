from src.lib.http_handler import HttpHelper
from src.lib.data_api_control_plane import DataApiControlPlane
import os
import json
from src.exceptions import *
import src.parameters as params
import src.lib.utils as utils
import http
import logging

__version__ = "0.9.0b1"


class DataAPIClient:
    """AWS Data API Client.
    """
    _primary_key_attr = None
    _http_handler = None
    _stage = None
    _region_name = None
    _credentials = None
    _access_key = None
    _secret_key = None
    _session_token = None
    _control_plane = None
    _logger = None

    SEARCH_UPSTREAM = 'UP'
    SEARCH_DOWNSTREAM = 'DOWN'

    def __init__(self, stage: str, region_name: str = None, access_key: str = None, secret_key: str = None,
                 session_token: str = None, service_endpoint: str = None, tls: bool = True, log_level: str = 'INFO'):
        logging.basicConfig()
        self._logger = logging.getLogger("DataAPIClient")
        self._logger.setLevel(log_level)

        self._stage = stage
        if region_name is None:
            self._region_name = os.getenv("AWS_REGION")
        else:
            self._region_name = region_name

        # resolve credentials
        if access_key is None and secret_key is None:
            # use helper module to resolve credentials
            credentials = utils.get_credentials()
            self._access_key = credentials.access_key
            self._secret_key = credentials.secret_key
            self._session_token = credentials.session_token
        else:
            self._access_key = access_key
            self._secret_key = secret_key
            self._session_token = session_token

        self._control_plane = DataApiControlPlane(tls=tls, region_name=self._region_name,
                                                  override_url=service_endpoint)

        self._http_handler = HttpHelper(host=self._control_plane.get_endpoint(stage), stage=self._stage,
                                        region=self._region_name, access_key=self._access_key,
                                        secret_key=self._secret_key, session_token=self._session_token,
                                        custom_domain=self._control_plane.is_custom_domain(stage), logger=self._logger)

        print(
            f"Bound Data API Client in Stage {self._stage} to {self._http_handler.get_base_path()}")

    def _handle_response(self, response):
        if response.status_code in [http.HTTPStatus.CREATED, http.HTTPStatus.ACCEPTED]:
            return True
        elif response.status_code == http.HTTPStatus.NOT_MODIFIED:
            return False
        elif response.status_code == http.HTTPStatus.NO_CONTENT:
            return None
        elif response.status_code == http.HTTPStatus.BAD_REQUEST:
            raise InvalidArgumentsException()
        elif response.status_code == http.HTTPStatus.NOT_FOUND:
            raise ResourceNotFoundException()
        elif response.status_code == http.HTTPStatus.CONFLICT:
            raise ConstraintViolationException()
        elif response.status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR:
            raise Exception(response.reason)
        elif response.status_code != http.HTTPStatus.OK:
            message = response.reason

            if "content" in response:
                content_body = json.loads(response.get("content"))
                if "Message" in content_body:
                    message = content_body.get("Message")
            raise DetailedException(message)
        else:
            if response is None:
                return None
            else:
                if response.text is not None and response.text != '':
                    return response.json()
                else:
                    return True

    def _validate_item_structure(self, structure, omit=None):
        valid_top_level = ["Resource", "Metadata", "References"]

        if omit is not None:
            for o in omit:
                valid_top_level.pop(o)

        if not any([x in structure for x in valid_top_level]):
            raise InvalidArgumentsException("Item must include Resource, Metadata, or References")

    def provision(self, data_type: str, primary_key: str, table_indexes=None, metadata_indexes=None, delete_mode=None,
                  crawler_rolename=None, schema_validation_refresh_hitcount=None,
                  graph_endpoint=None, allow_non_item_master_writes=True, strict_occv=False, catalog_database=None,
                  es_domain=None, es_delivery_role_arn=None, es_delivery_failure_s3=None, pitr_enabled=True,
                  kms_key_arn=None):
        """Create a new API endpoint.
        """
        # return PUT /provision
        body = {
            params.DATA_TYPE: data_type,
            params.PRIMARY_KEY: primary_key,
            params.TABLE_INDEXES: table_indexes,
            params.METADATA_INDEXES: metadata_indexes,
            params.DELETE_MODE: delete_mode,
            params.CRAWLER_ROLENAME: crawler_rolename,
            params.SCHEMA_VALIDATION_REFRESH_HITCOUNT: schema_validation_refresh_hitcount,
            params.GREMLIN_ADDRESS: graph_endpoint,
            params.NON_ITEM_MASTER_WRITES_ALLOWED: allow_non_item_master_writes,
            params.STRICT_OCCV: strict_occv,
            params.CATALOG_DATABASE: catalog_database,
            params.ES_DOMAIN: es_domain,
            params.FIREHOSE_DELIVERY_ROLE_ARN: es_delivery_role_arn,
            params.DELIVERY_STREAM_FAILURE_BUCKET: es_delivery_failure_s3,
            params.PITR_ENABLED: pitr_enabled,
            params.KMS_KEY_ARN: kms_key_arn
        }
        return self._handle_response(self._http_handler.put(data_type=data_type, path="provision"), put_body=body)

    def get_namespaces(self):
        """ Get all the provisioned namespaces in a given API
        """
        # return GET /namespaces
        return self._handle_response(self._http_handler.get(data_type=None, path="namespaces"))

    def get_endpoints(self, data_type: str):
        """ Get all of the available endpoints for the API Type;
        """
        # return GET /endpoints
        return self._handle_response(self._http_handler.get(data_type=data_type, path="endpoints"))

    def get_status(self, data_type: str):
        """Method to return the status of a Namsepace
        """
        # return GET /status
        return self._handle_response(self._http_handler.get(data_type=data_type, path="status"))

    def get_info(self, data_type: str, attribute_filters: list = None):
        """Method to return Namespace Metadata.
        """
        apply_filters = None

        if attribute_filters is not None:
            apply_filters = {
                params.ATTRIBUTE_FILTER_PARAM: ','.join(attribute_filters)
            }

        # return GET /info
        return self._handle_response(
            self._http_handler.get(data_type=data_type, path="info", query_params=apply_filters))

    def put_info(self, data_type: str, api_metadata: dict):
        """Method to create Namespace Metadata."""
        # return PUT /info
        return self._handle_response(self._http_handler.put(data_type=data_type, path="info", put_body=api_metadata))

    def list_items(self, data_type: str, page_size: int = None, start_token: str = None, segment: int = None,
                   total_segments: int = None):
        """List items in the API Namespace using pagination and parallel scanning if requested.
        """
        # validate args
        args = {}
        try:
            args[params.QUERY_PARAM_LIMIT] = int(page_size)
            if segment is not None:
                args[params.QUERY_PARAM_SEGMENT] = int(segment)
            if total_segments is not None:
                args[params.QUERY_PARAM_TOTAL_SEGMENTS] = int(total_segments)
        except ValueError as e:
            raise InvalidArgumentsException("Invalid Value for page_size, segment, or total_segments. Must be Int")

        if segment is not None and total_segments is None:
            raise InvalidArgumentsException("Parallel List requires segment and total_segments")

        if start_token is not None:
            args[params.EXCLUSIVE_START_KEY] = start_token

        # return GET /list
        return self._handle_response(self._http_handler.get(data_type=data_type, path="list", query_params=args))

    def get_schema(self, data_type: str, schema_type: str):
        """Get the schema for the Namespace's Resources or Metadata.
        """
        # return GET /schema/{schema_type}
        return self._handle_response(self._http_handler.get(data_type=data_type, path=f"schema/{schema_type}"))

    def put_schema(self, data_type: str, schema_type: str, json_schema: dict):
        """Create a schema for a Namespace Resources or Metadata.
        """
        # return PUT /schema/{schema_type}
        return self._handle_response(
            self._http_handler.put(data_type=data_type, path=f"schema/{schema_type}", put_body=json_schema))

    def delete_schema(self, data_type: str, schema_type: str):
        """Delete the schema from a Namespace Resource or Metadata.
        """
        # return DELETE /schema/{schema_type}
        return self._handle_response(self._http_handler.delete(data_type=data_type, path=f"schema/{schema_type}"))

    def set_item_master(self, data_type: str, item_id: str, item_master_id: str):
        """Link a Resource in the Namespace to an Item Master.
        """
        # return PUT /ItemMaster
        body = {
            "id": item_id,
            "ItemMasterID": item_master_id
        }
        return self._handle_response(self._http_handler.put(data_type=data_type, path="ItemMaster", put_body=body))

    def remove_item_master(self, data_type: str, item_id: str, item_master_id: str):
        """Remove an Item Master reference.
        """
        # return DELETE /ItemMaster with correct payload
        body = {
            "id": item_id,
            "ItemMasterID": item_master_id
        }
        return self._handle_response(
            self._http_handler.delete(data_type=data_type, path="ItemMaster", delete_body=body))

    def find(self, data_type: str, resource_attributes=None, metadata_attributes=None, start_token: str = None,
             limit: int = None,
             consistent_read: bool = None):
        """Perform a query or scan on the Namespace to find the item based on provided Resource or Metadata attributes.
        """
        if resource_attributes is not None and metadata_attributes is not None:
            raise InvalidArgumentsException("Provide Resource or Metadata attributes to search, but not both")

        if limit is not None and not isinstance(limit, int):
            raise InvalidArgumentsException("Limit must be an Integer")

        if consistent_read is not None and not isinstance(consistent_read, bool):
            raise InvalidArgumentsException("Consistent Read must be a Boolean")

        search_request = {}
        if resource_attributes is not None and not isinstance(resource_attributes, dict):
            raise InvalidArgumentsException("Resource Attributes must be a Dictionary")
        else:
            search_request[params.RESOURCE] = resource_attributes

        if metadata_attributes is not None and not isinstance(metadata_attributes, dict):
            raise InvalidArgumentsException("Metadata Attributes must be a Dictionary")
        else:
            search_request[params.METADATA] = metadata_attributes

        if start_token is not None:
            search_request[params.EXCLUSIVE_START_KEY] = start_token

        if limit is not None:
            search_request[params.QUERY_PARAM_LIMIT] = limit

        if consistent_read is not None and consistent_read is True:
            search_request[params.QUERY_PARAM_CONSISTENT] = "True"

        # return POST /find
        return self._handle_response(
            self._http_handler.post(data_type=data_type, path="find", post_body=search_request))

    def validate_item(self, data_type: str, item_id: str):
        """Check if an Item exists by ID in the Namespace.
        """
        return self._handle_response(self._http_handler.head(data_type=data_type, path=f"{item_id}"))

    def get_resource(self, data_type: str, item_id: str, item_master_option: str = None,
                     suppress_metadata_fetch: bool = False):
        """Get a Resource from the Namespace.
        """
        p = {}
        if item_master_option is not None:
            if item_master_option.lower() not in [params.ITEM_MASTER_INCLUDE.lower(),
                                                  params.ITEM_MASTER_PREFER.lower()]:
                raise InvalidArgumentsException(
                    f"Item Master option should be {params.ITEM_MASTER_PREFER} or {params.ITEM_MASTER_INCLUDE}")
            p[params.ITEM_MASTER_QP] = item_master_option

        if suppress_metadata_fetch is not None:
            p[params.SUPPRESS_ITEM_METADATA_FETCH] = suppress_metadata_fetch

        return self._handle_response(self._http_handler.get(data_type=data_type, path=f"{item_id}", query_params=p))

    def get_metadata(self, data_type: str, item_id: str):
        """Get Metadata for an Item in the Namespace.
        """
        # return GET /id/meta
        return self._handle_response(self._http_handler.get(data_type=data_type, path=f"{item_id}/meta"))

    def delete_resource(self, data_type: str, item_id: str, delete_mode: str = None):
        """Delete an item from the Namespace based upon admin config (tombstone or soft delete).
        """
        # return DELETE /{id}
        body = {}
        if delete_mode is not None:
            body[params.DELETE_MODE] = delete_mode
        return self._handle_response(
            self._http_handler.delete(data_type=data_type, path=f"{item_id}", delete_body=body))

    def delete_metadata(self, data_type: str, item_id: str):
        """Delete Metadata for an Item from the Namespace.
        """
        return self._handle_response(
            self._http_handler.delete(data_type=data_type, path=f"{item_id}", delete_body={"Metadata": {}}))

    def restore_item(self, data_type: str, item_id: str):
        """Restore a deleted Item in the Namespace (only supported after Soft Delete).
        """
        # return PUT /restore
        return self._handle_response(self._http_handler.put(data_type=data_type, path=f"{item_id}/restore"))

    def delete_attributes(self, data_type: str, item_id: str, resource_attributes=None, metadata_attributes=None):
        """Delete attributes from a Resource or Metadata.
        """
        # validate that at least 1 attribute list has been provided and their type is list
        if (resource_attributes is None and metadata_attributes is None) or \
                (resource_attributes is not None and not isinstance(resource_attributes, list)) or \
                (metadata_attributes is not None and not isinstance(metadata_attributes, list)) or \
                (resource_attributes is not None and len(resource_attributes) == 0) or \
                (metadata_attributes is not None and len(metadata_attributes) == 0):
            raise InvalidArgumentsException("Provide either Resource or Metadata attributes to remove")

        delete = {}
        if resource_attributes is not None:
            delete["Resource"] = resource_attributes

        if metadata_attributes is not None:
            delete["Metadata"] = metadata_attributes

        # return DELETE /{id}
        return self._handle_response(
            self._http_handler.delete(data_type=data_type, path=f"{item_id}", delete_body=delete))

    # private method to perform a put body with the correct path
    def _item_write(self, data_type: str, item_id: str, body: dict):
        return self._handle_response(self._http_handler.put(data_type=data_type, path=f"{item_id}", put_body=body))

    # put a full item that is well formed by the client
    def _put_item(self, data_type: str, item_id: str, item: dict, item_version: int = None, strict_schema: bool = None):
        # ensure the item is well formed
        self._validate_item_structure(item)

        if item_version is not None:
            if not isinstance(item_version, int):
                raise InvalidArgumentsException("Item Version must be an Integer")
            else:
                # ensure that the value of the item version is set correctly
                iv = "ItemVersion"
                item.pop(iv)
                item[iv] = item_version

        if strict_schema is not None and isinstance(strict_schema, bool) and strict_schema is True:
            item.pop("StrictSchemaValidation")
            item["StrictSchemaValidation"] = 'True'

        # write the item structure
        return self._item_write(data_type=data_type, item_id=item_id, body=item)

    def put_resource(self, data_type: str, item_id: str, resource: dict, item_version: int = None):
        """Create or update a Resource in the Namespace.
        """
        if params.RESOURCE in resource:
            _resource = resource
        else:
            _resource = {params.RESOURCE: resource}

        return self._put_item(data_type=data_type, item_id=item_id, item=_resource, item_version=item_version).get(
            params.RESOURCE)

    def put_metadata(self, data_type: str, item_id: str, meta: dict):
        """Create or update Metadata for a Resource in the Namespace
        """
        if params.METADATA in meta:
            _meta = meta
        else:
            _meta = {params.METADATA: meta}

        # remove the primary key from the item
        return self._put_item(data_type=data_type, item_id=item_id, item=_meta).get(params.METADATA)

    def put_references(self, data_type: str, item_id: str, references: dict):
        """Create or update References for a Resource in the Namespace.
        """
        if params.REFERENCES in references:
            _item = references
        else:
            _item = {params.REFERENCES: [references]}

        return self._put_item(data_type=data_type, item_id=item_id, item=_item).get(params.REFERENCES)

    def lineage_search(self, data_type: str, item_id: str, direction: str, max_depth: int = None):
        """Perform an upstream or downstream data lineage search.
        """
        p = None
        if max_depth is not None:
            if not isinstance(max_depth, int):
                raise InvalidArgumentsException("Max Depth must be an Integer")
            else:
                p = {"search_depth": max_depth}

        if direction.upper() == 'UP':
            d = "upstream"
        else:
            d = "downstream"

        # return GET /upstream or /downstream
        return self._handle_response(self._http_handler.get(data_type=data_type, path=f"{item_id}/{d}", query_params=p))

    def start_export(self, data_type: str, export_job_dpu: int, read_pct: int, s3_export_path: str, log_path: str,
                     setup_crawler: bool = True, kms_key_arn: str = None,
                     catalog_database: str = None):
        """Export the contents of a Namespace to S3.
        """
        body = {
            params.EXPORT_JOB_DPU: export_job_dpu,
            params.EXPORT_READ_PCT: read_pct,
            params.EXPORT_S3_PATH: s3_export_path,
            params.EXPORT_LOG_PATH: log_path,
            params.EXPORT_SETUP_CRAWLER: setup_crawler,
            params.KMS_KEY_ARN: kms_key_arn,
            params.CATALOG_DATABASE: catalog_database
        }
        return self._handle_response(self._http_handler.post(data_type=data_type, path="export", post_body=body))

    def get_export_status(self, data_type: str, job_name: str, job_run_id: str = None):
        """Get the status of an Export Job.
        """
        qp = {params.JOB_NAME_PARAM: job_name}

        if job_run_id is not None:
            qp[params.JOB_RUN_PARAM] = job_run_id

        return self._handle_response(self._http_handler.get(data_type=data_type, path="export", query_params=qp))

    def understand(self, data_type: str, item_id: str, storage_location_attribute: str):
        """Run an AI powered Metadata resolver against a Resource.
        """
        return self._handle_response(
            self._http_handler.put(data_type=data_type, path=f"{item_id}/understand", put_body={
                params.STORAGE_LOCATION_ATTRIBUTE: storage_location_attribute}))
