# coding: utf-8
#
import sys
import subprocess
import os
import logging
from time import sleep
import uiautomator2 as u2
from uiautomator2 import UiObjectNotFoundError
from mobly.controllers import android_device as ad

# define d here, or inside the function, or pass it as adbdevice object to function, all work.
# because u2.connect() is to get the adb device (connection) object, not to create a new one.
d = u2.connect()


# Better to open via command line.
# -------------------------------------------------
# open_play_account_menu()
# is_play_latest(), i.e, to Google Play Settings.
# -------------------------------------------------


def to_Settings():

	os.system("adb shell am start com.android.settings/com.android.settings.Settings")


def to_Settings_Security():

	os.system("adb shell am start -a android.settings.SECURITY_SETTINGS")


def stop_Settings_activity():
	''' force close activity to keep env clean. '''
	os.system("adb shell am force-stop com.android.settings")


def to_Settings_PaA():
	''' to Settings - Passwords & accounts. '''
	os.system("adb shell am start -a android.settings.SYNC_SETTINGS")


def screen_stay_on():

	os.system("adb shell settings put global stay_on_while_plugged_in 7")
	# the unit is milliseconds, set device goes to sleep after 1 hours' inactivity.
	os.system("adb shell settings put system screen_off_timeout 3600000")
	# set screen lock to be None.
	os.system("adb shell locksettings set-disabled true")


def enable_testharness():

	os.system("adb shell cmd testharness enable")


def install_apk(apk_dir):

	print("\ninstalling " + apk_dir + " ......")
	os.system('adb install -r -d -g ' + apk_dir)


def connect_to_wifi(ssid, pswd):

	# using d1 = ad.AndroidDevice() is supposed to be safer, but this is more convenient.
	d1 = ad.AndroidDevice()
	d1.load_snippet('mbs', 'com.google.android.mobly.snippet.bundled')
	d1.mbs.wifiEnable()
	d1.mbs.wifiConnectSimple(ssid, pswd)
	# d1.mbs.wifiConnectSimple("GoogleGuestPSK-Legacy", "pUp3EkaP")


def get_os_build_info():
	
	build_info = os.popen("adb shell getprop | grep 'build.description'").read()
	print("\nAndroid build: ", build_info)
	return build_info


def trigger_crash_app(package_name):

	os.system("adb shell am crash " + package_name)


def chimera_debug():

	os.system("adb shell am start -n com.google.android.gms/com.google.android.gms.chimera.debug.ChimeraDebugActivity")


def back2home():
	# d.open_notification() # triiger uiautomator2 to auto-recover if it's not working, like in the case just reboot.
	for i in range(6):
	    d.press("back")
	d.press("home")


def complete_setup_by_installing_app():
	d.open_notification()
	d(textContains="Complete setup").click()
	d(text="Ok").click()


def reboot_device():
	os.system("adb reboot")


def get_current_activity():
	activity_info = os.popen("adb shell dumpsys activity activities | grep mResumedActivity").read()
	activity_name = activity_info.split()[-2]
	print(activity_info)
	return activity_name


def module_killer(intent_name: str, package_name: str, kill_times=10):
    """
    intent_name sample: android.intent.action.OPEN_DOCUMENT_TREE
    package_name sample: com.google.android.documentsui
    """
    print("Will kill poor " + package_name + " " + str(kill_times) + " times......\n")
    for i in range(kill_times):
        os.system("adb shell am start -a " + intent_name) 
        sleep(4)
        os.system("adb shell am crash " + package_name)
        sleep(2)


def device_waitor(base_wait_time):
    """ wait the device to be connected, once connected exit waiting and go next, otherwise keep waiting. """
    sleep(base_wait_time)
    while True:
        sleep(2)
        print("waiting for device to be connected...")
        adb_devices_line = os.popen('adb devices |grep device |wc -l').read().strip()
        if int(adb_devices_line) > 1:
            sleep(10)
            break


def wait_till_finished(command):
	# use split() to perfectly prepare the command format (a list) to subprocess
    proc = subprocess.Popen(command.split(), stdout=subprocess.PIPE, universal_newlines=True)
    (output, err) = proc.communicate()
    print(output)

    while True:
        sleep(1)
        # poll() function to check the return code of the process. It will return None while the process is still running.
        return_code = proc.poll()
        if return_code is not None:
            # Process has finished
            sleep(3) # time buffer
            break



######################################
# Below functions are not in use.
######################################

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

	d = u2.connect()
	os_version = d.device_info.get('version')
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

	d = u2.connect()
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


def open_usb_debug(adbdevice):

	d = adbdevice
	to_Settings_item("About phone")
	d(scrollable=True).scroll.toEnd()
	for i in range(1, 8):
		d(text="Build number").click()
	# back to desktop to clean the ui interface cache.
	for i in range(1, 4):
		d.press("back")


def disable_screen_lock(adbdevice):

	d = adbdevice
	to_Settings_item("Security")
	d(scrollable=True).scroll.to(text="Screen lock")
	d(text="Screen lock").click()
	d(resourceId="android:id/title", text="None").click()
	# back to desktop to clean the ui interface cache.
	for i in range(4):
		d.press("back")

def setup_screen_timeout(adbdevice):

	d = adbdevice
	to_Settings_item("Display")
	d(resourceId="android:id/title", text="Screen timeout").click()
	d.xpath('//*[@resource-id="com.android.settings:id/recycler_view"]/android.widget.LinearLayout[7]/android.widget.LinearLayout[1]/android.widget.RadioButton[1]').click()
	d(resourceId="com.android.systemui:id/back").click()
	# back to desktop to clean the ui interface cache.
	for i in range(4):
		d.press("back")



def clean_and_setup_device():
	reset_device()
	setup_wizard_dealer("wx.test1", "G00gl3test")
	disable_screen_lock()
	setup_screen_timeout()
	open_usb_debug()


def test_d_conflict():
	open_usb_debug(u2.connect())
	disable_screen_lock(u2.connect())
	setup_screen_timeout(u2.connect())



if __name__ == '__main__':
	# globals()[sys.argv[1]](sys.argv[2], (sys.argv[3])) # need to be flexible.
	# globals()[sys.argv[1:]]()
	# to_Settings()
	# to_Settings_Security()
	# install_mobly_apk()
	connect_to_wifi("wx.test1", "G00gl3test")
	# screen_stay_on()
	# test_remove_all_google_accounts()
	# setup_wizard_dealer("wx.test1", "G00gl3test")
	# to_Settings_item("Display")
	# open_usb_debug()
	# command="adb shell pm rollback-app com.google.android.modulemetadata"
	# wait_till_finished(command)
