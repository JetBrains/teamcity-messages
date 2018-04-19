from behave import *

use_step_matcher("re")


@given("I like BDD")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    print("Hello")


@when("country is (?P<country>.+)")
def step_impl(context, country):
    """
    :type context: behave.runner.Context
    :type country: str
    """
    context.country = country


@then("capital is (?P<city>.+)")
def step_impl(context, city):
    """
    :type context: behave.runner.Context
    :type city: str
    """
    capitals = {"USA": "Washington", "Japan": "Tokio"}
    assert capitals[context.country] == city


@given("I will fail")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    raise Exception("fail")


@given("I will create background")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    print("Background")


@then("THEN_A")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    pass


@when("WHEN_A")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    pass


@when("WHEN_B")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    pass


@then("THEN_B")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    pass
