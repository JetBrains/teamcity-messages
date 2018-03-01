Feature: Complex

  Background: Install background
    Given I will create background


  Scenario Outline: With examples
    When country is <country>
    Then capital is <city>

    Examples:
      | country     | city        |
      | USA         | Washington  |
      | Japan       | Tokio       |
      | I will fail | I will fail |


  Scenario: Broken
    Given I will fail
    And Skip me