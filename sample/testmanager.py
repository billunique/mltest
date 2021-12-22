# coding: utf-8
#

from mobly import suite_runner
import helloworldtest
import systemtweak
import versioncodetest


# selected_tests = suite_runner.compute_selected_tests(
# 		[
# 		  'HelloWorldTest',
# 		  'SystemTweakTest',
# 		  'VersionCodeTest'
# 		],
# 		[
# 		  'HelloWorldTest.test_hello',
# 		  'SystemTweakTest',
# 		  'VersionCodeTest'
# 		]
# 	)

if __name__ == '__main__':
	suite_runner.run_suite(
		[
		  helloworldtest.HelloWorldTest,
		  systemtweak.SystemTweakTest,
		  versioncodetest.VersionCodeTest
		]
	)

	# suite_runner.run_suite(selected_tests)