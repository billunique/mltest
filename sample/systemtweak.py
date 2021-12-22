# coding: utf-8
#

from time import sleep
from mobly import base_test
from mobly import test_runner
from mobly import suite_runner
from mobly import asserts
from mobly.controllers import android_device


class SystemTweakTest(base_test.BaseTestClass):

	def setup_class(self):
		self.ads = self.register_controller(android_device)
		self.dut = self.ads[0]
		self.dut.load_snippet('mbs', 'com.google.android.mobly.snippet.bundled')

	def test_bt_switch(self):
		self.dut.mbs.btDisable()
		sleep(3)
		self.dut.mbs.btEnable()

	def test_wifi_connect(self):
		self.dut.mbs.wifiEnable()
		self.dut.mbs.wifiConnectSimple("GoogleGuestPSK", "pUp3EkaP")


if __name__ == '__main__':
	test_runner.main()


