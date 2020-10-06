# Working with Data API's

Once you have created a Client, you can start calling methods on your Data API. Each method in the client requires that you specify a `data_type`, which is a reference to the [Namespace](Concepts) you want to work with. You can discover all of the available Namespaces that the Data API you are connected to can support with the `get_namespaces()` method.

## Client

_class_ `DataAPIClient`

Class representing a connection to a Data API Stage.

```python
from lib.data_api_control_plane import DataApiControlPlane
from data_api_client import DataAPIClient

# get the region from the environment
region = os.getenv("AWS_REGION")

# create a control plane reference
control_plane = DataApiControlPlane(tls=True, region_name=region)

# One time setup of the endpoint cache
control_plane.connect(
	from_url=endpoint,
	access_key=access_key,
	secret_key=secret_key, 
	session_token=session_token,
	force_refresh=True
)

# create an API client in Dev stage
cls.client = DataAPIClient(stage="test", region_name=region)
```
these are the available methods:

* [`delete_attributes()`](#delete_attributes)
* [`delete_metadata()`](#delete_metadata)
* [`delete_resource()`](#delete_resource)
* [`delete_schema()`](#delete_schema)
* [`find()`](#find)
* [`get_endpoints()`](#get_endpoints)
* [`get_export_status()`](#get_export_status)
* [`get_info()`](#get_info)
* [`get_metadata()`](#get_metadata)
* [`get_namespaces()`](#get_namespaces)
* [`get_resource()`](#get_resource)
* [`get_schema()`](#get_schema)
* [`lineage_search()`](#lineage_search)
* [`list_items()`](#list_items)
* [`provision()`](#provision)
* [`put_info()`](#put_info)
* [`put_metadata()`](#put_metadata)
* [`put_references()`](#put_references)
* [`put_resource()`](#put_resource)
* [`put_schema()`](#put_schema)
* [`remove_item_master()`](#remove_item_master)
* [`restore_item()`](#restore_item)
* [`set_item_master()`](#set_item_master)
* [`start_export()`](#start_export)
* [`understand()`](#understand)
* [`validate_item()`](#validate_item)

---- 
### delete_attributes

Method that enables you to delete specific Attributes from a Resource or Metadata item.

#### Request Syntax

__HTTP__

```json
http DELETE https://<data-api>/<stage>/<namespace>/<id>
{
	"Resource": [
		"Attribute1",
		"Attribute2",
		...,
		"AttributeN"
	],
	"Metadata": [
		"Attribute1",
		"Attribute2",
		...,
		"AttributeN"	
	]
}
```

__Python Client__

```python
response = client.delete_attributes(
	data_type: str, 
	id: str, 
	resource_attributes=None, 
	metadata_attributes=None
)
```

#### Parameters

* `data_type` (string) - The data type/Namespace
* `id` (string) - The ID of the Item to be modified
* `resource_attributes` (list) - The list of Attributes to remove from the Resource
* `metadata_attributes` (list) - The list of Attributes to remove from the Metadata

#### Return Type

JSON - Document

#### Returns

Indicator of whether the attribute deletion was successful. All attributes will be deleted, or none will be.

##### Response Syntax

```
{
	"DataModified": "boolean"
}
```

##### Response Structure

* `DataModified` - Boolean indicator of if the Attributes were deleted

---- 
### delete_metadata

Request to delete Metadata for an Item.

#### Request Syntax

__HTTP__

```json
http DELETE https://<data-api>/<stage>/<namespace>/<id>
{
	"Metadata": []
}

```

__Python Client__

```python
response = client.delete_metadata(
	data_type: str, 
	id: str
)
```

#### Parameters

* `data_type` (string) - The data type/Namespace
* `id` (string) - The ID of the Item to be modified

#### Return Type

JSON - Document

#### Returns

Indicator of whether the Metadata was deleted.

##### Response Syntax

```
{
	"DataModified": "boolean"
}
```

##### Response Structure

* `DataModified` - Boolean indicator of if the Attributes were deleted

---- 
### delete_resource

Deletes a Resource and its associated Metadata.

#### Request Syntax

__HTTP__

```json
http DELETE https://<data-api>/<stage>/<namespace>/<id>
{
	"DeleteMode": str
}

```

__Python Client__

```python
response = client.delete_resource(
data_type: str, 
id: str, 
delete_mode: str = None
)
```

#### Parameters

* `data_type` (string) - The data type/Namespace
* `id` (string) - The ID of the Item to be deleted
* `delete_mode` (string) - The deletion mode, defaulted to the configuration set by the Data API Administrator. If Delete Mode Overrides are enabled, this setting this value will result in differing behaviour of the deletion. Use `TOMBSTONE` for completely delete the item and leave a record of its deletion (this cannot be reversed), or `SOFT` for soft deletion, which can be reversed with the [`restore_item()`](#restore_item) API request.

#### Return Type

JSON - Document

#### Returns

Indicator of whether the Resource deletion was successful.

##### Response Syntax

```
{
	"DataModified": "boolean"
}
```

##### Response Structure

* `DataModified` - Boolean indicator of if the Attributes were deleted
	
---- 
### delete_schema

Removes the Schema for Resources or Metadata from a Namespace (requires elevated privileges).

#### Request Syntax

__HTTP__

```json
http DELETE https://<data-api>/<stage>/<namespace>/schema/<schema type>

```

__Python Client__

```python
response = client.delete_schema(
	data_type: str, 
	schema_type: str
)
```

#### Parameters

* `data_type` (string) - The data type/Namespace
* `schema_type` (string) - The schema type to remove. Must be one of `resource` or `metadata`.

#### Return Type

JSON - Document

#### Returns

Indicator of whether the deletion was successful.

##### Response Syntax

```
{
	"DataModified": "boolean"
}
```

##### Response Structure

* `DataModified` - Boolean indicator of if the Attributes were deleted

---- 
### find

Performs a search for an Item based upon Attribute values provided.

#### Request Syntax

__HTTP__

```json
http POST https://<data-api>/<stage>/<namespace>/<id>
{
	"Resource": {
		"Attribute1": str,
		"Attribute2": str,
		...,
		"AttributeN":str
	},
	"Metadata": {
		"Attribute1": str,
		"Attribute2": str,
		...,
		"AttributeN":str	
	},
	"Limit": int,
	"Segment": int,
	"TotalSegments": int,
	"Consistent": bool
}

```

__Python Client__

```python
response = client.find(
	data_type: str, 
	resource_attributes=None, 
	metadata_attributes=None, 
	start_token: str = None,
	limit: int = None,
	consistent_read: bool = None
)
```

#### Parameters

* `data_type` (string) - The data type/Namespace
* `resource_attributes` (dict) - The Resource attributes to search for
* `metadata_attributes` (dict) - The Metadata attributes to search for
* `start_token` (string) - The starting token value to search from, for paginated searches
* `limit` (int) - The number of results to return
* `consistent_read` (boolean) - Whether a consistent read should be performed (default False)

#### Return Type

JSON - Document

#### Returns

List of Items found by the search request.

##### Response Syntax

```
{
    "Items": [
        {
            "id": "2000-meta"
            "ItemVersion": 3,
            "LastUpdateAction": "update",
            "LastUpdateDate": "2020-03-15 13:29:40",
            "LastUpdatedBy": "887210671223.AROA45EPAPR3Q7HLRS63S:AwsDataAPI-dev",
			...   
        },
        ...
	],
	"LastEvaluatedKey": "2740-meta"
}
```

##### Response Structure
 
* `Items` (list) - The Items that were found in the search request
	* `id` (string) - The ID of the Item
	* `ItemVersion` (int) - The version number of the Item - increments on each update
	* `LastUpdateAction` (string) - The last action taken against the Item
	* `LastUpdateDate` (string) - The date of the last action
	* `LastUpdatedBy` (string) - The ARN of the Identity that performed the last action
	* ...
	* Attributes of the Item are projected into the search results
* `LastEvaluatedKey` (string) - String value that was the last evaluated by the search before the 'limit' was reached.

---- 
### get_endpoints

Returns the endpoint addresses of the resources used by a namespace. This includes the Resource and Metadata stream addresses, and the ElasticSearch and Neptune configurations if they have been provisioned.

#### Request Syntax

__HTTP__

```json
http GET https://<data-api>/<stage>/<namespace>/endpoints

```

__Python Client__

```python
response = client.get_endpoints(
	data_type: str
)
```

#### Parameters

* `data_type` (string) - The data type/Namespace

#### Return Type

JSON - Document

#### Returns

Endpoint information in use by the Data API.

##### Response Syntax

```
{
    "MetadataARN": "arn",
    "ResourceARN": "arn",
    "GraphURL":"string",
    "Elasticsearch":"string"
}

```

##### Response Structure

* `MetadataARN` (arn) - The ARN of the change stream associated with the Resources in this Namespace.
* `ResourceARN` (arn) - The ARN of the change stream associated with the Metadata in this Namespace.
* `GraphURL` (string) - The URL of the configured Graph Database, if provisioned and used for creating [References](ResourcesMetadataReferences).
* `Elasticsearch` (string) - The URL of the configured Elasticsearch cluster, if provisioned and used for enhanced search.

---- 
### get\_export\_status

Returns the status of a data export job (export to S3).

#### Request Syntax

__HTTP__

```json
http GET https://<data-api>/<stage>/<namespace>/export?JobName=str&JobRunId=str
```

__Python Client__

```python
response = client.get_export_status(
	data_type: str, 
	job_name: str, 
	job_run_id: str = None
)
```

#### Parameters

* `data_type` (string) - The data type/Namespace
* `job_name` (string) - The name of the job specified when the export was created
* `job_run_id` (string) - The instance of the specified export job

#### Return Type

JSON - Document

#### Returns

JSON Document indexing status information for the Export job.

##### Response Syntax

```json
{<Job ID>: {
	"Status": str,
	"Started": datetime,
	"ExecutedDuration": int,
	"Completed": datetime,
	"ErrorMessage": str,
	"Arguments": dict
	}
}
```

##### Response Structure

* `Job ID` - The ID of the Glue job used to export data to S3
	* `Status` - The status of the export job. One of `'STARTING'|'RUNNING'|'STOPPING'|'STOPPED'|'SUCCEEDED'|'FAILED'|'TIMEOUT'`
	* `Started` - The date and time that the job started (format `%Y-%m-%d %H:%M:%S`)
	* `ExecutedDuration` - The amount of time, in seconds, that the job ran
	* `Completed` - The date and time that the job completed  (format `%Y-%m-%d %H:%M:%S`)
	* `ErrorMessage` - Any error message that was encountered during the export. Optional.
	* `Arguments` - Dictionary of arguments passed to the export job

---- 
### get_info

Returns Metadata about an API Namespace. View all available Namespaces in the Stage with the [get_namespaces()](#get_namespaces) method.

#### Request Syntax

__HTTP__

```json
http GET https://<data-api>/<stage>/<namespace>/info

```

__Python Client__

```python
response = client.get_info(
	data_type: str
)
```

#### Parameters

* `data_type`: str - The Data Type/Namespace for which you wish to return Metadata

#### Return Type

JSON - Document

#### Returns

API Namespace and Stage level Metadata.

##### Response Syntax

```json
{
    "AllowRuntimeDeleteModeChange": bool,
    "CatalogDatabase": str,
    "CrawlerRolename": str,
    "DataType": str,
    "DeleteMode": str,
    "DeployedAccount": str,
    "GremlinAddress": str,
    "LastUpdateAction": str,
    "LastUpdateDate": datetime,
    "LastUpdatedBy": str,
    "ResourceIndexes": struct,
    "MetadataIndexes": struct,
    "NonItemMasterWritesAllowed": bool,
    "PrimaryKey": str,
    "Resources": [
        {
            "name": "EsIndexer_role",
            "resource_type": "iam_role",
            "role_arn": str,
            "role_name": "AwsDataAPI-MyItem-dev-EsIndexer"
        },
        {
            "lambda_arn": str,
            "name": "EsIndexer",
            "resource_type": "lambda_function"
        },
        {
            "name": "api_handler_role",
            "resource_type": "iam_role",
            "role_arn": str,
            "role_name": "AwsDataAPI-MyItem-dev-api_handler"
        },
        {
            "lambda_arn": str,
            "name": "api_handler",
            "resource_type": "lambda_function"
        },
        {
            "name": "rest_api",
            "resource_type": "rest_api",
            "rest_api_id": str,
            "rest_api_url": str
        }
    ],
    "SearchConfig": {
        "DeliveryStreams": {
            "Metadata": {
                "DestinationDeliveryStreamARN": str,
                "SourceStreamARN": str
            },
            "Resource": {
                "DestinationDeliveryStreamARN": str,
                "SourceStreamARN": str
            }
        },
        "ElasticSearchDomain": {
            "ARN": str,
            "DomainId": str,
            "ElasticSearchEndpoint": str
        }
    },
    "SearchSetup": {
        "ElasticSearchDomain": str,
        "FailedSearchIndexRecordBucket": str,
        "FirehoseDeliveryIamRoleARN": str
    },
    "Stage": str,
    "StorageHandler": str,
    "StorageTable": str,
    "StrictOCCV": str,
    "api": str,
    "region": str,
    "type": "ApiMetadata"
}
```

##### Response Structure

* `AllowRuntimeDeleteModeChange`: bool - Administrator setting indicating whether the Deletes can dynamically be switched between `soft` and `tombstone`. If False, then only the `DeleteMode` is applied to Item delete requests
* `CatalogDatabase`: str - The name of the Glue Catalog database which contains references to Data API data
* `CrawlerRolename`: str - The name of the Glue Crawler used to determine Object schema for this Namespace
* `DataType`: str - The name and stage that uniquely identifies this Namespace
* `DeleteMode`: str - Configuration value dictating how deletes are handled. `soft` deletes support restore operations, while `tombstone` deletes are permanent.
* `DeployedAccount`: str - The Account ID in which this Data API is installed
* `GremlinAddress`: str - If Data Lineage & Reference tracking is enabled, the address of the Graph Database that contains the lineage store
* `ResourceIndexes`: struct - Name of Resource Attributes, and their data types, which are indexed by the Data API
* `MetadataIndexes`: struct - Name of Metadata Attributes, and their data types, which are indexed by the Data API
* `NonItemMasterWritesAllowed`: bool - Configuration value that determines whether updates are allowed on Items that have an ItemMaster link created.
* `PrimaryKey`: str - Attribute Name of the primary key for the Resource
* `Resources`: list - List of objects provisioned automatically for the Data API in this account
	* `name`: str - Name of the Resource
	* `resource_type`: (`iam_role` | `lambda_function` | `rest_api`) - The type of the resource provisioned
	* `role_arn`: str - If an `iam_role`, the ARN of the Role
	* `role_name`: str - If an `iam_role`, the Name of the Role
	* `lambda_arn`: str - If a `lambda_function`, the ARN of the deployed function
	* `rest_api_id`: str - If a `rest_api`, the ID of the API Gateway
	* `rest_api_url`: str - If a `rest_api`, the URL of the API gateway (does not include custom domain information)
* `SearchConfig`: JSON - Provisioned Search Integration Information
	* `DeliveryStreams`: JSON - Information about the provisioned Delivery Streams for DynamoDB and Kinesis Firehose
		* `Metadata`: JSON - Information about delivery of Metadata to ElasticSearch
			* `DestinationDeliveryStreamARN`: str - Firehose Delivery Stream ARN for Metadata
			* `SourceStreamARN`: str - DynamoDB Stream ARN for Metadata
		* `Resource`: JSON - Information about delivery of Resources to ElasticSearch
			* `DestinationDeliveryStreamARN`: str - Firehose Delivery Stream ARN for Resources
			* `SourceStreamARN`: str - DynamoDB Stream ARN for Resources
	* `ElasticSearchDomain`: JSON - The configured ElasticSearch Domain
		* `ARN`: str - ARN of the ElasticSearch Service Domain
		* `DomainId`: str - Domain ID for the ElasticSearch Service
		* `ElasticSearchEndpoint`: str - Endpoint Address for ElasticSearch
* `SearchSetup`: JSON - Configuration information supplied by Administrator for Search Integration
	* `ElasticSearchDomain`: str - Name of the ElasticSearch Domain to be used for Indexing
	* `FailedSearchIndexRecordBucket`: str - S3 Bucket to be used for failed indexing records
	* `FirehoseDeliveryIamRoleARN`: str - IAM Role ARN that contains permissions for Lambda to write to Kinesis Firehose, and Firehose to write to ElasticSearch
* `Stage`: str - The Stage for this Namespace
* `StorageHandler`: str - The back end storage integration class. Today only supports `dynamo_storage_handler`.
* `StorageTable`: str - The table in DynamoDB used to store Resource data
* `StrictOCCV`: str - Configuration indicating whether Strict Optimistic Concurrency Control is in use
* `api`: str - The name of the API
* `region`: str - The AWS Region in which this API is deployed
* `type`: "ApiMetadata"

---- 
### get_metadata

Retrieves Metadata for an Item

#### Request Syntax

__HTTP__

```json
http GET https://<data-api>/<stage>/<namespace>/<id>/meta

```

__Python Client__

```python
response = client.get_metadata(
	data_type: str,
	id: str
)
```

#### Parameters

* `data_type` (string) - The data type/Namespace
* `id` (string) - The ID of the Item to fetch Metadata for

#### Return Type

JSON - Document

#### Returns

Metadata associated with the Item.

##### Response Syntax

```json
{
	"MetadataAttribute1": "MetadataValue1",
	"MetadataAttribute2": "MetadataValue2",
	...
	"MetadataAttributeN": "MetadataValueN",
	"ItemVersion": int,
	"LastUpdateAction": str,
	"LastUpdateDate": datetime,
	"LastUpdatedBy": str
}
```

##### Response Structure

* `MetadataAttributes` - The Metadata Attributes associated with the Resource
* `ItemVersion` - The current version number of the Metadata entry
* `LastUpdateAction` - `insert` or `update` depending on the last action take on the Metadata
* `LastUpdateDate` - The date and time of the `LastUpdateAction`
* `LastUpdatedBy` - The Identity ARN of the user who performed the last action

---- 
### get_namespaces

#### Request Syntax

__HTTP__

```json
http GET https://<data-api>/<stage>/namespaces

```

__Python Client__

```python
response = client.get_namespaces()
```

#### Parameters

None

#### Return Type

JSON - List

#### Returns

List of Namespaces avialable from this API Stage

##### Response Syntax

```json
[
	"Namespace 1",
	"Namespace 2",
	...
	"Namespace N"
]
```

##### Response Structure

* List of Data API Namespaces

---- 
### get_resource

#### Request Syntax

__HTTP__

```json
http GET https://<data-api>/<stage>/<namespace>/<id>?ItemMaster=str&SuppressItemMetadataFetch=bool

```

__Python Client__

```python
response = client.get_resource(
	data_type: str,
	id: str,
	item_master_option: str,
	suppress_metadata_fetch: bool = False
)
```

#### Parameters

* `data_type` (string) - The data type/Namespace
* `id` (string) - The ID of the Item to fetch
* `item_master_option ` - If MDM features are in use, and the Resource has an Item Master ID, then use `include` to also return the Item Master, or `prefer` to *only* return the Item Master
* `suppress_metadata_fetch` - By default, the Item will return both the Resource and the Metadata. Set this parameter to `True` to only return the Resource.

#### Return Type

JSON - Document

#### Returns

JSON Document containing the Item, and optionally the Item Master associated with the Item.

##### Response Syntax

```json
{
	"Item": {
		"Resource": {
			"Resource Attribute 1: "Resource Value 1",
			"Resource Attribute 2: "Resource Value 2",
			...
			"Resource Attribute N: "Resource Value N",
			"ItemVersion": int,
			"LastUpdateAction": str,
			"LastUpdateDate": datetime,
			"LastUpdatedBy": str
		},
		"Metadata": {
			"Metadata Attribute 1: "Metadata Value 1",
			"Metadata Attribute 2: "Metadata Value 2",
			...
			"Metadata Attribute N: "Metadata Value N",
			"ItemVersion": int,
			"LastUpdateAction": str,
			"LastUpdateDate": datetime,
			"LastUpdatedBy": str
		}		
	},
	"Master": {
		"Resource": {
			"Resource Attribute 1: "Resource Value 1",
			"Resource Attribute 2: "Resource Value 2",
			...
			"Resource Attribute N: "Resource Value N",
			"ItemVersion": int,
			"LastUpdateAction": str,
			"LastUpdateDate": datetime,
			"LastUpdatedBy": str
		},
		"Metadata": {
			"Metadata Attribute 1: "Metadata Value 1",
			"Metadata Attribute 2: "Metadata Value 2",
			...
			"Metadata Attribute N: "Metadata Value N",
			"ItemVersion": int,
			"LastUpdateAction": str,
			"LastUpdateDate": datetime,
			"LastUpdatedBy": str
		}	
	}
}
```

##### Response Structure

* `Item` - The Data API Item
	* `Resource` - The Data API Resource for the Item
	* `Metadata` - Metadata associated with the Resource (optional)
* `Master` - Item Master associated with the Item (optional)
	* `Resource` - The Data API Resource for the Master
	* `Metadata` - Metadata associated with the Master Resource (optional)
	
---- 
### get_schema

#### Request Syntax

__HTTP__

```json
http GET https://<data-api>/<stage>/<namespace>/schema/<schema type>

```

__Python Client__

```python
response = client.get_schema(
	data_type: str,
	schema_type: str
)
```

#### Parameters

* `data_type` (string) - The data type/Namespace
* `schema_type` (string) - Schemas can be applied to Resources, Metadata, or both. Use `resource` or `metadata` to fetch the type of schema you are interested in

#### Return Type

JSON - Schema

#### Returns

JSON Schema associated with the Resource or Metadata

##### Response Syntax

```json
{
    "$id": "https://example.com/person.schema.json",
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": <Namespace>,
    "type": "object",
    "properties": {
        <property>: {
            "description": str,
            "type": str
        }
    },
    "required": list,
    "additionalProperties": bool
}
```

##### Response Structure

---- 
### lineage_search

Performs a search on data References using a graph traversal. Depth indicates the number of levels of hierarchy and references to be traversed.

#### Request Syntax

__HTTP__

```json
http GET https://<data-api>/<stage>/<namespace>/<id>

```

__Python Client__

```python
response = client.lineage_search(
	data_type: str, 
	id: str, 
	direction: str, 
	max_depth: int = None
)
```

#### Parameters

* `data_type` - The Data Type/Namespace to perform a lineage search on
* `id` - The Primary Key of the Item you wish to search for References from
* `direction` - Enum indicating the direction of search. `UP`/`DataAPIClient.SEARCH_UPSTREAM` for an upstream search (objects that reference the indicated ID), or `DOWN`/`DataAPIClient.SEARCH_DOWNSTREAM` for a downstream search (objects that the indicated ID references)
* `max_depth` - Depth of the search in generations of References

#### Return Type

List

#### Returns

List of References for the provided Item.

##### Response Syntax

```json
[
    {
        "AdditionalProperties": {
            "date": datetime
        },
        "Label": "References",
        "TypeStage": str,
        "id": str
    }
]
```

##### Response Structure

* List of References
	* Reference
		* `AdditionalProperties` - JSON containing properties attached to the reference
			* `date` - the DateTime that the Reference was created
			* ...
		* `Label` - The type of Reference - defaults to 'References'
		* `TypeStage` - the Namespace and Stage of the Resource which this Reference points to
		* `id` - The Resource ARN of the Item referenced

---- 
### list_items

Lists all Resources in an API Namespace and Stage. This API supports pagination through the use of a `start_token`, and you can access multiple concurrent lists through parallel listings by using `segment` and `total_segment`.

#### Request Syntax

__HTTP__

```json
http GET https://<data-api>/<stage>/<namespace>/list?Limit=int&Segment=int&TotalSegments=int&ExclusiveStartKey=str
```

__Python Client__

```python
response = client.list_items(
	data_type: str, 
	page_size: int = None, 
	start_token: str = None, 
	segment: int = None,
	total_segments: int = None
)
```

#### Parameters

* `data_type` - The Data Type/Namespace
* `page_size` - The number of Items to return in this request
* `start_token` - The continuation token to be used for pagination
* `segment` - When using parallel listings, this value indicates the segment ID that should be returned relative to all segments in the scan
* `total_segments` - When using parallel listings, the number of all segments that will be requested

#### Return Type

JSON - Document

#### Returns

List of Items in the API Namespace given the pagination settings

##### Response Syntax

```json
{
	"Items": [
		{
			<Data API Item>
		},
		...
	],
	"LastEvaluatedKey": {
        <table primary key>: str
    }
}
```

##### Response Structure

* `Items` - List of Data API Items returned by the operation
* `LastEvaluatedKey` - Struct containing the ID of the last item processed by the List page. Match this value to input parameter `start_token`.

---- 
### provision

Creates a new Data API Namespace. This operation is asyncronous and returns immediately. To determine status of provisioning, use `/status` or `get_status()`.

#### Request Syntax

__HTTP__

```json
http PUT https://<data-api>/<stage>/<namespace>/provision
{
	"ApiName": str,
	"PrimaryKey": str,
	"TableIndexes": str,
	"MetadataIndexes": str,		
	"DeleteMode": str (soft | tombstone),
	"CrawlerRolename": str,
	"SchemaValidationRefreshHitCount": int,
	"GremlinAddress": str,
	"NonItemMasterWritesAllowed": bool,	
	"StrictOCCV": str
	"CatalogDatabase": str,	
	"ElasticSearchDomain":str,
	"FirehoseDeliveryIamRoleArn": str,
	"FailedIndexRecordBucket": str,
	"PointInTimeRecoveryEnabled": bool,
	"KMSKeyARN": str
}

```

__Python Client__

```python
response = client.provision(
	data_type, 
	primary_key, 
	table_indexes=None, 
	metadata_indexes=None, 
	delete_mode=None,
	crawler_rolename=None, 
	schema_validation_refresh_hitcount=None,
	graph_endpoint=None, 
	allow_non_item_master_writes=True, 
	strict_occv=False, 
	catalog_database=None,
	es_domain=None, 
	es_delivery_role_arn=None, 
	es_delivery_failure_s3=None, 
	pitr_enabled=True,
	kms_key_arn=None
)
```

#### Parameters

* `data_type | ApiName` - The name of the data type or Namespace to create
* `primary_key` - The Attribute of the object to be used as the primary key
* `table_indexes` - The Attributes and datatypes to be used for Table Indexes. Format is a comman separated list of name value pairs such as `Attribute1=dataType,Attribute2=dataType`. Supported data types are `string`, `number`, `int`, and `bin`.
* `metadata_indexes` - The Attributes and datatypes to be used for Metadata Indexes. CSV formatted string identical to `table_indexes`.
* `delete_mode` - Type of deletes to be performed against the Namespace. `soft` deletes can be restored from the recycle bin, while `tombstone` deletes are permanent.
* `crawler_rolename` - The name of the Role to be used for AWS Glue Schema Crawlers (invoking user must possess `IAM::PassRole` for this role name).
* `schema_validation_refresh_hitcount` - Numeric value indicating the interval that the cache of the Schemas for this Namespace are valid. During this time, Data API operations may use an old verison of the Schema when updates occur. Set this value to a very high number if you don't change the Namespace schema very often.

#### Return Type

#### Returns

##### Response Syntax

```json
{

}
```

##### Response Structure

---- 
### put_info

#### Request Syntax

__HTTP__

```json
http GET https://<data-api>/<stage>/<namespace>/<id>

```

__Python Client__

```python
response = client.<>(
	<>: str
)
```

#### Parameters

#### Return Type

#### Returns

##### Response Syntax

```json
{

}
```

##### Response Structure

---- 
### put_metadata

#### Request Syntax

__HTTP__

```json
http GET https://<data-api>/<stage>/<namespace>/<id>

```

__Python Client__

```python
response = client.<>(
	<>: str
)
```

#### Parameters

#### Return Type

#### Returns

##### Response Syntax

```json
{

}
```

##### Response Structure

---- 
### put_references

#### Request Syntax

__HTTP__

```json
http GET https://<data-api>/<stage>/<namespace>/<id>

```

__Python Client__

```python
response = client.<>(
	<>: str
)
```

#### Parameters

#### Return Type

#### Returns

##### Response Syntax

```json
{

}
```

##### Response Structure

---- 
### put_resource

#### Request Syntax

__HTTP__

```json
http GET https://<data-api>/<stage>/<namespace>/<id>

```

__Python Client__

```python
response = client.<>(
	<>: str
)
```

#### Parameters

#### Return Type

#### Returns

##### Response Syntax

```json
{

}
```

##### Response Structure

---- 
### put_schema

#### Request Syntax

__HTTP__

```json
http GET https://<data-api>/<stage>/<namespace>/<id>

```

__Python Client__

```python
response = client.<>(
	<>: str
)
```

#### Parameters

#### Return Type

#### Returns

##### Response Syntax

```json
{

}
```

##### Response Structure

---- 
### remove\_item\_master

#### Request Syntax

__HTTP__

```json
http GET https://<data-api>/<stage>/<namespace>/<id>

```

__Python Client__

```python
response = client.<>(
	<>: str
)
```

#### Parameters

#### Return Type

#### Returns

##### Response Syntax

```json
{

}
```

##### Response Structure

---- 
### restore_item

#### Request Syntax

__HTTP__

```json
http GET https://<data-api>/<stage>/<namespace>/<id>

```

__Python Client__

```python
response = client.<>(
	<>: str
)
```

#### Parameters

#### Return Type

#### Returns

##### Response Syntax

```json
{

}
```

##### Response Structure

---- 
### set\_item\_master

#### Request Syntax

__HTTP__

```json
http GET https://<data-api>/<stage>/<namespace>/<id>

```

__Python Client__

```python
response = client.<>(
	<>: str
)
```

#### Parameters

#### Return Type

#### Returns

##### Response Syntax

```json
{

}
```

##### Response Structure

---- 
### start_export

#### Request Syntax

__HTTP__

```json
http GET https://<data-api>/<stage>/<namespace>/<id>

```

__Python Client__

```python
response = client.<>(
	<>: str
)
```

#### Parameters

#### Return Type

#### Returns

##### Response Syntax

```json
{

}
```

##### Response Structure

---- 
### understand

#### Request Syntax

__HTTP__

```json
http GET https://<data-api>/<stage>/<namespace>/<id>

```

__Python Client__

```python
response = client.<>(
	<>: str
)
```

#### Parameters

#### Return Type

#### Returns

##### Response Syntax

```json
{

}
```

##### Response Structure

---- 
### validate_item

#### Request Syntax

__HTTP__

```json
http GET https://<data-api>/<stage>/<namespace>/<id>

```

__Python Client__

```python
response = client.<>(
	<>: str
)
```

#### Parameters

#### Return Type

#### Returns

##### Response Syntax

```json
{

}
```

##### Response Structure