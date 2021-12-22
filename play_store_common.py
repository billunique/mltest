# coding: utf-8
#
import sys
import logging
from time import sleep
import uiautomator2 as u2
from uiautomator2 import UiObjectNotFoundError

import system_common_op as sysop

d = u2.connect()

def open_google_play_by_icon():

	logging.info("Go to Home screen and open Google Play.")
	d.press("home")
	d(text="Play Store").click()


def open_google_play():

	d.shell("am start -n com.android.vending/.AssetBrowserActivity")


def open_account_menu():

	try:
		open_google_play_by_icon()
		sleep(1)
		# account menu already opened.
		if d(text="Library").wait(timeout=2.0):
			pass
		# click the account avatar by coordinate, no better ways.
		else:
			d.click(0.89, 0.072)
	except u2.UiObjectNotFoundError:
		# exit all activity to return to home screen.
		for i in range(1, 6):
			d.press("back")

		open_account_menu()



def play_login(account_name, pswd):

	attempts = 3
	for i in range(attempts):
		try:
			open_google_play_by_icon()
			d(resourceId="com.android.vending:id/0_resource_name_obfuscated", text="Sign in").click()
			sysop.minutemaid_login(account_name, pswd)

		except UiObjectNotFoundError:
			if i < attempts -1: # i steps from 0
				continue
			else:
				raise
		break
	if d.wait_activity(".AssetBrowserActivity", timeout=20):
		logging.info("Play login with " + account_name + " successfully!")


def play_logout(test_account):

	open_account_menu()
	# click the "expand menu" button near the avatar.
	d.click(0.884, 0.228)
	d(resourceId="com.android.vending:id/0_resource_name_obfuscated", text="Manage accounts on this device").click()
	d(resourceId="android:id/title", text=test_account + "@gmail.com").click()
	# choose remove the account
	d(resourceId="com.android.settings:id/button").click()
	# confirm remove
	d(resourceId="android:id/button1").click()


def check_if_latest():

	open_account_menu()
	d(text="Settings").click()
	d(text="About").click()
	d(text="Play Store version").click()
	if d(textContains="A new version").wait(timeout=3.0):
		d(text="Got it").click()
		print('Play store need to be updated.')
		d.screenshot("play_store_need_update.png")
		uptodate = False
	else:
		print("Play store is already up-to-date.")
		d.screenshot("play_store_latest.png")
		uptodate = True

	return uptodate


def force_stop_play():

	# d.press("home")
	# d(text="Play Store").long_click()
	# d(description="App info").click()
	# # Force stop button
	# d(resourceId="com.android.settings:id/button3").click()
	# # OK button
	# d(resourceId="android:id/button1").click()

	d.shell("am force-stop com.android.vending")


if __name__ == '__main__':

	# force_stop_play()
	play_login("wx.test1", "G00gl3test")
