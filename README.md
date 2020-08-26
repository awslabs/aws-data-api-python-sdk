# AWS Data API - Python SDK

This project contains a python SDK for [AWS Data API's](https://github.com/IanMeyers/aws-data-api). Data API's give you the ability to create a new back end web service to handle core business data, without any coding or servers to manage. The Python SDK gives you a client that can create and interact with Data API's using a model similar to the AWS [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) Python SDK.

AWS Data API's use URL Paths and HTTP Verbs to implement underlying actions against your data - for example `HTTP GET` for reads, or `HTTP PUT` for writes. However, the Python SDK provides more user friendly methods - such as `get_item()` or `put_metadata()`.

## Installation

To install the Data API, either clone this repo and add to your `PYTHONPATH`, or run:

`pip3 install aws-data-api-python-sdk`

to check that it's installed correctly:

```
aws-data-api-python-sdk meyersi$ python3
Python 3.7.4 (default, Sep  7 2019, 18:27:02)
[Clang 10.0.1 (clang-1001.0.46.4)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import data_api_client as d
>>> print(d.__version__)
0.9.0
```

## Setting Up Credentials

Data API Clients use the same process for setting up credentials as the [AWS Python SDK](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html), and the simplest way of setting up credentials can often be to either install the AWS command line client, or to setup and configure boto3.

## Creating a Data API Client

To create a Data API Client, you must:

* Import the module
* Perform a one-time connection to the Endpoint addresses in your Account
* Instantiate the client

### Linking to Data API Endpoints

API endpoints for your client are cached in a local file, and can be refreshed at any time. Initially the endpoint addresses are not installed, and so you need to load them. To do this, we will create a Data API 'Control Plane' helper, and use it to build our connection set:

```
from lib.data_api_control_plane import DataApiControlPlane
region = os.getenv("AWS_REGION")
control_plane = DataApiControlPlane(tls=True, region_name=region)
```

Then we need to call the connect method:

```
def connect(from_url: str, 
			access_key: str, 
			secret_key: str, 
			session_token: str,
			force_refresh: bool = False
)
```

| Arg | Purpose | Required |
| --- | ------- | -------- |
| `from_url` | URL used to link your client environment to all Stages in an Account. This URL can be any valid Data API endpoint in your Account - any any Stage | Yes |
| `access_key` | The AWS Access Key to be used to call the API Endpoint | Yes |
| `secret_key` | The AWS Secrete Access Key to be used to call the API Endpoint | Yes |
| `session_token` | The Session Token associated with a temporary STS Token | No |
| `force_refresh` | Boolean value - when True, will force the endpoints.json file to be reloaded from the endpoint. When False, the method will return immediately | No |


For example:

```
access_key = os.getenv("aws_access_key_id")
secret_key = os.getenv("aws_secret_access_key")
session_token = os.getenv("aws_session_token")
control_plane.connect(from_url="https://XXXXX.execute-api.eu-west-1.amazonaws.com/dev",
                      access_key=access_key,
                      secret_key=secret_key, 
                      session_token=session_token,
                      force_refresh=True)
```

If you want to see the endpoints for your Client, you can open the `lib/endpoints.json`, which will look something like this:

```
{
    "dev": "dm8906f6ae",
    "test": "txcoxv32dh"
}

```

These are the internal GUID addresses per-stage that your client will connect to - for example `https://txcoxv32dh.execute-api.eu-west-1.amazonaws.com/test`. If you prefer, you can also create this file manually or download it from a separate storage medium.

## Creating a Client

Now that you have linked your client environment to your Account, you can create a Client for the required Region and Stage:

```
my_client = DataAPIClient(
	stage: str, 
	region_name: str = None, 
	credentials: dict = None,
	service_endpoint: str = None, 
	tls: bool = True
)
```
| Arg | Purpose | Required |
| --- | ------- | -------- |
|`stage` | Links the Client to the specified Stage of the API, such as 'dev', or 'test', thus setting the endpoint that is called. | Yes |
|`region_name`| The AWS Short Region in which you are connecting. Used for SigV4 signing of requests. If not supplied, then environment `AWS_REGION` will be used. | No |
|`credentials` | Configuration object that allows you to use an underlying boto3 configuration as the connection provider. If omitted, then Environment Variables `aws_access_key_id`, `aws_secret_access_key`, and `aws_session_token` will be used. | No |
| `service_endpoint` | Allows you to ignore the cached endpoint configuration, and connect your client to a specific endpoint. Intended for testing purposes. | No |
| `tls` | Specifies whether TLS is used to connect to the API. Turned on by default, but can be switched off for local testing | No |

## Calling Client Methods

Please see our [pydocs](https://htmlpreview.github.io/?doc/data_api_client.html).