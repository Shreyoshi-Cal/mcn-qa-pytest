Feature: Delete an AWS VPC by providing only the VPC ID on the CLI
  Scenario: Delete VPC by CLI-supplied ID
    Given the VPC ID from CLI is available
    When the DELETE call is sent
    Then the API responds 200
