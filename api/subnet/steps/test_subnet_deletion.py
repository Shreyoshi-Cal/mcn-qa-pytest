"""
Single-purpose test: delete a subnet whose ID is provided via --subnet-id
"""

import json
import logging
import os
import requests
from pytest_bdd import given, when, then, scenario

LOG = logging.getLogger(__name__)
PAYLOAD_TEMPLATE = {
    "cloudAccountId": int(os.getenv("aws_account_id", "1")),
    "cloudProvider": "aws",
    "cloudRegion": os.getenv("aws_default_region", "us-east-1"),
}

@scenario("../subnet_delete.feature", "Delete Subnet by CLI-supplied ID")
def test_delete():
    pass

@given("the subnet ID from CLI is available")
def check_id(subnet_id):
    LOG.info(" Deleting Subnet %s", subnet_id)

@when("the DELETE call is sent")
def send_delete(izo_mcn_url, subnet_id, default_headers):
    url = f"{izo_mcn_url}/cloud/subnet/{subnet_id}"
    LOG.info("DELETE %s | payload=%s", url, PAYLOAD_TEMPLATE)
    resp = requests.delete(url, headers=default_headers,
                           data=json.dumps(PAYLOAD_TEMPLATE))
    send_delete.resp = resp
    LOG.info("→ %s %s", resp.status_code, resp.text)

@then("the API responds 200")
def check_status():
    assert send_delete.resp.status_code == 200
