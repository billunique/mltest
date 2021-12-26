# coding: utf-8
#
import logging
import subprocess
import os
import sys
from time import sleep

def test_01():

	# sysop.enable_testharness() 
	# # wait 2.5 minutes for the device to finish reset and reboot into desktop.
	# sleep(150)
	# sleep(60) # wait for the device to power down.
	while True:
		sleep(1)
		print("sleep")
		adb_devices_line = os.popen('adb devices |grep device |wc -l').read().strip()
		if int(adb_devices_line) > 1:
			sleep(5)
			break

def test_02():

	# proc = subprocess.Popen(["cat", "/etc/services"], stdout=subprocess.PIPE, shell=True) # shell=True will open a new shell console in background which can not be seen.
	# proc = subprocess.Popen(["cat", "/etc/services"], stdout=subprocess.PIPE)
	# without universal_newlines=True, the output is of type bytes, which will cause "\n" just shows as char and untidy look.
	proc = subprocess.Popen(["cat", "/etc/services"], stdout=subprocess.PIPE, universal_newlines=True)
	(out, err) = proc.communicate()
	print(out)


if __name__ == '__main__':
	test_02()
	# globals()[sys.argv[1]]()