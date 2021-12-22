# coding: utf-8
#
import sys
import os
import logging
from time import sleep
import uiautomator2 as u2
from uiautomator2 import UiObjectNotFoundError

from mobly import base_test
from mobly.controllers import android_device as ad

d = u2.connect()
os_version = d.device_info.get('version')
PASSWORD = "G00gl3test"


def to_Settings():

	d.shell("am start com.android.settings/com.android.settings.Settings")


def to_Settings_Security():

	d.shell("am start -a android.settings.SECURITY_SETTINGS")


def stop_Settings_activity():
	''' force close activity to keep env clean. '''
	d.shell("am force-stop com.android.settings")


def screen_stay_on():

	d.shell("settings put global stay_on_while_plugged_in 7")
	# the unit is milliseconds, set device goes to sleep after 1 hours' inactivity.
	d.shell("settings put system screen_off_timeout 3600000")
	# set screen lock to be None.
	d.shell("locksettings set-disabled true")


def enable_testharness():

	d.shell("cmd testharness enable")

def install_mobly_apk():

	apk_dir="./mobly-bundled-snippets-debug.apk"
	os.system('adb install -r -d -g ' + apk_dir)


def connect_to_wifi(ssid, pswd):

	# using d1 = ad.AndroidDevice() is supposed to be safer, but this is more convenient.
	d1 = ad.AndroidDevice()
	d1.load_snippet('mbs', 'com.google.android.mobly.snippet.bundled')
	d1.mbs.wifiEnable()
	d1.mbs.wifiConnectSimple(ssid, pswd)
	# d1.mbs.wifiConnectSimple("GoogleGuestPSK-Legacy", "pUp3EkaP")



def minutemaid_login(account_name, pswd):

	d.implicitly_wait(18.0)
	if d.wait_activity(".auth.uiflows.minutemaid.MinuteMaidActivity", timeout=30):
		# redundant click and wait to improve the success rate.
		# d(resourceId="identifierId").click()
		# sleep(1)
		# d.send_keys(account_name)
		d(resourceId="identifierId").send_keys(account_name)
		if not d(focused=True).exists(timeout=3):
			sleep(6)
			d.xpath('//*[@resource-id="com.google.android.gms:id/sud_layout_content"]/android.webkit.WebView[1]/android.webkit.WebView[1]/android.view.View[3]/android.view.View[1]/android.view.View[1]/android.view.View[3]').click()
		sleep(1)
		# d.send_keys(account_name)
		d(focused=True).set_text(account_name)
		sleep(1)
		d(text="Next").click()
		sleep(2)
		# d.send_keys(pswd, clear=True)
		d(focused=True).set_text(pswd)
		d(text="Next").click()
		# agree the TOS
		d(text="I agree").click()
		# if d.wait_activity(".setupservices.GoogleServicesActivity", timeout=10): # even not fresh login also trigger this Activity, just no More and Accept dialog.
		# if d(text="More").wait(3):
		if d(text="More").exists(timeout=5):
			d(text="More").click()
			d(text="Accept").click()


def add_google_account(account_name, pswd):

	d.implicitly_wait(10.0)
	attempts = 3
	for i in range(attempts):
		try:
			# or adb shell am start -n com.android.settings/.accounts.AddAccountSettings
			# ! or adb shell sm start -n com.google.android.gms/.auth.uiflows.addaccount.AccountIntroActivity 
			d.shell("am start -a android.settings.ADD_ACCOUNT_SETTINGS")
			d(resourceId="android:id/title", text="Google").click()
			minutemaid_login(account_name, pswd)

		except UiObjectNotFoundError:
			if i < attempts -1: # i steps from 0
				continue
			else:
				raise
		break

	# deal with the screen that only displays for the first fresh login.
	# d1 = ad.AndroidDevice()
	# d1.load_snippet('mbs', 'com.google.android.mobly.snippet.bundled')
	# if len(d1.mbs.listAccounts()) == 1: # So the account is the first one in this device.
	# 	if d.wait_activity(".setupservices.GoogleServicesActivity", timeout=30):
	# 		d(text="More").click()
	# 		d(text="Accept").click()

	stop_Settings_activity()


def remove_google_account(account_name):

	# open Passwords & accounts
	d.shell("am start -a android.settings.SYNC_SETTINGS")
	# d(scrollable=True).fling()
	d(textContains=account_name).click()
	d(text="Remove account").click()
	# confirm
	d(resourceId="android:id/button1").click()
	stop_Settings_activity()


def test_add_remove_account():
	add_google_account("wx.test2", PASSWORD)
	add_google_account("wx.test1", PASSWORD)
	add_google_account("wx.test3", PASSWORD)
	# remove_google_account("wx.test1")


def test_remove_all_google_accounts():
	d.shell("am start -a android.settings.SYNC_SETTINGS")
	sleep(2)
	while d(textContains='gmail.com'):
		d(textContains='gmail.com').click()
		d(text="Remove account").click()
		# confirm
		d(resourceId="android:id/button1").click()
		stop_Settings_activity()
		d.shell("am start -a android.settings.SYNC_SETTINGS")
		sleep(2)
		continue
	else:
		stop_Settings_activity()


def detect_if_device_connected():

	while True:
	    sleep(2)
	    print("waiting for device to be connected...")
	    adb_devices_line = os.popen('adb devices |grep device |wc -l').read().strip()
	    if int(adb_devices_line) > 1:
	        sleep(10)
	        break


# # Deprecated
# def to_Settings():

# 		
# 		d.unlock()
# 		d.open_quick_settings()
# 		d(resourceId="com.android.systemui:id/settings_button_container").click()

