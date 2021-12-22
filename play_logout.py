# coding: utf-8
#
import uiautomator2 as u2
import logging

d = u2.connect()

def play_logout(test_account):

	logging.info("Go to Home screen and open Google Play.")
	d.press("home")
	d(text="Play Store").click()
	# click the account avatar by coordinate, no better ways.
	d.click(0.89, 0.072) 
	# click the "expand menu" button near the avatar.
	d.click(0.884, 0.228)
	d(resourceId="com.android.vending:id/0_resource_name_obfuscated", text="Manage accounts on this device").click()
	d(resourceId="android:id/title", text=test_account + "@gmail.com").click()
	# choose remove the account
	d(resourceId="com.android.settings:id/button").click()
	# confirm remove
	d(resourceId="android:id/button1").click()

if __name__ == '__main__':
	play_logout("wx.test1")