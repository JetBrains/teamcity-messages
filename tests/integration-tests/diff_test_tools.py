from service_messages import ServiceMessage


SCRIPT = "../diff_assert.py"


def expected_messages(package_name):
    return [

        ServiceMessage('testStarted', {'name': package_name + ".test_2_test"}),
        ServiceMessage('testFailed', {'name': package_name + ".test_2_test",
                                      "expected": "(|'eggs|',)", "actual": "spam"}),
        ServiceMessage('testFinished', {'name': package_name + ".test_2_test"}),


        ServiceMessage('testStarted', {'name': package_name + ".test_3_test"}),
        ServiceMessage('testFailed', {'name': package_name + ".test_3_test",
                                      "actual": "spam", "expected": "eggs"}),
        ServiceMessage('testFinished', {'name': package_name + ".test_3_test"}),


        ServiceMessage('testStarted', {'name': package_name + ".test_test"}),
        ServiceMessage('testFailed', {'name': package_name + ".test_test", "expected": "spam", "actual": "(|'eggs|',)"}),
        ServiceMessage('testFinished', {'name': package_name + ".test_test"}),



    ]
