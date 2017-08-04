from service_messages import ServiceMessage


SCRIPT = "../diff_assert.py"


def expected_messages(test_name):
    return [
        ServiceMessage('testStarted', {'name': test_name}),
        ServiceMessage('testFailed', {'name': test_name, "expected": "spam", "actual": "eggs"}),
        ServiceMessage('testFinished', {'name': test_name}),
    ]
