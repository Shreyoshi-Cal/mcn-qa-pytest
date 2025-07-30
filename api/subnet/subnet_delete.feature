Feature: Delete an AWS Subnet by providing only the Subnet ID on the CLI
  Scenario: Delete Subnet by CLI-supplied ID
    Given the subnet ID from CLI is available
    When the DELETE call is sent
    Then the API responds 200
