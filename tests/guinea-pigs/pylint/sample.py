"""Sample python file for testing PyLint integration."""


def my_fun(one, two, three, four, five, six):  # pylint: disable=W0613
    """Sample function with multiple code issues"""
    one += 1; two += 2  # More than one statement on a single line (C0321)
    seven = eight  # Unused variable "seven" (W0612), undefined variable "eight" (E1101)
    return one + two + nine  # Undefined variable "nine" (E1101)

# TODO gets also picked up by PyLint (W0511)
