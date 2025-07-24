import requests
import logging
import json
from pytest_bdd import scenarios, parsers, when, then
from api.urlpaths.paths import Paths
from api.pulumi.steps.pulumi import config, pulumi, response_data  # updated import

logger = logging.getLogger(__name__)

scenarios("../cloud_register.feature")

mcn = {}


################################################################################################################
#   Test Cloud Account Registration API Endpoint                                                               #
################################################################################################################

@when(parsers.cfparse("I send a POST request to register an {cloud} account"))
def send_post_req_register_cloud_acc(izo_mcn_url, default_headers, cloud, aws_key, aws_secret,
                                     azure_clientId, azure_clientSecret, azure_tenantId, azure_subscriptionId):
    cloud = cloud.lower()
    data = {}

    match cloud:
        case "aws":
            data = {
                "accessKey": aws_key,
                "secretKey": aws_secret,
                "accountName": f"Test{cloud}fromAPI",
                "ownerEmailId": f"qa-{cloud}@mcn.in"
            }
        case "azure":
            data = {
                "clientId": azure_clientId,
                "clientSecret": azure_clientSecret,
                "tenantId": azure_tenantId,
                "subscriptionId": azure_subscriptionId,
                "accountName": f"Test{cloud}fromAPI",
                "ownerEmailId": f"qa-{cloud}@mcn.in"
            }

    response_data["response"] = requests.post(
        f"{izo_mcn_url}/cloud/{cloud}/account?organizationName={config['org_name']}",
        headers=default_headers,
        data=json.dumps(data)
    )

@then(parsers.cfparse("the {cloud} registration API response should be {status_code}"))
def check_response_code_register_cloud_acc(status_code):
    assert response_data["response"].status_code == int(status_code)

@then(parsers.cfparse("the {cloud} registration API response body must contain a cloud ID"))
def check_response_body_register_cloud_acc(cloud):
    resp = response_data["response"].json()
    match cloud.lower():
        case "aws":
            mcn["aws_id"] = resp["id"]
            assert "aws_id" in mcn
        case "azure":
            mcn["azure_id"] = resp["id"]
            assert "azure_id" in mcn


################################################################################################################
#   Test Retrieve Cloud Account API Endpoint                                                                   #
################################################################################################################

@when(parsers.cfparse("I send a GET request to retrieve an {cloud} account"))
def send_get_req_retrieve_cloud_acc(izo_mcn_url, default_headers, cloud):
    cloud = cloud.lower()
    url = f'{izo_mcn_url}/cloud/{cloud}/account'
    response_data["response"] = requests.get(url, headers=default_headers)

@then(parsers.cfparse("the {cloud} retrieval API response should be {status_code}"))
def check_response_code_retrieve_cloud_acc(status_code):
    assert response_data["response"].status_code == int(status_code)

@then(parsers.cfparse("the {cloud} retrieval API response body must contain the cloud ID"))
def check_response_body_retrieve_cloud_acc(cloud):
    resp = response_data["response"].json()
    cloud = cloud.lower()

    for entry in resp:
        if entry["accountName"] == f"Test{cloud}fromAPI":
            match cloud:
                case "aws":
                    assert mcn["aws_id"] == entry["id"]
                case "azure":
                    assert mcn["azure_id"] == entry["id"]


################################################################################################################
#   Test Cloud Account Deletion API Endpoint                                                                   #
################################################################################################################

@when(parsers.cfparse("I send a DELETE request to delete an {cloud} account"))
def send_delete_req_delete_cloud_acc(izo_mcn_url, default_headers, cloud):
    cloud = cloud.lower()

    match cloud:
        case "aws":
            url = f'{izo_mcn_url}/cloud/aws/account/{mcn["aws_id"]}'
        case "azure":
            url = f'{izo_mcn_url}/cloud/azure/account/{mcn["azure_id"]}'

    response_data["response"] = requests.delete(url, headers=default_headers)

@then(parsers.cfparse("the {cloud} deletion API response should be {status_code}"))
def check_response_code_delete_cloud_acc(status_code):
    assert response_data["response"].status_code == int(status_code)

@then(parsers.cfparse("the {cloud} deletion API response body must contain {msg}"))
def check_response_body_delete_cloud_acc(msg):
    assert msg in response_data["response"].text
