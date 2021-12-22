# coding: utf-8
#

from time import sleep
from mobly import base_test
from mobly import test_runner
from mobly.controllers import android_device
import uiautomator2 as u2

d = u2.connect()

class HelloWorldTest(base_test.BaseTestClass):

	def setup_class(self):
		# Registering android_device controller module declares the test's 
		# dependency on Android device hardware. By default, we expect at least one
		# object is created from this.
		self.ads = self.register_controller(android_device)
		self.dut = self.ads[0]
		# Start Mobly Bundled Snippets (MBS)
		self.dut.load_snippet('mbs', 'com.google.android.mobly.snippet.bundled')

	def test_hello(self):
		self.dut.mbs.makeToast('Hello World!')
		sleep(2)

	def test_bye(self):
		self.dut.mbs.makeToast('Goodbye!')
		sleep(2)

	def test_remove_account(self):
		self.dut.mbs.removeAccount("wx.test1@gmail.com")

	def test_get_version(self):
		print(d.info)
		print(d.app_current)
		print(d.serial, d.wlan_ip)
		print(d.device_info)
		# d.screenshot("test.jpg")
		# print(d.shell("pwd"))
		version_info = d.shell("dumpsys package com.google.android.modulemetadata | grep -E 'versionName|versionCode'").output
		print(version_info)


if __name__ == '__main__':
	# d.press("home")
	# d(text="Play Store").click()
	test_runner.main()



