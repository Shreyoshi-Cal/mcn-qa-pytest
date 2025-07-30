"""
AWS VPC Creation Test Steps - Single Scenario

API Endpoints:
  • POST    /cloud/vpc                        create a VPC

Model for VPC Creation:
{
  "cidrBlock": "string",
  "cloudAccountId": 0,
  "cloudProvider": "aws",
  "cloudRegion": "string",
  "cloudResourceGroup": "string",
  "name": "string",
  "stackName": "string",
  "tags": {
    "additionalProp1": "string",
    "additionalProp2": "string",
    "additionalProp3": "string"
  }
}
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict

import requests
from pytest_bdd import given, when, then, scenarios, parsers


logger = logging.getLogger(__name__)

mcn: Dict[str, Any] = {}           
vpc_data: Dict[str, Any] = {}      
response_data: Dict[str, requests.Response] = {}  


scenarios("../vpc_create.feature")


@given("I have a registered AWS account")
def given_registered_aws_account() -> None:
    """Put an AWS account id into the global state, validate with match/case."""
    mcn["aws_id"] = "1"         
    match mcn:
        case {"aws_id": str(acc_id)} if acc_id:
            logger.info(f"✓ AWS account id configured: {acc_id}")
        case _:
            assert False, "AWS account id must be present and non-empty"


@given("the AWS API is accessible")
def given_api_accessible(izo_mcn_url) -> None:
    """Best-effort health probe; does not fail test if /health is absent."""
    health_url = f"{izo_mcn_url}/health"

    try:
        resp = requests.get(health_url, timeout=5)
        logger.info(f"Health probe {health_url} → {resp.status_code}")
        
        match resp.status_code:
            case 200:
                logger.info("✓ AWS API is healthy")
            case 404:
                logger.info("Health endpoint not found for AWS (acceptable)")
            case code if 400 <= code < 500:
                logger.warning(f"AWS health check returned client error {code}")
            case code if code >= 500:
                logger.warning(f"AWS health check returned server error {code}")
            case _:
                logger.warning(f"AWS health check returned unexpected status {resp.status_code}")
                
    except requests.exceptions.RequestException as exc:
        logger.warning(f"AWS health check failed: {exc}")


@given("the VPC details are:")
def given_vpc_details(docstring) -> None:
    # inside given_vpc_details(docstring):

    auto_name  = os.getenv("VPC_BULK_NAME")
    auto_cidr  = os.getenv("VPC_BULK_CIDR")
    auto_stack = os.getenv("VPC_BULK_STACK")

    if auto_name and auto_cidr and auto_stack:
        raw = f"""
        cidrBlock={auto_cidr}
        cloudAccountId=1
        cloudProvider=aws
        cloudRegion=us-east-1
        cloudResourceGroup=
        name={auto_name}
        stackName={auto_stack}
        tagName={auto_name}
        """.strip()
        docstring=raw
        
    global vpc_data
    vpc_data.clear()

    for raw in docstring.strip().splitlines():
        if "=" not in raw:
            continue

        key, val = (part.strip() for part in raw.split("=", 1))

        match key:
            case "cloudAccountId":
                vpc_data[key] = int(val) if val else int(mcn.get("aws_id", 1))
            case "tagName":
                vpc_data.setdefault("tags", {})["Name"] = val
            case "cloudResourceGroup" if not val:
                vpc_data[key] = ""
            case "cloudProvider":
                vpc_data[key] = val if val else "aws"
            case "cloudRegion":
                vpc_data[key] = val
                mcn["vpc_region"] = val  
            case _:
                vpc_data[key] = val

    
    vpc_data.setdefault("cloudAccountId", int(mcn.get("aws_id", 1)))
    vpc_data.setdefault("cloudProvider", "aws")
    vpc_data.setdefault("cloudResourceGroup", "")
    vpc_data.setdefault("cloudRegion", "us-east-1")
    
    
    mcn["vpc_region"] = vpc_data.get("cloudRegion", "us-east-1")

    match vpc_data:
        case dict() if vpc_data:
            logger.info("✓ Parsed VPC payload:\n%s",
                        json.dumps(vpc_data, indent=2, default=str))
        case _:
            assert False, "VPC details table was empty"

# ------------------------------------------------------------------------------
#  WHEN STEPS
# ------------------------------------------------------------------------------
@when("I send a POST request to create a VPC on AWS")
def when_post_create_vpc(izo_mcn_url, default_headers) -> None:
    """Send POST request to create VPC on AWS and capture VPC ID for logging"""
    url = f"{izo_mcn_url}/cloud/vpc"
    logger.info(f" Initiating VPC creation request")
    logger.info(f" Endpoint: {url}")
    logger.info(f" Request headers: {json.dumps(default_headers, indent=2)}")
    logger.info(f" VPC creation payload:\n{json.dumps(vpc_data, indent=2)}")

    try:
        response_data["response"] = requests.post(
            url,
            headers=default_headers,
            data=json.dumps(vpc_data)
        )
        
        logger.info(f" Response Status: {response_data['response'].status_code}")
        logger.info(f" Response Body: {response_data['response'].text}")
        
        
        if response_data["response"].status_code == 200:
            logger.info(" VPC creation request completed successfully")
        else:
            logger.warning(f"  VPC creation returned non-200 status: {response_data['response'].status_code}")
            
    except requests.exceptions.RequestException as exc:
        logger.error(f" VPC creation request failed with exception: {exc}")
        raise

# ------------------------------------------------------------------------------
#  THEN STEPS – status code verification
# ------------------------------------------------------------------------------
def _assert_status(expected: int) -> None:
    """Verify the API response status code using match/case"""
    actual = response_data["response"].status_code
    response_body = response_data["response"].text

    match actual:
        case code if code == expected:
            logger.info(f" Response status code validation passed: {code}")
        case 400:
            assert False, f"Bad Request (400): Invalid VPC configuration. Response: {response_body}"
        case 401:
            assert False, f"Unauthorized (401): Check authentication headers"
        case 403:
            assert False, f"Forbidden (403): Insufficient permissions for VPC creation"
        case 404:
            assert False, f"Not Found (404): API endpoint not found"
        case 409:
            assert False, f"Conflict (409): VPC already exists or naming conflict. Response: {response_body}"
        case 500:
            assert False, f"Internal Server Error (500): {response_body}"
        case code if code >= 500:
            assert False, f"Server Error ({code}): {response_body}"
        case _:
            assert False, f"Expected status {expected}, got {actual}. Response: {response_body}"


@then(parsers.cfparse("the AWS VPC creation API response should be {status_code:d}"))
def then_create_status(status_code: int) -> None:
    """Verify VPC creation response status code"""
    logger.info(f"🔍 Validating VPC creation response status code")
    _assert_status(status_code)

# ------------------------------------------------------------------------------
#  THEN STEPS – body-content assertions with enhanced VPC ID logging
# ------------------------------------------------------------------------------
@then("the AWS VPC creation API response body must contain a VPC ID")
def then_body_contains_vpc_id() -> None:
    """
    Verify response contains VPC ID using match/case patterns with comprehensive logging
    Returns the VPC ID in logs for easy identification and tracking
    """
    logger.info(" Analyzing VPC creation response for VPC ID extraction")
    
    try:
        resp_json = response_data["response"].json()
        logger.info(f" Full API response structure:\n{json.dumps(resp_json, indent=2)}")
    except json.JSONDecodeError:
        response_body = response_data["response"].text
        logger.error(f" Response is not valid JSON: {response_body}")
        assert False, f"Response is not valid JSON: {response_body}"

    vpc_id: str | None = None
    extraction_method: str = ""

    match resp_json:
        
        case {"id": str(id_val)} if id_val.strip():
            vpc_id = id_val.strip()
            extraction_method = "direct 'id' field"
        case {"vpcId": str(vpc_val)} if vpc_val.strip():
            vpc_id = vpc_val.strip()
            extraction_method = "direct 'vpcId' field"
        
        case {"data": {"id": str(id_val)}} if id_val.strip():
            vpc_id = id_val.strip()
            extraction_method = "nested 'data.id' field"
        case {"data": {"vpcId": str(vpc_val)}} if vpc_val.strip():
            vpc_id = vpc_val.strip()
            extraction_method = "nested 'data.vpcId' field"
        
        case dict() as body:
            logger.info(" Performing fallback search for VPC ID in response")
            for field in ("id", "vpcId"):
                match body.get(field):
                    case str(x) if x.strip():
                        vpc_id = x.strip()
                        extraction_method = f"fallback direct '{field}' field"
                        break
                    case _:
                        
                        if "data" in body and isinstance(body["data"], dict):
                            match body["data"].get(field):
                                case str(x) if x.strip():
                                    vpc_id = x.strip()
                                    extraction_method = f"fallback nested 'data.{field}' field"
                                    break
                                case _:
                                    continue
        case _:
            logger.warning("  Response structure doesn't match expected patterns")

    match vpc_id:
        case str(v) if v and v.startswith("vpc-"):
            
            mcn["aws_vpc_id"] = v
            
            
            logger.info("="*60)
            logger.info(" VPC CREATION SUCCESSFUL!")
            logger.info("="*60)
            logger.info(f" VPC ID: {v}")
            logger.info(f" Region: {mcn.get('vpc_region', 'us-east-1')}")
            logger.info(f"  VPC Name: {vpc_data.get('name', 'N/A')}")
            logger.info(f" CIDR Block: {vpc_data.get('cidrBlock', 'N/A')}")
            logger.info(f" Account ID: {vpc_data.get('cloudAccountId', 'N/A')}")
            logger.info(f"  Provider: {vpc_data.get('cloudProvider', 'N/A')}")
            logger.info(f" Stack Name: {vpc_data.get('stackName', 'N/A')}")
            logger.info(f" Extraction Method: {extraction_method}")
            logger.info("="*60)
            
            
            logger.info(f"VPC_CREATED|ID={v}|REGION={mcn.get('vpc_region', 'us-east-1')}|NAME={vpc_data.get('name', 'N/A')}", flush=True)
            
        case str(v) if v:
            logger.warning(f"Found ID but doesn't match VPC format: {v}")
            assert False, f"Found ID '{v}' but it doesn't match expected VPC ID format (vpc-xxxxxxxxx)"
        case _:
            logger.error(" VPC ID extraction failed")
            logger.error(f" Response analysis:")
            logger.error(f"   - Response type: {type(resp_json)}")
            logger.error(f"   - Response keys: {list(resp_json.keys()) if isinstance(resp_json, dict) else 'Not a dict'}")
            logger.error(f"   - Full response: {json.dumps(resp_json, indent=2)}")
            assert False, (
                f"VPC ID not found in response. "
                f"Response: {json.dumps(resp_json, indent=2)}"
            )


@then("cleanup any created AWS VPC resources")
def then_cleanup_log() -> None:
    """Log created VPC resources for cleanup tracking"""
    match mcn:
        case {"aws_vpc_id": str(vpc_id)} if vpc_id:
            logger.info("="*50)
            logger.info(" CLEANUP TRACKING")
            logger.info("="*50)
            logger.info(f" VPC ID Created: {vpc_id}")
            logger.info(f" Region: {mcn.get('vpc_region', 'us-east-1')}")
            logger.info(f"  VPC Name: {vpc_data.get('name', 'N/A')}")
            logger.info("  Note: Manual cleanup may be required")
            logger.info("="*50)
            
            
            logger.info(f"CLEANUP_REQUIRED|VPC_ID={vpc_id}|REGION={mcn.get('vpc_region', 'us-east-1')}")
        case _:
            logger.info("  No AWS VPC resources created to track for cleanup")



'''

from __future__ import annotations

import json
import logging
from typing import Any, Dict

import requests
from pytest_bdd import given, when, then, scenarios, parsers

# ------------------------------------------------------------------------------
#  Constants & shared state
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)

mcn: Dict[str, Any] = {}           # e.g. {"aws_id": "1", "aws_vpc_id": "vpc-123", "vpc_region": "us-east-1"}
vpc_data: Dict[str, Any] = {}      # payload for create
response_data: Dict[str, requests.Response] = {}  # last HTTP response

# Register all scenarios in the same directory
scenarios("../vpc_create.feature")

# ------------------------------------------------------------------------------
#  GIVEN STEPS
# ------------------------------------------------------------------------------
@given("I have a registered AWS account")
def given_registered_aws_account() -> None:
    """Put an AWS account id into the global state, validate with match/case."""
    mcn["aws_id"] = "1"         # AWS account id for tests

    match mcn:
        case {"aws_id": str(acc_id)} if acc_id:
            logger.info(f"✓ AWS account id configured: {acc_id}")
        case _:
            assert False, "AWS account id must be present and non-empty"


@given("the AWS API is accessible")
def given_api_accessible(izo_mcn_url) -> None:
    """Best-effort health probe; does not fail test if /health is absent."""
    health_url = f"{izo_mcn_url}/health"

    try:
        resp = requests.get(health_url, timeout=5)
        logger.info(f"Health probe {health_url} → {resp.status_code}")
        
        match resp.status_code:
            case 200:
                logger.info("✓ AWS API is healthy")
            case 404:
                logger.info("Health endpoint not found for AWS (acceptable)")
            case code if 400 <= code < 500:
                logger.warning(f"AWS health check returned client error {code}")
            case code if code >= 500:
                logger.warning(f"AWS health check returned server error {code}")
            case _:
                logger.warning(f"AWS health check returned unexpected status {resp.status_code}")
                
    except requests.exceptions.RequestException as exc:
        logger.warning(f"AWS health check failed: {exc}")


@given("the VPC details are:")
def given_vpc_details(docstring) -> None:
    """
    Convert the multi-line table in the feature file to a dict matching the API model.

    Each line is key=value; blank values are allowed.
    Special handling:
      • tagName → tags = {"Name": "<value>"}
      • cloudAccountId – cast to int
      • cloudProvider – defaults to "aws"
    """
    global vpc_data
    vpc_data.clear()

    for raw in docstring.strip().splitlines():
        if "=" not in raw:
            continue

        key, val = (part.strip() for part in raw.split("=", 1))

        match key:
            case "cloudAccountId":
                vpc_data[key] = int(val) if val else int(mcn.get("aws_id", 1))
            case "tagName":
                vpc_data.setdefault("tags", {})["Name"] = val
            case "cloudResourceGroup" if not val:
                vpc_data[key] = ""
            case "cloudProvider":
                vpc_data[key] = val if val else "aws"
            case "cloudRegion":
                vpc_data[key] = val
                mcn["vpc_region"] = val  # Store region for delete operation
            case _:
                vpc_data[key] = val

    # Ensure required fields are present with defaults
    vpc_data.setdefault("cloudAccountId", int(mcn.get("aws_id", 1)))
    vpc_data.setdefault("cloudProvider", "aws")
    vpc_data.setdefault("cloudResourceGroup", "")
    vpc_data.setdefault("cloudRegion", "us-east-1")
    
    # Ensure region is stored in mcn for deletion
    mcn["vpc_region"] = vpc_data.get("cloudRegion", "us-east-1")

    match vpc_data:
        case dict() if vpc_data:
            logger.info("✓ Parsed VPC payload:\n%s",
                        json.dumps(vpc_data, indent=2, default=str))
        case _:
            assert False, "VPC details table was empty"

# ------------------------------------------------------------------------------
#  WHEN STEPS
# ------------------------------------------------------------------------------
@when("I send a POST request to create a VPC on AWS")
def when_post_create_vpc(izo_mcn_url, default_headers) -> None:
    """Send POST request to create VPC on AWS"""
    url = f"{izo_mcn_url}/cloud/vpc"
    logger.info(f"Sending POST request to: {url}")
    logger.info(f"Payload: {json.dumps(vpc_data, indent=2)}")

    response_data["response"] = requests.post(
        url,
        headers=default_headers,
        data=json.dumps(vpc_data)
    )

    logger.info(f"Response Status: {response_data['response'].status_code}")
    logger.info(f"Response Body: {response_data['response'].text}")


@when("I send a DELETE request to delete an AWS VPC with payload")
def when_delete_vpc_with_payload(izo_mcn_url, vpc_id_for_deletion, default_headers) -> None:
    
    vpc_id = vpc_id_for_deletion if vpc_id_for_deletion else mcn.get("aws_vpc_id")
    logger.info(f"Resolved VPC ID: {vpc_id} (from {'environment' if vpc_id_for_deletion else 'memory'})")

    match vpc_id:
        case str(vpc) if vpc and vpc.startswith("vpc-") and len(vpc) > 10:
            # Use stored region from VPC creation or default
            vpc_region = mcn.get("vpc_region", "us-east-1")
            
            # Prepare the delete payload based on the API model
            delete_payload = {
                "cloudAccountId": int(mcn.get("aws_id", 1)),
                "cloudProvider": "aws",
                "cloudRegion": vpc_region
            }
            
            url = f"{izo_mcn_url}/cloud/vpc/{vpc}"
            logger.info(f"Sending DELETE request to: {url}")
            logger.info(f"VPC ID being deleted: {vpc}")
            logger.info(f"Region for deletion: {vpc_region}")
            logger.info(f"Delete payload: {json.dumps(delete_payload, indent=2)}")
            
            response_data["response"] = requests.delete(
                url,
                headers=default_headers,
                data=json.dumps(delete_payload)
            )
            
            logger.info(f"Response Status: {response_data['response'].status_code}")
            logger.info(f"Response Body: {response_data['response'].text}")
        case _:
            assert False, f"Invalid or missing VPC ID. Environment: '{vpc_id_for_deletion}', Memory: '{mcn.get('aws_vpc_id')}'"


# ------------------------------------------------------------------------------
#  THEN STEPS – status code verification
# ------------------------------------------------------------------------------
def _assert_status(expected: int) -> None:
    """Verify the API response status code using match/case"""
    actual = response_data["response"].status_code
    response_body = response_data["response"].text

    match actual:
        case code if code == expected:
            logger.info(f"✓ Response status code is {code}")
        case 400:
            assert False, f"Bad Request (400): Invalid VPC configuration. Response: {response_body}"
        case 401:
            assert False, f"Unauthorized (401): Check authentication headers"
        case 403:
            assert False, f"Forbidden (403): Insufficient permissions for VPC creation"
        case 404:
            assert False, f"Not Found (404): API endpoint not found"
        case 409:
            assert False, f"Conflict (409): VPC already exists or naming conflict. Response: {response_body}"
        case 500:
            assert False, f"Internal Server Error (500): {response_body}"
        case code if code >= 500:
            assert False, f"Server Error ({code}): {response_body}"
        case _:
            assert False, f"Expected status {expected}, got {actual}. Response: {response_body}"


@then(parsers.cfparse("the AWS VPC creation API response should be {status_code:d}"))
def then_create_status(status_code: int) -> None:
    """Verify VPC creation response status code"""
    _assert_status(status_code)


@then(parsers.cfparse("the AWS VPC deletion API response should be {status_code:d}"))
def then_delete_status(status_code: int) -> None:
    """Verify VPC deletion response status code"""
    _assert_status(status_code)

# ------------------------------------------------------------------------------
#  THEN STEPS – body-content assertions
# ------------------------------------------------------------------------------
@then("the AWS VPC creation API response body must contain a VPC ID")
def then_body_contains_vpc_id() -> None:
    """Verify response contains VPC ID using match/case patterns"""
    try:
        resp_json = response_data["response"].json()
    except json.JSONDecodeError:
        response_body = response_data["response"].text
        assert False, f"Response is not valid JSON: {response_body}"

    vpc_id: str | None = None

    match resp_json:
        # Direct fields in response
        case {"id": str(id_val)} if id_val.strip():
            vpc_id = id_val.strip()
        case {"vpcId": str(vpc_val)} if vpc_val.strip():
            vpc_id = vpc_val.strip()
        # Nested under data object
        case {"data": {"id": str(id_val)}} if id_val.strip():
            vpc_id = id_val.strip()
        case {"data": {"vpcId": str(vpc_val)}} if vpc_val.strip():
            vpc_id = vpc_val.strip()
        # Fallback search for additional patterns
        case dict() as body:
            for field in ("id", "vpcId"):
                match body.get(field):
                    case str(x) if x.strip():
                        vpc_id = x.strip()
                        break
                    case _:
                        # Check nested data
                        if "data" in body and isinstance(body["data"], dict):
                            match body["data"].get(field):
                                case str(x) if x.strip():
                                    vpc_id = x.strip()
                                    break
                                case _:
                                    continue
        case _:
            pass

    match vpc_id:
        case str(v) if v:
            mcn["aws_vpc_id"] = v
            logger.info(f"✓ VPC ID found: {v}")
        case _:
            assert False, (
                f"VPC ID not found in response. "
                f"Response: {json.dumps(resp_json, indent=2)}"
            )


@then(parsers.cfparse("the AWS VPC deletion API response body must contain {msg}"))
def then_delete_body_contains(msg: str) -> None:
    """Verify VPC deletion response contains specified message"""
    body_text = response_data["response"].text

    match body_text:
        case text if msg in text:
            logger.info(f"✓ Expected message '{msg}' found in deletion response")
        case _:
            assert False, f"Expected message '{msg}' not found in response: {body_text}"


@then("cleanup any created AWS VPC resources")
def then_cleanup_log() -> None:
    """Log created VPC resources for cleanup"""
    match mcn:
        case {"aws_vpc_id": str(vpc_id)} if vpc_id:
            logger.info(f"✓ AWS VPC created with ID: {vpc_id}")
            logger.info("Note: Manual cleanup may be required")
        case _:
            logger.info("No AWS VPC resources to cleanup")'''








'''from __future__ import annotations

import json
import logging
from typing import Any, Dict

import requests
from pytest_bdd import given, when, then, scenarios, parsers

# ------------------------------------------------------------------------------
#  Constants & shared state
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)

mcn: Dict[str, Any] = {}           # e.g. {"aws_id": "1", "aws_vpc_id": "vpc-123"}
vpc_data: Dict[str, Any] = {}      # payload for create
response_data: Dict[str, requests.Response] = {}  # last HTTP response

# Register all scenarios in the same directory
scenarios("../vpc_create.feature")

# ------------------------------------------------------------------------------
#  GIVEN STEPS
# ------------------------------------------------------------------------------
@given("I have a registered AWS account")
def given_registered_aws_account() -> None:
    """Put an AWS account id into the global state, validate with match/case."""
    mcn["aws_id"] = "1"         # AWS account id for tests

    match mcn:
        case {"aws_id": str(acc_id)} if acc_id:
            logger.info(f"✓ AWS account id configured: {acc_id}")
        case _:
            assert False, "AWS account id must be present and non-empty"


@given("the AWS API is accessible")
def given_api_accessible(izo_mcn_url) -> None:
    """Best-effort health probe; does not fail test if /health is absent."""
    health_url = f"{izo_mcn_url}/health"

    try:
        resp = requests.get(health_url, timeout=5)
        logger.info(f"Health probe {health_url} → {resp.status_code}")
        
        match resp.status_code:
            case 200:
                logger.info("✓ AWS API is healthy")
            case 404:
                logger.info("Health endpoint not found for AWS (acceptable)")
            case code if 400 <= code < 500:
                logger.warning(f"AWS health check returned client error {code}")
            case code if code >= 500:
                logger.warning(f"AWS health check returned server error {code}")
            case _:
                logger.warning(f"AWS health check returned unexpected status {resp.status_code}")
                
    except requests.exceptions.RequestException as exc:
        logger.warning(f"AWS health check failed: {exc}")


@given("the VPC details are:")
def given_vpc_details(docstring) -> None:
    """
    Convert the multi-line table in the feature file to a dict matching the API model.

    Each line is key=value; blank values are allowed.
    Special handling:
      • tagName → tags = {"Name": "<value>"}
      • cloudAccountId – cast to int
      • cloudProvider – defaults to "aws"
    """
    global vpc_data
    vpc_data.clear()

    for raw in docstring.strip().splitlines():
        if "=" not in raw:
            continue

        key, val = (part.strip() for part in raw.split("=", 1))

        match key:
            case "cloudAccountId":
                vpc_data[key] = int(val) if val else int(mcn.get("aws_id", 1))
            case "tagName":
                vpc_data.setdefault("tags", {})["Name"] = val
            case "cloudResourceGroup" if not val:
                vpc_data[key] = ""
            case "cloudProvider":
                vpc_data[key] = val if val else "aws"
            case _:
                vpc_data[key] = val

    # Ensure required fields are present with defaults
    vpc_data.setdefault("cloudAccountId", int(mcn.get("aws_id", 1)))
    vpc_data.setdefault("cloudProvider", "aws")
    vpc_data.setdefault("cloudResourceGroup", "")

    match vpc_data:
        case dict() if vpc_data:
            logger.info("✓ Parsed VPC payload:\n%s",
                        json.dumps(vpc_data, indent=2, default=str))
        case _:
            assert False, "VPC details table was empty"

# ------------------------------------------------------------------------------
#  WHEN STEPS
# ------------------------------------------------------------------------------
@when("I send a POST request to create a VPC on AWS")
def when_post_create_vpc(izo_mcn_url, default_headers) -> None:
    """Send POST request to create VPC on AWS"""
    url = f"{izo_mcn_url}/cloud/vpc"
    logger.info(f"Sending POST request to: {url}")
    logger.info(f"Payload: {json.dumps(vpc_data, indent=2)}")

    response_data["response"] = requests.post(
        url,
        headers=default_headers,
        data=json.dumps(vpc_data)
    )

    logger.info(f"Response Status: {response_data['response'].status_code}")
    logger.info(f"Response Body: {response_data['response'].text}")


@when("I send a GET request to retrieve AWS VPCs")
def when_get_list_vpcs(izo_mcn_url, default_headers) -> None:
    """Send GET request to retrieve VPCs from AWS"""
    account_id = mcn.get("aws_id")

    match account_id:
        case str(acc) if acc:
            url = f"{izo_mcn_url}/cloud/aws/account/{acc}/vpcs"
            logger.info(f"Sending GET request to: {url}")
            response_data["response"] = requests.get(url, headers=default_headers)
            logger.info(f"Response Status: {response_data['response'].status_code}")
            logger.info(f"Response Body: {response_data['response'].text}")
        case _:
            assert False, "AWS account id missing from context"


@when("I send a DELETE request to delete an AWS VPC")
def when_delete_vpc(izo_mcn_url, default_headers) -> None:
    """Send DELETE request to delete VPC from AWS"""
    vpc_id = mcn.get("aws_vpc_id")

    match vpc_id:
        case str(vpc) if vpc:
            url = f"{izo_mcn_url}/cloud/vpi/{vpc}"
            logger.info(f"Sending DELETE request to: {url}")
            response_data["response"] = requests.delete(url, headers=default_headers)
            logger.info(f"Response Status: {response_data['response'].status_code}")
            logger.info(f"Response Body: {response_data['response'].text}")
        case _:
            assert False, "No VPC id stored in context – cannot delete"

# ------------------------------------------------------------------------------
#  THEN STEPS – status code verification
# ------------------------------------------------------------------------------
def _assert_status(expected: int) -> None:
    """Verify the API response status code using match/case"""
    actual = response_data["response"].status_code
    response_body = response_data["response"].text

    match actual:
        case code if code == expected:
            logger.info(f"✓ Response status code is {code}")
        case 400:
            assert False, f"Bad Request (400): Invalid VPC configuration. Response: {response_body}"
        case 401:
            assert False, f"Unauthorized (401): Check authentication headers"
        case 403:
            assert False, f"Forbidden (403): Insufficient permissions for VPC creation"
        case 404:
            assert False, f"Not Found (404): API endpoint not found"
        case 409:
            assert False, f"Conflict (409): VPC already exists or naming conflict. Response: {response_body}"
        case 500:
            assert False, f"Internal Server Error (500): {response_body}"
        case code if code >= 500:
            assert False, f"Server Error ({code}): {response_body}"
        case _:
            assert False, f"Expected status {expected}, got {actual}. Response: {response_body}"


@then(parsers.cfparse("the AWS VPC creation API response should be {status_code:d}"))
def then_create_status(status_code: int) -> None:
    """Verify VPC creation response status code"""
    _assert_status(status_code)


@then(parsers.cfparse("the AWS VPC retrieval API response should be {status_code:d}"))
def then_retrieve_status(status_code: int) -> None:
    """Verify VPC retrieval response status code"""
    _assert_status(status_code)


@then(parsers.cfparse("the AWS VPC deletion API response should be {status_code:d}"))
def then_delete_status(status_code: int) -> None:
    """Verify VPC deletion response status code"""
    _assert_status(status_code)

# ------------------------------------------------------------------------------
#  THEN STEPS – body-content assertions
# ------------------------------------------------------------------------------
@then("the AWS VPC creation API response body must contain a VPC ID")
def then_body_contains_vpc_id() -> None:
    """Verify response contains VPC ID using match/case patterns"""
    try:
        resp_json = response_data["response"].json()
    except json.JSONDecodeError:
        response_body = response_data["response"].text
        assert False, f"Response is not valid JSON: {response_body}"

    vpc_id: str | None = None

    match resp_json:
        # Direct fields in response
        case {"id": str(id_val)} if id_val.strip():
            vpc_id = id_val.strip()
        case {"vpcId": str(vpc_val)} if vpc_val.strip():
            vpc_id = vpc_val.strip()
        # Nested under data object
        case {"data": {"id": str(id_val)}} if id_val.strip():
            vpc_id = id_val.strip()
        case {"data": {"vpcId": str(vpc_val)}} if vpc_val.strip():
            vpc_id = vpc_val.strip()
        # Fallback search for additional patterns
        case dict() as body:
            for field in ("id", "vpcId"):
                match body.get(field):
                    case str(x) if x.strip():
                        vpc_id = x.strip()
                        break
                    case _:
                        # Check nested data
                        if "data" in body and isinstance(body["data"], dict):
                            match body["data"].get(field):
                                case str(x) if x.strip():
                                    vpc_id = x.strip()
                                    break
                                case _:
                                    continue
        case _:
            pass

    match vpc_id:
        case str(v) if v:
            mcn["aws_vpc_id"] = v
            logger.info(f"✓ VPC ID found: {v}")
        case _:
            assert False, (
                f"VPC ID not found in response. "
                f"Response: {json.dumps(resp_json, indent=2)}"
            )


@then("the AWS VPC retrieval API response body must contain the VPC ID")
def then_retrieval_contains_vpc_id() -> None:
    """Verify response contains the created VPC ID using match/case"""
    vpc_id = mcn.get("aws_vpc_id")
    
    match vpc_id:
        case str(vpc_id_val) if vpc_id_val:
            pass  # Continue with validation
        case _:
            assert False, "No AWS VPC ID found in mcn data"

    try:
        resp_json = response_data["response"].json()
    except json.JSONDecodeError:
        response_body = response_data["response"].text
        assert False, f"Response is not valid JSON: {response_body}"

    found = False

    match resp_json:
        # Response is a list of VPCs
        case [*vpc_list]:
            for entry in vpc_list:
                match entry:
                    case {"id": str(id_val)} if id_val == vpc_id:
                        found = True
                        break
                    case {"vpcId": str(vpc_val)} if vpc_val == vpc_id:
                        found = True
                        break
        # Response is a single VPC object
        case {"id": str(id_val)} if id_val == vpc_id:
            found = True
        case {"vpcId": str(vpc_val)} if vpc_val == vpc_id:
            found = True
        case _:
            found = False

    match found:
        case True:
            logger.info(f"✓ VPC ID {vpc_id} found in retrieval response")
        case _:
            assert False, f"VPC ID {vpc_id} not found in retrieval response"


@then(parsers.cfparse("the AWS VPC deletion API response body must contain {msg}"))
def then_delete_body_contains(msg: str) -> None:
    """Verify VPC deletion response contains specified message"""
    body_text = response_data["response"].text

    match body_text:
        case text if msg in text:
            logger.info(f"✓ Expected message '{msg}' found in deletion response")
        case _:
            assert False, f"Expected message '{msg}' not found in response: {body_text}"


@then("cleanup any created AWS VPC resources")
def then_cleanup_log() -> None:
    """Log created VPC resources for cleanup"""
    match mcn:
        case {"aws_vpc_id": str(vpc_id)} if vpc_id:
            logger.info(f"✓ AWS VPC created with ID: {vpc_id}")
            logger.info("Note: Manual cleanup may be required")
        case _:
            logger.info("No AWS VPC resources to cleanup")'''




'''"""
VPC Creation BDD Step Definitions
Test file: api/vpc/steps/test_vpc_creation.py
"""

import pytest
import requests
import json
import time
from pytest_bdd import scenario, given, when, then, parsers


BASE_URL = "http://3.111.234.240:8081"
VPC_ENDPOINT = "/cloud/vpc"
ORGANIZATION_NAME = "caltestorg"
TENANT_ID = "tata"


@scenario('../vpc_create.feature', 'Successfully create a VPC')
def test_vpc_creation():
    """Test VPC creation scenario"""
    pass


@pytest.fixture
def vpc_payload():
    """Store VPC payload data"""
    return {}

@pytest.fixture
def api_response():
    """Store API response data"""
    return {}

@pytest.fixture
def api_headers():
    """Common headers for API requests"""
    return {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-TenantID': TENANT_ID,
        'organization-name': ORGANIZATION_NAME
    }

def make_vpc_request(url, headers, payload, timeout=(10, 120), max_retries=1):
    """
    Enhanced request handler with proper error handling and retry logic
    """
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}: Sending POST request to: {url}")
            print(f"Headers: {json.dumps(headers, indent=2)}")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=timeout  
            )
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print(f"Response Body: {response.text}")
            
            
            try:
                response_json = response.json() if response.text else None
            except (json.JSONDecodeError, ValueError):
                response_json = None
            
            api_response_data = {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'body': response.text,
                'json': response_json,
                'error': None
            }
            
            
            if (response.status_code == 400 and 
                response.text and 
                'Another update is currently in progress' in response.text):
                
                if attempt < max_retries - 1:
                    print(f"Pulumi conflict detected. Waiting 60 seconds before retry...")
                    time.sleep(60)
                    continue
                else:
                    print("Max retries reached. Pulumi conflict persists.")
            
            return api_response_data
            
        except requests.exceptions.Timeout as e:
            error_msg = f"Request timed out: {str(e)}"
            print(f"Timeout error: {error_msg}")
            
            if attempt < max_retries - 1:
                print(f"Retrying after timeout... Attempt {attempt + 2}")
                time.sleep(30)
                continue
            
            return {
                'status_code': 0,
                'error': error_msg,
                'body': '',
                'json': None,
                'headers': {}
            }
            
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Connection error: {str(e)}"
            print(f"Connection error: {error_msg}")
            
            if attempt < max_retries - 1:
                print(f"Retrying after connection error... Attempt {attempt + 2}")
                time.sleep(30)
                continue
                
            return {
                'status_code': 0,
                'error': error_msg,
                'body': '',
                'json': None,
                'headers': {}
            }
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            print(f"Request exception: {error_msg}")
            
            return {
                'status_code': 0,
                'error': error_msg,
                'body': '',
                'json': None,
                'headers': {}
            }
    
    
    return {
        'status_code': 0,
        'error': "Maximum retries exceeded",
        'body': '',
        'json': None,
        'headers': {}
    }


@given('the VPC details are:', target_fixture='vpc_payload')
def given_vpc_details(docstring):
    """Parse VPC details from the feature file"""
    vpc_data = {}
    
    
    lines = docstring.strip().split('\n')
    for line in lines:
        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            
            if key == 'cloudAccountId':
                vpc_data[key] = int(value) if value else 1
            elif key == 'cloudResourceGroup' and not value:
                vpc_data[key] = ''
            elif key == 'tagName':
                
                vpc_data['tags'] = {'Name': value}
            else:
                vpc_data[key] = value
    
    print(f"Parsed VPC data: {json.dumps(vpc_data, indent=2)}")
    return vpc_data

@when('I send a POST request to create a VPC', target_fixture='api_response')
def when_send_post_request(vpc_payload, api_headers):
    """Send POST request to create VPC with enhanced error handling"""
    url = f"{BASE_URL}{VPC_ENDPOINT}"
    
    
    return make_vpc_request(
        url=url,
        headers=api_headers,
        payload=vpc_payload,
        timeout=(10, 120),  
        max_retries=2  
    )

@then('the VPC creation API response should be 200')
def then_response_should_be_200(api_response):
    """Verify response status code is 200 with comprehensive error handling"""
    actual_code = api_response['status_code']
    expected_codes = [200, 201]
    
    
    if actual_code == 0:
        error_msg = api_response.get('error', 'Unknown network error')
        if 'timed out' in error_msg.lower():
            pytest.fail(f"Request timed out: {error_msg}. "
                       f"The server may be slow or unresponsive. "
                       f"Try increasing timeout or check server status.")
        elif 'connection' in error_msg.lower():
            pytest.fail(f"Connection failed: {error_msg}. "
                       f"Check if the server is running and accessible.")
        else:
            pytest.fail(f"Network error: {error_msg}")
    
    
    elif actual_code == 400:
        response_body = api_response.get('body', '')
        response_json = api_response.get('json', {})
        
        
        if 'Another update is currently in progress' in response_body:
            pytest.skip("Test skipped: Pulumi stack operation in progress. "
                       "Please wait for the current operation to complete and retry.")
        
        
        elif 'Invalid VPC/VNet configuration' in response_body:
            error_details = response_json.get('error', 'No error details provided')
            pytest.fail(f"VPC configuration validation failed: {error_details}")
        
        
        else:
            pytest.fail(f"Bad Request (400): {response_body}")
    
    elif actual_code == 401:
        pytest.fail("Authentication failed (401). "
                   f"Check X-TenantID ('{TENANT_ID}') and "
                   f"organization-name ('{ORGANIZATION_NAME}') headers.")
    
    elif actual_code == 403:
        pytest.fail("Authorization failed (403). Insufficient permissions for VPC creation.")
    
    elif actual_code == 404:
        pytest.fail(f"API endpoint not found (404). "
                   f"Check URL: {BASE_URL}{VPC_ENDPOINT}")
    
    elif actual_code == 409:
        response_body = api_response.get('body', '')
        if 'already exists' in response_body.lower():
            pytest.fail("Conflict (409): VPC with this name/configuration already exists.")
        else:
            pytest.fail(f"Conflict (409): {response_body}")
    
    elif actual_code == 500:
        response_body = api_response.get('body', '')
        pytest.fail(f"Internal server error (500): {response_body}. "
                   f"Check server logs for more details.")
    
    elif actual_code >= 500:
        pytest.fail(f"Server error ({actual_code}): {api_response.get('body', '')}")
    
    
    if actual_code not in expected_codes:
        pytest.fail(f"Unexpected status code {actual_code}. "
                   f"Expected {expected_codes}. "
                   f"Response: {api_response.get('body', '')}")
    
    print(f"✓ Response status code is {actual_code}")

@then('the response body must contain a VPC ID')
def then_response_contains_vpc_id(api_response):
    """Verify response contains VPC ID"""
    
    if api_response['status_code'] not in [200, 201]:
        pytest.skip("Skipping VPC ID validation due to unsuccessful API response")
    
    response_json = api_response['json']
    response_body = api_response['body']
    
    if response_json is None:
        pytest.fail(f"Response is not valid JSON: {response_body}")
    
    
    vpc_id_found = False
    vpc_id_value = None
    
    
    if 'id' in response_json:
        vpc_id_found = True
        vpc_id_value = response_json['id']
    elif 'vpcId' in response_json:
        vpc_id_found = True
        vpc_id_value = response_json['vpcId']
    elif 'data' in response_json and isinstance(response_json['data'], dict):
        if 'id' in response_json['data']:
            vpc_id_found = True
            vpc_id_value = response_json['data']['id']
        elif 'vpcId' in response_json['data']:
            vpc_id_found = True
            vpc_id_value = response_json['data']['vpcId']
    
    if not vpc_id_found:
        pytest.fail(f"VPC ID not found in response. "
                   f"Expected fields: 'id', 'vpcId', 'data.id', or 'data.vpcId'. "
                   f"Actual response: {json.dumps(response_json, indent=2)}")
    
    if not vpc_id_value:
        pytest.fail(f"VPC ID is empty or null. Value: {vpc_id_value}")
    
    print(f"✓ VPC ID found: {vpc_id_value}")


def print_test_context(vpc_payload, api_response):
    """Print test context for debugging"""
    print("\n" + "="*50)
    print("TEST CONTEXT DEBUG")
    print("="*50)
    print(f"VPC Payload: {json.dumps(vpc_payload, indent=2)}")
    print(f"API Response Status: {api_response.get('status_code', 'N/A')}")
    print(f"API Response Body: {api_response.get('body', 'N/A')}")
    print(f"API Response Error: {api_response.get('error', 'N/A')}")
    print("="*50)


@given('the VPC API is accessible')
def given_api_accessible():
    """Optional step to verify API accessibility before running tests"""
    try:
        
        health_url = f"{BASE_URL}/health"  
        response = requests.get(health_url, timeout=10)
        print(f"Health check response: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Health check failed (this is optional): {e}")
        
@then('cleanup any created resources')
def cleanup_resources(api_response):
    """Optional cleanup step to remove created VPCs after test"""
    if api_response.get('status_code') in [200, 201] and api_response.get('json'):
        response_json = api_response['json']
        vpc_id = None
        
        
        if 'id' in response_json:
            vpc_id = response_json['id']
        elif 'vpcId' in response_json:
            vpc_id = response_json['vpcId']
        
        if vpc_id:
            print(f"Note: VPC created with ID {vpc_id}. Manual cleanup may be required.")'''
            






'''"""
VPC Creation BDD Step Definitions
Test file: api/vpc/steps/test_vpc_creation.py
"""

import pytest
import requests
import json
from pytest_bdd import scenario, given, when, then, parsers

# Configuration
BASE_URL = "http://3.111.234.240:8081"
VPC_ENDPOINT = "/cloud/vpc"
ORGANIZATION_NAME = "caltestorg"
TENANT_ID = "tata"

# Bind scenario to test function
@scenario('../vpc_create.feature', 'Successfully create a VPC')
def test_vpc_creation():
    """Test VPC creation scenario"""
    pass

# Fixtures for storing test data
@pytest.fixture
def vpc_payload():
    """Store VPC payload data"""
    return {}

@pytest.fixture
def api_response():
    """Store API response data"""
    return {}

@pytest.fixture
def api_headers():
    """Common headers for API requests"""
    return {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-TenantID': TENANT_ID,
        'organization-name': ORGANIZATION_NAME  # API expects this as header, not query param
    }

# Step definitions
@given('the VPC details are:', target_fixture='vpc_payload')
def given_vpc_details(docstring):
    """Parse VPC details from the feature file"""
    vpc_data = {}
    
    # Parse the docstring format
    lines = docstring.strip().split('\n')
    for line in lines:
        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            # Handle different data types
            if key == 'cloudAccountId':
                vpc_data[key] = int(value) if value else 1
            elif key == 'cloudResourceGroup' and not value:
                vpc_data[key] = ''
            elif key == 'tagName':
                # Convert tagName to tags structure
                vpc_data['tags'] = {'Name': value}
            else:
                vpc_data[key] = value
    
    print(f"Parsed VPC data: {json.dumps(vpc_data, indent=2)}")
    return vpc_data

@when('I send a POST request to create a VPC', target_fixture='api_response')
def when_send_post_request(vpc_payload, api_headers):
    """Send POST request to create VPC"""
    url = f"{BASE_URL}{VPC_ENDPOINT}"
    # Remove params since organization-name is now in headers
    
    print(f"Sending POST request to: {url}")
    print(f"Headers: {json.dumps(api_headers, indent=2)}")
    print(f"Payload: {json.dumps(vpc_payload, indent=2)}")
    
    try:
        response = requests.post(
            url,
            headers=api_headers,
            json=vpc_payload,
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        return {
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'body': response.text,
            'json': response.json() if response.headers.get('content-type', '').startswith('application/json') else None
        }
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return {
            'status_code': 0,
            'error': str(e),
            'body': '',
            'json': None
        }

@then('the VPC creation API response should be 200')
def then_response_should_be_200(api_response):
    """Verify response status code is 200"""
    expected_codes = [200, 201]  # Accept both 200 and 201 for successful creation
    actual_code = api_response['status_code']
    
    assert actual_code in expected_codes, (
        f"Expected status code {expected_codes}, but got {actual_code}. "
        f"Response body: {api_response['body']}"
    )
    print(f"✓ Response status code is {actual_code}")

@then('the response body must contain a VPC ID')
def then_response_contains_vpc_id(api_response):
    """Verify response contains VPC ID"""
    response_json = api_response['json']
    response_body = api_response['body']
    
    assert response_json is not None, f"Response is not JSON: {response_body}"
    
    # Check for VPC ID in common response formats
    vpc_id_found = False
    vpc_id_value = None
    
    # Check different possible locations for VPC ID
    if 'id' in response_json:
        vpc_id_found = True
        vpc_id_value = response_json['id']
    elif 'vpcId' in response_json:
        vpc_id_found = True
        vpc_id_value = response_json['vpcId']
    elif 'data' in response_json and isinstance(response_json['data'], dict):
        if 'id' in response_json['data']:
            vpc_id_found = True
            vpc_id_value = response_json['data']['id']
        elif 'vpcId' in response_json['data']:
            vpc_id_found = True
            vpc_id_value = response_json['data']['vpcId']
    
    assert vpc_id_found, (
        f"VPC ID not found in response. "
        f"Response JSON: {json.dumps(response_json, indent=2)}"
    )
    
    assert vpc_id_value, f"VPC ID is empty. Value: {vpc_id_value}"
    print(f"✓ VPC ID found: {vpc_id_value}")

# Remove the problematic debug fixtures and hooks
def print_test_context(vpc_payload, api_response):
    """Print test context for debugging"""
    print("\n" + "="*50)
    print("TEST CONTEXT DEBUG")
    print("="*50)
    print(f"VPC Payload: {json.dumps(vpc_payload, indent=2)}")
    print(f"API Response Status: {api_response.get('status_code', 'N/A')}")
    print(f"API Response Body: {api_response.get('body', 'N/A')}")
    print("="*50)'''