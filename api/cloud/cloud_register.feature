Feature: Validate API endpoints for Cloud Account Registration

@setup @sanity
Scenario Outline: Register a cloud account
  When I send a POST request to register an <cloud> account
  Then the <cloud> registration API response should be 200
  And the <cloud> registration API response body must contain a cloud ID

  Examples:
  | cloud |
  | aws   |
  | azure |

@sanity
Scenario Outline: Rerieve a cloud account
  When I send a GET request to retrieve an <cloud> account
  Then the <cloud> retrieval API response should be 200
  And the <cloud> retrieval API response body must contain the cloud ID

  Examples:
  | cloud |
  | aws   |
  | azure |

@test
Scenario Outline: Delete a cloud account
  When I send a DELETE request to delete an <cloud> account
  Then the <cloud> deletion API response should be 200
  And the <cloud> deletion API response body must contain cloud account deleted successfully

  Examples:
  | cloud |
  | aws   |
  | azure |
