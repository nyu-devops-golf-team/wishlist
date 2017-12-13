Feature: The wishlist service
	As a Wishlist (?)
	I need a service
	So that I can keep track of all the products added and the wishlists themselves

Background:
    Given the following wishlists
    	| name       | id |
        | wishlist1  |  1 |
        | wishlist2  |  2 | 
	| wishlist3  |  3 |


Scenario: Create a Wishlist
    When I visit the "Home Page"
    And I set the "name" to "wishlist1"
    And I press the "create" button
    Then I should see the message "Success"

Scenario: List a Wishlist
    When I visit the "Home Page"
    And I press the "search" button
    Then I should see "wishlist1" in the results
    And I should see "wishlist2" in the results
    And I should see "wishlist3" in the results

Scenario: Update a Wishlist
    When I visit the "Home Page"
    And I set the "id" to "1"
    And I press the "retrieve" button
    Then I should see "wishlist1" in the results
    When I change the "name" to "test_change"
    And I press the "update" button
    Then I should see the message "Success"
    When I set the "id" to "1"
    And I press the "retrieve" button
    Then I should see "test_change" in the results
    When I press the "clear" button
    And I press the "search" button
    Then I should see "test_change" in the results

Scenario: Delete a Wishlist
    When I visit the "Home Page"
    And I set the "id" to "2"
    And I press the "retrieve" button
    Then I should see "wishlist2" in the results
    When I press the "delete" button
    Then I should see the message "Success"
    When I press the "search" button
    Then I should not see "wishlist2" in the results

Scenario: The server is up
    When I visit the "Home Page"
    Then I should see "Wishlist Service" in the title

