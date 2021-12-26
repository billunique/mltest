# coding: utf-8
#
import uiautomator2 as u2
import logging
import system_common_op as sysop
from time import sleep
import os
import sys
import unittest


d = u2.connect()

def get_train_version() -> dict:

	#only take the first 2 matches for parsing and comparing.
	version_info = d.shell("dumpsys package com.google.android.modulemetadata | grep -m 2 -E 'versionName|versionCode'").output
	print("raw version info:\n")
	print(version_info)
	# split() splits on one or more whitespace chars, including "\n"
	# use list comprehensions to remove the elements might bothering, i.e, don't have "=" char.
	# ['versionCode=311318024', 'minSdk=31', 'targetSdk=31', 'versionName=2022-01-01', 'S+'] -> 
	# ['versionCode=311318024', 'minSdk=31', 'targetSdk=31', 'versionName=2022-01-01']
	list_version_info = [x for x in version_info.split() if "=" in x]
	# convert the list to key-value pairs dict.
	# ['versionCode=311318024', 'minSdk=31', 'targetSdk=31', 'versionName=2022-01-01'] ->
	# {'versionCode': '311318024', 'minSdk': '31', 'targetSdk': '31', 'versionName': '2022-01-01'}
	dict_version_info = dict(pair.split('=') for pair in list_version_info if pair)
	print("version info of this build in dict:\n")
	print(dict_version_info)

	return dict_version_info


def get_module_list() -> list:

	# return sample: ['com.google.android.ext.services', 'com.google.android.permissioncontroller', 'com.google.android.captiveportallogin', 'com.google.android.modulemetadata', 'com.google.android.networkstack']

	module_info = d.shell("pm get-moduleinfo").output
	print("\nraw current moudules info:\n")
	print(module_info)
	list_module_pkg = []
	for i in module_info.splitlines():
		list_module_pkg.append(i.split(":")[1].strip())

	# listl = [x.split(":")[1].strip() for x in module_info.splitlines()]
	
	print("list current modules in package names:\n")
	print(list_module_pkg)
	return list_module_pkg


def get_train_module_and_version() -> dict:

	list_module = get_module_list()
	output1 = os.popen("adb shell cmd package list packages --show-versioncode").readlines()
	output2 = os.popen("adb shell cmd package list packages --show-versioncode --apex-only").readlines()
	output_list = output1 + output2
	matched_line = []
	for l in list_module:
		for line in output_list:
			if l in line:
				matched_line.append(line.strip())
	print("\ntrain modules with their versionCode:\n")
	for _ in matched_line:
		print(_)

	print("\ntrain modules with their versionCode in pure mode:\n")

	matched_line_lite = [(x.split(":")[1].replace(" versionCode", "") + ":" + x.split(":")[2]) for x in matched_line]
	for _ in matched_line_lite:
		print(_)
	dict_module_and_versioncode = dict(pair.split(":") for pair in matched_line_lite)
	# print(dict_module_and_versioncode)
	return dict_module_and_versioncode


def get_os_build_info():
	
	build_info = d.shell("getprop | grep 'build.description'").output
	print(build_info)
	return build_info


def trigger_update_byui():

	sysop.to_Settings_Security()
	d(resourceId="android:id/title", text="Google Play system update").click()


def trigger_module_update():

	d.shell("am start -a android.settings.MODULE_UPDATE_SETTINGS")
	# d.shell("am start -n com.android.vending/com.google.android.finsky.systemupdateactivity.SystemUpdateActivity")


def chimera_debug():

	d.shell("am start -n com.google.android.gms/com.google.android.gms.chimera.debug.ChimeraDebugActivity")


def download_install():

	trigger_update()
	d(text="system update available").wait(timeout=20.0)
	d.screenshot("system_update_available.png")
	wct = d.watch_context()
	wct.when("Download & install").click()
	# d(resourceId="com.android.vending:id/0_resource_name_obfuscated", text="Download & install").click()

def restart_to_update():

	trigger_update()
	wct = d.watch_context()
	wct.when("Restart now").click()
	d.screenshot("restart_to_update.png")

def already_up_to_date():

	trigger_update()
	d(text="Your device is up to date").wait(timeout=30.0)
	d.screenshot("up_to_date.png")


if __name__ == '__main__':
	globals()[sys.argv[1]]()