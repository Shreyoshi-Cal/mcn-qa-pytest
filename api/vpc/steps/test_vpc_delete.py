"""
Single-purpose test: delete a VPC whose ID is provided via --vpc-id
"""

import json
import logging
import os
import requests
from pytest_bdd import given, when, then, scenario

LOG = logging.getLogger(__name__)
PAYLOAD_TEMPLATE = {
    "cloudAccountId": int(os.getenv("cloudAccountId", "1")),
    "cloudProvider": "aws",
    "cloudRegion": os.getenv("cloudRegion", "us-east-1"),
}

@scenario("../vpc_delete.feature", "Delete VPC by CLI-supplied ID")
def test_delete():
    pass


@given("the VPC ID from CLI is available")
def check_id(vpc_id):
    LOG.info(" Deleting VPC %s", vpc_id)


@when("the DELETE call is sent")
def send_delete(izo_mcn_url, vpc_id, default_headers):
    url = f"{izo_mcn_url}/cloud/vpc/{vpc_id}"
    LOG.info("DELETE %s | payload=%s", url, PAYLOAD_TEMPLATE)
    resp = requests.delete(url, headers=default_headers,
                           data=json.dumps(PAYLOAD_TEMPLATE))
    send_delete.resp = resp
    LOG.info("→ %s %s", resp.status_code, resp.text)


@then("the API responds 200")
def check_status():
    assert send_delete.resp.status_code == 200
