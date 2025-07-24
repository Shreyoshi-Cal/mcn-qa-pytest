Feature: Validate API endpoints for Pulumi

@setup @sanity
Scenario Outline: Save a Pulumi account
  When I send a POST request to save a pulumi account
  Then the pulumi save account API response should be 201
  And the pulumi save account API response body must contain a pulumi account ID

@setup @sanity
Scenario Outline: Save a Pulumi organization
  When I send a POST request to save a pulumi organization
  Then the pulumi save organization API response should be 201
  And the pulumi save organization API response body must contain a pulumi organization ID
