"""
AWS Subnet Creation  pytest-bdd step definitions

Endpoint assumed:
    POST /cloud/subnet

Request model:
{
  "cloudAccountId":      0,
  "cloudProvider":       "string",
  "cloudRegion":         "string",
  "cloudResourceGroup":  "",
  "stackName":           "string",
  "subnetCidr":          "string",
  "vpcId":               "string"
}
"""

from __future__ import annotations
import json, logging, requests
import os
from typing import Dict, Any
from pytest_bdd import given, when, then, scenarios, parsers

logger = logging.getLogger(__name__)
step_data: Dict[str, Any] = {}
response_data: Dict[str, requests.Response] = {}


scenarios("../subnet_create.feature")

@given("the AWS API is accessible")
def given_api_accessible(izo_mcn_url) -> None:
    """Best-effort health probe; does not fail test if /health is absent."""
    health_url = f"{izo_mcn_url}/health"

    try:
        resp = requests.get(health_url, timeout=5)
        logger.info(f"Health probe {health_url} → {resp.status_code}")
        
        match resp.status_code:
            case 200:
                logger.info(" AWS API is healthy")
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

@given("the subnet details")
def given_subnet_details(docstring) -> None:
    # Check for bulk creation environment variables
    auto_vpc_id = os.getenv("SUBNET_BULK_VPC_ID")
    auto_cidr   = os.getenv("SUBNET_BULK_CIDR")
    auto_name   = os.getenv("SUBNET_BULK_NAME")
    auto_stack  = os.getenv("SUBNET_BULK_STACK")
    #auto_az= os.getenv("SUBNET_BULK_AZ")  availabilityZone={auto_az}

    if auto_vpc_id and auto_cidr and auto_name and auto_stack :
        docstring = f"""
        cloudAccountId=1
        cloudProvider=aws
        cloudRegion=us-east-1
        cloudResourceGroup=
        stackName={auto_stack}
        subnetCidr={auto_cidr}
        vpcId={auto_vpc_id}
        
        name={auto_name}
        """.strip()

    """Parse the multiline table to build the subnet-creation payload."""
    step_data.clear()
    for raw in docstring.strip().splitlines():
        if "=" not in raw:
            continue
        key, val = (part.strip() for part in raw.split("=", 1))
        if key == "cloudAccountId":
            step_data[key] = int(val)
        else:
            step_data[key] = val
    logger.info(" Subnet payload\n%s", json.dumps(step_data, indent=2))



@when("I send the subnet-creation request")
def when_post_subnet(izo_mcn_url, default_headers) -> None:
    url = f"{izo_mcn_url}/cloud/create-subnet"
    logger.info(" POST %s", url)
    response_data["resp"] = requests.post(
        url, headers=default_headers, data=json.dumps(step_data)
    )
    logger.info("↩︎ %s  %s",
                response_data["resp"].status_code,
                response_data["resp"].text[:200])



@then(parsers.cfparse("the subnet API must return {status:d}"))
def then_status(status: int) -> None:
    resp = response_data["resp"]
    assert resp.status_code == status, f"Expected {status}, got {resp.status_code}"


@then("the response contains the created subnet id")
def then_extract_subnet() -> None:
    resp = response_data["resp"]
    try:
        body = resp.json()
    except ValueError:
        assert False, "Non-JSON response"

    subnet_id = None
    for key in ("subnetId", "id", "data"):
        if key in body:
            if isinstance(body[key], str):
                subnet_id = body[key]
                break
            if isinstance(body[key], dict):
                subnet_id = body[key].get("subnetId") or body[key].get("id")
                break

    assert subnet_id, f"Subnet ID not found in {body}"
    logger.info(" Subnet created: %s", subnet_id)
