# AWS Data API - Python SDK

This project contains a python SDK for [AWS Data API's](https://github.com/awslabs/aws-data-api). Data API's give you the ability to create a new back end web service to handle core business data, without any coding or servers to manage. The Python SDK gives you a client that can create and interact with Data API's using a model similar to the AWS [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) Python SDK.

AWS Data API's use URL Paths and HTTP Verbs to implement underlying actions against your data - for example `HTTP GET` for reads, or `HTTP PUT` for writes. However, the Python SDK provides more user friendly methods - such as `get_item()` or `put_metadata()`.

## Installation

The AWS Data API Python client is distributed only through Github due to an issue with Pypi name squatting. This project is in no way affiliated with the Pypi project `aws-data-api-python-sdk`. To install:

```
git clone aws-data-api-python-sdk
cd aws-data-api-python-sdk
pip install -r requirements.txt
```

this will install:

* `boto3`: The AWS Python SDK which is used for automating credential management.
* `requests-aws4auth`: Helper module that performs sigv4 signing of the requests you make to AWS Data API's
* `shortuuid`: Helper module to generate short, unique addresses

to check that it's installed correctly:

```
aws-data-api-python-sdk meyersi$ python3
Python 3.7.4 (default, Sep  7 2019, 18:27:02)
[Clang 10.0.1 (clang-1001.0.46.4)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import data_api_client as d
>>> print(d.__version__)
0.9.0b1
```

## Setting Up Credentials

Data API Clients use the same process for setting up credentials as the [AWS Python SDK](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html), and the simplest way of setting up credentials can often be to either install the AWS command line client, or to setup and configure boto3. You can use a correctly configured boto3 environment to provide credentials to Data API, or you can explicitly set the access key, secret key, and session token using the control plane and client constructors.

## Linking to Data API Endpoints

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
| `access_key` | The AWS Access Key to be used to call the API Endpoint | No |
| `secret_key` | The AWS Secret Access Key to be used to call the API Endpoint | No |
| `session_token` | The Session Token associated with a temporary STS Token | No |
| `force_refresh` | Boolean value - when True, will force the endpoints.json file to be reloaded from the endpoint. When False, the method will return immediately | No |


For example:

```
access_key = 'MY ACCESS KEY'
secret_key = 'MY SECRET KEY'
session_token = 'SESSION TOKEN'

control_plane.connect(from_url="https://XXXXX.execute-api.eu-west-1.amazonaws.com/dev",
                      access_key=access_key,
                      secret_key=secret_key, 
                      session_token=session_token,
                      force_refresh=True)
```

If you want to see the endpoints for your Client, you can open the `lib/endpoints.json`, which will look something like this:

```
{
    "RefreshDate": "2020-09-02 12:32:13",
    "dev": {
        "DistributionDomainName": "dbfje2qy9pn4z.cloudfront.net",
        "Endpoint": "https://sdma0i6rek.execute-api.eu-west-1.amazonaws.com",
        "Stage": "dev",
        "URL": "https://my-custom-url"
    },
    "test": {
        "Endpoint": "https://txcoxv32dh.execute-api.eu-west-1.amazonaws.com",
        "Stage": "test"
    }
}

```

These are the internal GUID addresses per-stage that your client will connect to. If you prefer, you can also create this file manually or download it from a separate storage medium.

## Creating a Client

Once the client environment is linked to your Endpoints, you can create a Client for the required Region and Stage:

```
my_client = DataAPIClient(
	stage: str, 
	region_name: str = None, 
	access_key: str = None, 
	secret_key: str = None,
	session_token: str = None
	service_endpoint: str = None, 
	tls: bool = True
)
```
| Arg | Purpose | Required |
| --- | ------- | -------- |
|`stage` | Links the Client to the specified Stage of the API, such as 'dev', or 'test', thus setting the endpoint that is called. | Yes |
|`region_name`| The AWS Short Region in which you are connecting. Used for SigV4 signing of requests. If not supplied, then environment `AWS_REGION` will be used. | No |
| `access_key` | The AWS Access Key to be used to call the API Endpoint | No |
| `secret_key` | The AWS Secret Access Key to be used to call the API Endpoint | No |
| `session_token` | The Session Token associated with a temporary STS Token | No |
| `service_endpoint` | Allows you to ignore the cached endpoint configuration, and connect your client to a specific endpoint. Intended for testing purposes. | No |
| `tls` | Specifies whether TLS is used to connect to the API. Turned on by default, but can be switched off for local testing | No |

## Calling Client Methods

You can call any of the [client methods](CallingMethods.md) directly, without considering authentication & authorisation, or HTTP methods and paths.