# 	except u2.UiObjectNotFoundError:
# 		# if plan A failed, try plan B ;)
# 		d.unlock()
# 		d.press("home")
# 		d(scrollable=True).scroll.toEnd()
# 		d(scrollable=True).scroll.to(text="Settings")
# 		d(text="Settings").click()


# example: go to System item - to_Settings_item("System")
def to_Settings_item(item_name):

	to_Settings()
	try:
		# must add scroll.toEnd() or filing() to let the scanner recognize all the items.
		d(scrollable=True).fling.toEnd()
		d(scrollable=True).scroll.to(text=item_name)
		d(text=item_name).click()

	except u2.UiObjectNotFoundError:
		# find the item entry by searching in the head of the Settings' page.
		d(scrollable=True).fling.vert.backward()
		d(resourceId="com.android.settings:id/search_action_bar_title").click()
		d.send_keys(item_name, clear=True)
		# d(scrollable=True).scroll.to(text="Search Support")
		d(resourceId="android:id/title", text=item_name).click()


def reset_device():

	d.unlock()
	to_Settings_item("System")
	if os_version == '11':
		d(scrollable=True).fling()
		d(scrollable=True).scroll.to(text="Reset options")
	elif os_version == '12':
		d(scrollable=False).fling()
	d(text="Reset options").click()
	d(resourceId="android:id/title", text="Erase all data (factory reset)").click()
	d(text="Erase all data").click()
	d.wait_activity(".Settings$FactoryResetConfirmActivity", timeout=15)
	d(text="Erase all data").click()
	# wait 3 minutes to let the reset done.
	sleep(180)


def setup_wizard_dealer(account_name, pswd):

	d(resourceId="com.google.android.pixel.setupwizard:id/start").click()
	d(text="Skip").click()
	# setup wifi, connect to GoogleGuestPSK
	d.xpath('//*[@content-desc="GoogleGuestPSK,Wifi three bars.,Secure network"]/android.widget.LinearLayout[1]').click()
	d.send_keys("pUp3EkaP", clear=True)
	d(resourceId="android:id/button1").click()
	# Getting your phone ready... This may take a few minutes (ineed)
	if d.device_info.get('version') == '11':
		d.wait_activity(".migrate.component.UsbD2dMigrateFlowActivity", timeout=180)
	elif d.device_info.get('version') == '12':
		d.wait_activity("com.google.android.apps.pixelmigrate.migrate.component.UsbD2dMigrateFlowActivity", timeout=180)
	d(text="Don’t copy").click()
	d.wait_activity(".auth.uiflows.minutemaid.MinuteMaidActivity", timeout=120)
	d(resourceId="com.google.andro bid.gms:id/sud_layout_content").click()
	d(resourceId="identifierId").click()
	d.send_keys(account_name, clear=True)
	d(text="Next").click()
	d.send_keys(pswd, clear=True)
	d(text="Next").click()
	d(text="I agree").click()
	d.wait_activity(".setupservices.GoogleServicesActivity", timeout=30)
	d(scrollable=True).scroll.toEnd()
	d(text="Accept").click()
	d.wait_activity(".password.SetupChooseLockPassword", timeout=60)
	d(text="Skip").click()
	d(resourceId="android:id/button1").click()
	d(text="Leave & get reminder").click()
	d.xpath('//*[@resource-id="android:id/content"]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.ScrollView[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.ScrollView[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.LinearLayout[1]/android.widget.LinearLayout[1]/android.widget.CheckBox[1]').click()
	d(text="Ok").click()

	# For R image (Android version 11)
	if d.device_info.get('version') == '11':
		d.wait_activity(".user.GestureIntroActivity", timeout=60)
		d(text="Skip").click()


def open_usb_debug():

	to_Settings_item("About phone")
	d(scrollable=True).scroll.toEnd()
	for i in range(1, 8):
		d(text="Build number").click()
	# back to desktop to clean the ui interface cache.
	for i in range(1, 4):
		d.press("back")


def disable_screen_lock():

	to_Settings_item("Security")
	d(scrollable=True).scroll.to(text="Screen lock")
	d(text="Screen lock").click()
	d(resourceId="android:id/title", text="None").click()
	# back to desktop to clean the ui interface cache.
	for i in range(1, 4):
		d.press("back")

def setup_screen_timeout():

	to_Settings_item("Display")
	d(resourceId="android:id/title", text="Screen timeout").click()
	d.xpath('//*[@resource-id="com.android.settings:id/recycler_view"]/android.widget.LinearLayout[7]/android.widget.LinearLayout[1]/android.widget.RadioButton[1]').click()
	d(resourceId="com.android.systemui:id/back").click()
	# back to desktop to clean the ui interface cache.
	for i in range(1, 4):
		d.press("back")



def clean_and_setup_device():
	reset_device()
	setup_wizard_dealer("wx.test1", "G00gl3test")
	disable_screen_lock()
	setup_screen_timeout()
	open_usb_debug()




if __name__ == '__main__':
	# globals()[sys.argv[1]](sys.argv[2], (sys.argv[3])) # need to be flexible.
	globals()[sys.argv[1]]()
	# to_Settings()
	# to_Settings_Security()
	# install_mobly_apk()
	# connect_to_wifi()
	# screen_stay_on()
	# test_remove_all_google_accounts()

	# reset_device()
	# setup_wizard_dealer("wx.test1", "G00gl3test")
	# to_Settings_item("Display")
	# disable_screen_lock()
	# setup_screen_timeout()
	# open_usb_debug()
	# clean_and_setup_device()