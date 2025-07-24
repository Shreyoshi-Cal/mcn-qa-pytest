import pytest
import os
from dotenv import load_dotenv


def pytest_addoption(parser):
    parser.addoption("--env", action="store", default="qa", help="Environment to run tests on. For eg.: dev, qa or uat")


@pytest.fixture(scope="session")
def get_env(request):
    env = request.config.getoption("--env")
    base_path = os.path.abspath(os.path.dirname(__file__))
    env_file = os.path.join(base_path, "env", f"{env}.env")
    return env_file


@pytest.fixture(scope="session")
def izo_mcn_url(get_env):
    env_file = get_env
    if not os.path.exists(env_file):
        raise ValueError(f"Environment file '{env_file}' not found.")
    load_dotenv(env_file)
    izo_mcn_url = os.getenv("izo_mcn_url")
    if not izo_mcn_url:
        raise ValueError(f"Environment variable 'izo_mcn_url' not found in {env_file}.")
    return izo_mcn_url

@pytest.fixture(scope="session")
def vpc_id_for_deletion(get_env):
    env_file = get_env
    if not os.path.exists(env_file):
        raise ValueError(f"Environment file '{env_file}' not found.")
    load_dotenv(env_file)
    vpc_id_for_deletion = os.getenv("vpc_id_for_deletion")
    if not vpc_id_for_deletion:
        raise ValueError(f"Environment variable 'vpc_id_for_deletion' not found in {env_file}.")
    return vpc_id_for_deletion


@pytest.fixture(scope="session")
def izo_iac_url(get_env):
    env_file = get_env
    if not os.path.exists(env_file):
        raise ValueError(f"Environment file '{env_file}' not found.")
    load_dotenv(env_file)
    izo_iac_url = os.getenv("izo_iac_url")
    if not izo_iac_url:
        raise ValueError(f"Environment variable 'izo_iac_url' not found in {env_file}.")
    return izo_iac_url

@pytest.fixture(scope="session")
def default_headers():
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-TenantID": "tata",
        "Organization-Name": "caltestorg"
    }


@pytest.fixture(scope="session")
def pulumi_acc(get_env):
    env_file = get_env
    if not os.path.exists(env_file):
        raise ValueError(f"Environment file '{env_file}' not found.")
    load_dotenv(env_file)
    pulumi_acc = os.getenv("pulumi_acc_name")
    if not pulumi_acc:
        raise ValueError(f"Environment variable 'pulumi_acc' not found in {env_file}.")
    return pulumi_acc


@pytest.fixture(scope="session")
def pulumi_email(get_env):
    env_file = get_env
    if not os.path.exists(env_file):
        raise ValueError(f"Environment file '{env_file}' not found.")
    load_dotenv(env_file)
    pulumi_email = os.getenv("pulumi_email")
    if not pulumi_email:
        raise ValueError(f"Environment variable 'pulumi_email' not found in {env_file}.")
    return pulumi_email


@pytest.fixture(scope="session")
def pulumi_accessToken(get_env):
    env_file = get_env
    if not os.path.exists(env_file):
        raise ValueError(f"Environment file '{env_file}' not found.")
    load_dotenv(env_file)
    pulumi_accessToken = os.getenv("pulumi_accessToken")
    if not pulumi_accessToken:
        raise ValueError(f"Environment variable 'pulumi_accessToken' not found in {env_file}.")
    return pulumi_accessToken


@pytest.fixture(scope="session")
def pulumi_description(get_env):
    env_file = get_env
    if not os.path.exists(env_file):
        raise ValueError(f"Environment file '{env_file}' not found.")
    load_dotenv(env_file)
    pulumi_description = os.getenv("pulumi_description")
    if not pulumi_description:
        raise ValueError(f"Environment variable 'pulumi_description' not found in {env_file}.")
    return pulumi_description


@pytest.fixture(scope="session")
def pulumi_org_name(get_env):
    env_file = get_env
    if not os.path.exists(env_file):
        raise ValueError(f"Environment file '{env_file}' not found.")
    load_dotenv(env_file)
    pulumi_org_name = os.getenv("pulumi_org_name")
    if not pulumi_org_name:
        raise ValueError(f"Environment variable 'pulumi_org_name' not found in {env_file}.")
    return pulumi_org_name


