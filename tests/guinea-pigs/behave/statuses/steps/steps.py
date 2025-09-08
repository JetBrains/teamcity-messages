from behave import *

use_step_matcher("re")


@given("I like BDD")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    raise RuntimeError("Failed step")
