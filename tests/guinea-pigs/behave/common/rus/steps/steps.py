# coding: utf8
from behave import *

use_step_matcher("re")


@given(u"Я говорю по-русски")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    print("Hello")
