# coding: utf-8
#

from time import sleep
from mobly import base_test
from mobly import test_runner
from mobly import asserts
from mobly.controllers import android_device


class VersionCodeTest(base_test.BaseTestClass):

	def setup_class(self):
		self.ads = self.register_controller(android_device)
		self.dut = self.ads[0]
		self.dut.load_snippet('mbs', 'com.google.android.mobly.snippet.bundled')

	def test_expected_versionCode(self):
		expected_code = self.user_params.get('version_code')
		# if code:
		# 	self.dut.mbs.makeToast("Right version code!")
		# else:
		# 	self.dut.mbs.makeToast("Not expected version code!")
		actual_code = 310005600
		asserts.assert_equal(
			actual_code, expected_code, 
			'Not expected version code!')


if __name__ == '__main__':
	test_runner.main()