@pytest.fixture(scope="session")
def pulumi_accessTokenName(get_env):
    env_file = get_env
    if not os.path.exists(env_file):
        raise ValueError(f"Environment file '{env_file}' not found.")
    load_dotenv(env_file)
    pulumi_accessTokenName = os.getenv("pulumi_accessTokenName")
    if not pulumi_accessTokenName:
        raise ValueError(f"Environment variable 'pulumi_accessTokenName' not found in {env_file}.")
    return pulumi_accessTokenName


@pytest.fixture(scope="session")
def pulumi_accessTokenDesc(get_env):
    env_file = get_env
    if not os.path.exists(env_file):
        raise ValueError(f"Environment file '{env_file}' not found.")
    load_dotenv(env_file)
    pulumi_accessTokenDesc = os.getenv("pulumi_accessTokenDesc")
    if not pulumi_accessTokenDesc:
        raise ValueError(f"Environment variable 'pulumi_accessTokenDesc' not found in {env_file}.")
    return pulumi_accessTokenDesc


@pytest.fixture(scope="session")
def pulumi_subscriptionKey(get_env):
    env_file = get_env
    if not os.path.exists(env_file):
        raise ValueError(f"Environment file '{env_file}' not found.")
    load_dotenv(env_file)
    pulumi_subscriptionKey = os.getenv("pulumi_subscriptionKey")
    if not pulumi_subscriptionKey:
        raise ValueError(f"Environment variable 'pulumi_subscriptionKey' not found in {env_file}.")
    return pulumi_subscriptionKey


@pytest.fixture(scope="session")
def aws_key(get_env):
    env_file = get_env
    if not os.path.exists(env_file):
        raise ValueError(f"Environment file '{env_file}' not found.")
    load_dotenv(env_file)
    aws_key = os.getenv("aws_key")
    if not aws_key:
        raise ValueError(f"Environment variable 'aws_key' not found in {env_file}.")
    return aws_key


@pytest.fixture(scope="session")
def aws_secret(get_env):
    env_file = get_env
    if not os.path.exists(env_file):
        raise ValueError(f"Environment file '{env_file}' not found.")
    load_dotenv(env_file)
    aws_secret = os.getenv("aws_secret")
    if not aws_secret:
        raise ValueError(f"Environment variable 'aws_secret' not found in {env_file}.")
    return aws_secret

@pytest.fixture(scope="session")
def azure_clientId(get_env):
    env_file = get_env
    if not os.path.exists(env_file):
        raise ValueError(f"Environment file '{env_file}' not found.")
    load_dotenv(env_file)
    azure_clientId = os.getenv("azure_clientId")
    if not azure_clientId:
        raise ValueError(f"Environment variable 'azure_clientId' not found in {env_file}.")
    return azure_clientId


@pytest.fixture(scope="session")
def azure_clientSecret(get_env):
    env_file = get_env
    if not os.path.exists(env_file):
        raise ValueError(f"Environment file '{env_file}' not found.")
    load_dotenv(env_file)
    azure_clientSecret = os.getenv("azure_clientSecret")
    if not azure_clientSecret:
        raise ValueError(f"Environment variable 'azure_clientSecret' not found in {env_file}.")
    return azure_clientSecret


@pytest.fixture(scope="session")
def azure_tenantId(get_env):
    env_file = get_env
    if not os.path.exists(env_file):
        raise ValueError(f"Environment file '{env_file}' not found.")
    load_dotenv(env_file)
    azure_tenantId = os.getenv("azure_tenantId")
    if not azure_tenantId:
        raise ValueError(f"Environment variable 'azure_tenantId' not found in {env_file}.")
    return azure_tenantId


@pytest.fixture(scope="session")
def azure_subscriptionId(get_env):
    env_file = get_env
    if not os.path.exists(env_file):
        raise ValueError(f"Environment file '{env_file}' not found.")
    load_dotenv(env_file)
    azure_subscriptionId = os.getenv("azure_subscriptionId")
    if not azure_subscriptionId:
        raise ValueError(f"Environment variable 'azure_subscriptionId' not found in {env_file}.")
    return azure_subscriptionId

