On implementing new framework support
-------------------------------------

Please check the following things:

* Skipped tests
* Expected failures/Unexpected success
* stderr and stdout should go via testStdErr and testStdOut messages
* testStdErr and testStdOut should not take large output (~ >50K), you may split it by chunks
* Do not forget about Python 2.4, 2.5, 2.6
* Failures in setup, teardown on all levels (class, module, namespace)
* Syntax and other errors when collecting tests should be correctly reported
* Internal test framework errors should be reported if possible
* doctests
* Test generators and parametrized tests 
* assert failures vs generic exceptions (failure/error)
* Coverage support
