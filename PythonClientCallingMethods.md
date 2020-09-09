# Working with Data API's

Once you have created a Client, you can start calling methods on your Data API. Each method in the client requires that you specify a `data_type`, which is a reference to the [Namespace](Concepts) you want to work with. You can discover all of the available Namespaces that the Data API you are connected to can support with the `get_namespaces()` method.

## Client

_class_ `DataAPIClient`

Class representing a connection to a Data API Stage.

```python
from lib.data_api_control_plane import DataApiControlPlane
from data_api_client import DataAPIClient

# get the region from the environment - connecting locally
region = os.getenv("AWS_REGION")

# create a control plane reference
control_plane = DataApiControlPlane(tls=True, region_name=region)

# One time setup of the endpoint cache
control_plane.connect(from_url=endpoint,
                      access_key=access_key,
                      secret_key=secret_key, session_token=session_token,
                  	  force_refresh=True)

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
### delete_attributes(**kwargs)

Method that enables you to delete specific Attributes from a Resource or Metadata item.

#### Request Syntax

```
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

dict

#### Returns

##### Response Syntax

```
{
	"DataModified": "boolean"
}
```

##### Response Structure

* dict - 
	* `DataModified` - Boolean indicator of if the Attributes were deleted

---- 
### delete_metadata(**kwargs)

Method that deletes Metadata for an Item.

#### Request Syntax

```
response = client.delete_metadata(
	data_type: str, 
	id: str
)
```

#### Parameters

* `data_type` (string) - The data type/Namespace
* `id` (string) - The ID of the Item to be modified

#### Return Type

dict

#### Returns

##### Response Syntax

```
{
	"DataModified": "boolean"
}
```

##### Response Structure

* dict - 
	* `DataModified` - Boolean indicator of if the Attributes were deleted

---- 
### delete_resource(**kwargs)

Deletes a Resource and it's associated Metadata.

#### Request Syntax

```
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

dict

#### Returns

##### Response Syntax

```
{
	"DataModified": "boolean"
}
```

##### Response Structure

* dict - 
	* `DataModified` - Boolean indicator of if the Attributes were deleted
	
---- 
### delete_schema(**kwargs)

Removes the Schema for Resources or Metadata from a Namespace (requires elevated privileges).

#### Request Syntax

```
response = client.delete_schema(
	data_type: str, 
	schema_type: str
)
```

#### Parameters

* `data_type` (string) - The data type/Namespace
* `schema_type` (string) - The schema type to remove. Must be one of `resource` or `metadata`.

#### Return Type

dict

#### Returns

##### Response Syntax

```
{
	"DataModified": "boolean"
}
```

##### Response Structure

* dict - 
	* `DataModified` - Boolean indicator of if the Attributes were deleted


---- 
### find(**kwargs)

Performs a search for an Item based upon Attribute values provided.

#### Request Syntax

```
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

dict

#### Returns

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

* dict - 
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
### get_endpoints(**kwargs)

Returns the endpoint addresses of the resources used by a namespace. This includes the Resource and Metadata stream addresses, and the ElasticSearch and Neptune configurations if they have been provisioned.

#### Request Syntax

```
response = client.get_endpoints(
	data_type: str
)
```

#### Parameters

* `data_type` (string) - The data type/Namespace

#### Return Type

dict

#### Returns

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
### get\_export\_status(**kwargs)

Returns the status of a data export job (export to S3).

#### Request Syntax

```
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

#### Returns

##### Response Syntax

##### Response Structure

---- 
### get_info(**kwargs)

#### Request Syntax

#### Parameters

#### Return Type

#### Returns

##### Response Syntax

##### Response Structure

---- 
### get_metadata(**kwargs)

#### Request Syntax

#### Parameters

#### Return Type

#### Returns

##### Response Syntax

##### Response Structure

---- 
### get_namespaces(**kwargs)

#### Request Syntax

#### Parameters

#### Return Type

#### Returns

##### Response Syntax

##### Response Structure

---- 
### get_resource(**kwargs)

#### Request Syntax

#### Parameters

#### Return Type

#### Returns

##### Response Syntax

##### Response Structure

---- 
### get_schema(**kwargs)

#### Request Syntax

#### Parameters

#### Return Type

#### Returns

##### Response Syntax

##### Response Structure

---- 
### lineage_search(**kwargs)

#### Request Syntax

#### Parameters

#### Return Type

#### Returns

##### Response Syntax

##### Response Structure

---- 
### list_items(**kwargs)

#### Request Syntax

#### Parameters

#### Return Type

#### Returns

##### Response Syntax

##### Response Structure

---- 
### provision(**kwargs)

#### Request Syntax

#### Parameters

#### Return Type

#### Returns

##### Response Syntax

##### Response Structure

---- 
### put_info(**kwargs)

#### Request Syntax

#### Parameters

#### Return Type

#### Returns

##### Response Syntax

##### Response Structure

---- 
### put_metadata(**kwargs)

#### Request Syntax

#### Parameters

#### Return Type

#### Returns

##### Response Syntax

##### Response Structure

---- 
### put_references(**kwargs)

#### Request Syntax

#### Parameters

#### Return Type

#### Returns

##### Response Syntax

##### Response Structure

---- 
### put_resource(**kwargs)

#### Request Syntax

#### Parameters

#### Return Type

#### Returns

##### Response Syntax

##### Response Structure

---- 
### put_schema(**kwargs)

#### Request Syntax

#### Parameters

#### Return Type

#### Returns

##### Response Syntax

##### Response Structure

---- 
### remove\_item\_master(**kwargs)

#### Request Syntax

#### Parameters

#### Return Type

#### Returns

##### Response Syntax

##### Response Structure

---- 
### restore_item(**kwargs)

#### Request Syntax

#### Parameters

#### Return Type

#### Returns

##### Response Syntax

##### Response Structure

---- 
### set\_item\_master(**kwargs)

#### Request Syntax

#### Parameters

#### Return Type

#### Returns

##### Response Syntax

##### Response Structure

---- 
### start_export(**kwargs)

#### Request Syntax

#### Parameters

#### Return Type

#### Returns

##### Response Syntax

##### Response Structure

---- 
### understand(**kwargs)

#### Request Syntax

#### Parameters

#### Return Type

#### Returns

##### Response Syntax

##### Response Structure

---- 
### validate_item(**kwargs)

#### Request Syntax

#### Parameters

#### Return Type

#### Returns

##### Response Syntax

##### Response Structure