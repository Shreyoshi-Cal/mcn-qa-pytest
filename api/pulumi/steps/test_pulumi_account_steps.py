import requests
import logging
import json
from pytest_bdd import scenarios, parsers, when, then
from api.urlpaths.paths import Paths
from api.pulumi.steps.pulumi import pulumi, response_data


logger = logging.getLogger(__name__)

scenarios("../pulumi_account.feature")

'''response_data = {}
pulumi = {}'''

################################################################################################################
#   Test Save Pulumi Account Details API Endpoint                                                              #
################################################################################################################

@when(parsers.cfparse("I send a POST request to save a pulumi account"))
def send_post_req_save_pulumi_acc(izo_mcn_url, default_headers, pulumi_acc, pulumi_email, pulumi_accessToken,
                                  pulumi_description):
    data = json.dumps({
        "accountName": pulumi_acc,
        "email": pulumi_email,
        "accessToken": pulumi_accessToken,
        "description": pulumi_description,
        "expires": 0
    })
    response_data["response"] = requests.post(f"{izo_mcn_url}/pulumi/account", headers=default_headers, data=data)

@then(parsers.cfparse("the pulumi save account API response should be {status_code}"))
def check_response_code_save_pulumi_acc(status_code):
    assert response_data["response"].status_code == int(status_code)

@then(parsers.cfparse("the pulumi save account API response body must contain a pulumi account ID"))
def check_response_body_save_pulumi_acc():
    resp = response_data["response"].json()
    assert "id" in resp.keys()
    pulumi['acc_id'] = resp['id']
    print(f"Pulumi Acc ID - {pulumi['acc_id']}")


################################################################################################################
#   Test Save Pulumi Organization Details API Endpoint                                                         #
################################################################################################################

@when(parsers.cfparse("I send a POST request to save a pulumi organization"))
def send_post_req_save_pulumi_org(izo_mcn_url, default_headers, pulumi_org_name, pulumi_accessTokenName, pulumi_acc,
                                  pulumi_accessToken, pulumi_accessTokenDesc, pulumi_subscriptionKey):
    data = json.dumps({
        "name": pulumi_org_name,
        "admin": True,
        "accessTokenName": pulumi_accessTokenName,
        "accessToken": pulumi_accessToken,
        "accessTokenDescription": pulumi_accessTokenDesc,
        "subscriptionKey": pulumi_subscriptionKey,
        "accessTokenExpires": 0
    })
    response_data["response"] = requests.post(f"{izo_mcn_url}/pulumi/account/{pulumi_acc}/organization", 
                                              headers=default_headers, data=data)

@then(parsers.cfparse("the pulumi save organization API response should be {status_code}"))
def check_response_code_save_pulumi_org(status_code):
    assert response_data["response"].status_code == int(status_code)

@then(parsers.cfparse("the pulumi save organization API response body must contain a pulumi organization ID"))
def check_response_body_save_pulumi_org():
    resp = response_data["response"].json()
    assert "id" in resp.keys()
    pulumi['org_id'] = resp['id']
    print(f"Pulumi Org ID - {pulumi['org_id']}")
