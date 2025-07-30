Feature: AWS Subnet creation
  As a cloud engineer
  I want to create subnets through the API
  So that I can carve out address space inside a VPC

  Background:
    Given the AWS API is accessible

  @aws @subnet_creation @positive
  Scenario: Successfully create a subnet
    Given the subnet details
      """
      cloudAccountId=1
      cloudProvider=aws
      cloudRegion=us-east-1
      cloudResourceGroup=
      stackName=subnet-stack-1
      subnetCidr=10.0.2.0/24
      vpcId=vpc-04fc4339d04982788
      """
    When I send the subnet-creation request
    Then the subnet API must return 200
    And the response contains the created subnet id
