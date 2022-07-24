Feature: Launch stack_group

  Scenario: launch a stack_group that does not exist
    Given stack_group "2" does not exist
    When the user launches stack_group "2"
    Then all the stacks in stack_group "2" are in "CREATE_COMPLETE"

  Scenario: launch a stack_group, excluding dependencies, that does not exist
    Given stack_group "2" does not exist
    When the user launches stack_group "2"
    Then all the stacks in stack_group "2" are in "CREATE_COMPLETE"

  Scenario: launch a stack_group that already exists
    Given all the stacks in stack_group "2" are in "CREATE_COMPLETE"
    When the user launches stack_group "2"
    Then all the stacks in stack_group "2" are in "CREATE_COMPLETE"

  Scenario: launch a stack_group that partially exists
    Given stack "2/A" exists in "CREATE_COMPLETE" state
    When the user launches stack_group "2"
    Then all the stacks in stack_group "2" are in "CREATE_COMPLETE"

  Scenario: launch a stack_group with updates that partially exists
    Given stack "2/A" exists in "CREATE_COMPLETE" state
    And stack "2/B" does not exist
    And stack "2/C" does not exist
    And the template for stack "2/A" is "updated_template.json"
    When the user launches stack_group "2"
    Then stack "2/A" exists in "UPDATE_COMPLETE" state
    And stack "2/B" exists in "CREATE_COMPLETE" state
    And stack "2/C" exists in "CREATE_COMPLETE" state

  Scenario: launch a stack_group with updates that already exists
    Given all the stacks in stack_group "2" are in "CREATE_COMPLETE"
    And the template for stack "2/A" is "updated_template.json"
    And the template for stack "2/B" is "updated_template.json"
    And the template for stack "2/C" is "updated_template.json"
    When the user launches stack_group "2"
    Then all the stacks in stack_group "2" are in "UPDATE_COMPLETE"

  Scenario: launch a stack_group with nested stack_groups that do not exist
    Given stack_group "5" does not exist
    When the user launches stack_group "5"
    Then all the stacks in stack_group "5" are in "CREATE_COMPLETE"

  Scenario: launch a stack_group that does not exist ignoring dependencies
    Given stack_group "2" does not exist
    When the user launches stack_group "2" with ignore dependencies
    Then all the stacks in stack_group "2" are in "CREATE_COMPLETE"

  Scenario: launch a StackGroup with stacks with launch_type = delete and skip that has not been launched
    Given stack_group "launch-actions" does not exist
    When the user launches stack_group "launch-actions"
    Then stack "launch-actions/delete" does not exist
    And stack "launch-actions/skip" does not exist
    And stack "launch-actions/deploy" exists in "CREATE_COMPLETE" state

  Scenario: launch a StackGroup with stacks with launch_type = delete that currently exist
    Given  stack "launch-actions/delete" exists using "valid_template.json"
    And stack "launch-actions/deploy" exists using "valid_template.json"
    When the user launches stack_group "launch-actions"
    Then stack "launch-actions/delete" does not exist
    And stack "launch-actions/deploy" exists in "CREATE_COMPLETE" state

  Scenario: launch a StackGroup with stacks with launch_type = skip that currently exist
    Given  stack "launch-actions/skip" exists using "valid_template.json"
    And stack "launch-actions/deploy" exists using "valid_template.json"
    When the user launches stack_group "launch-actions"
    Then stack "launch-actions/skip" exists in "CREATE_COMPLETE" state
    And stack "launch-actions/deploy" exists in "CREATE_COMPLETE" state
