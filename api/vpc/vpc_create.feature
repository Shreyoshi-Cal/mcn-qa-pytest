Feature: AWS VPC Creation API Testing
  As a cloud infrastructure administrator
  I want to create AWS VPCs through the API
  So that I can provision VPC infrastructure programmatically and track the created resources

  Background:
    Given I have a registered AWS account
    And the AWS API is accessible

  @aws @vpc_creation @positive @smoke @logging
  Scenario: Successfully create a VPC on AWS with detailed logging
  Given the VPC details are:
    """
    cidrBlock=${VPC_BULK_CIDR}
    cloudAccountId=1
    cloudProvider=aws
    cloudRegion=us-east-1
    cloudResourceGroup=
    name=${VPC_BULK_NAME}
    stackName=${VPC_BULK_STACK}
    tagName=${VPC_BULK_NAME}
    """
    When I send a POST request to create a VPC on AWS
    Then the AWS VPC creation API response should be 200
    And the AWS VPC creation API response body must contain a VPC ID
    And cleanup any created AWS VPC resources
