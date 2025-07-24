Feature: AWS VPC Management API Testing
  As a cloud infrastructure administrator
  I want to manage AWS VPCs through the API
  So that I can create and delete VPCs programmatically for my infrastructure needs

  Background:
    Given I have a registered AWS account
    And the AWS API is accessible

   @aws @vpc_creation @positive @smoke
  Scenario: Successfully create a VPC on AWS
    Given the VPC details are:
     """
      cidrBlock=10.0.0.0/16
      cloudAccountId=1
      cloudProvider=aws
      cloudRegion=us-east-1
      cloudResourceGroup=
     name=successful-test-vpc
      stackName=successful-vpc-stack
      tagName=successful-test-vpc
      """
    When I send a POST request to create a VPC on AWS
    Then the AWS VPC creation API response should be 200
    And the AWS VPC creation API response body must contain a VPC ID
    And cleanup any created AWS VPC resources

  @aws @vpc_deletion @positive @smoke
  Scenario: Delete AWS VPC after creation
    Given the VPC details are:
      """
      cidrBlock=10.2.0.0/16
      cloudAccountId=1
      cloudProvider=aws
      cloudRegion=us-east-1
      cloudResourceGroup=
      name=delete-test-vpc
      stackName=delete-test-stack
      tagName=delete-test-vpc
      """
    When I send a POST request to create a VPC on AWS
    Then the AWS VPC creation API response should be 200
    And the AWS VPC creation API response body must contain a VPC ID
    When I send a DELETE request to delete an AWS VPC with payload
    Then the AWS VPC deletion API response should be 200
    And the AWS VPC deletion API response body must contain VPC deleted successfully
