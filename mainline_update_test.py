# coding: utf-8
#

import subprocess
import os
import sys
from time import sleep
import time
import datetime
import json
import unittest
from TestRunner import HTMLTestRunner

import uiautomator2 as u2
import system_common as sysc
import mainline_test as mt
from utils import *

# variables that need to be specified.
# -------------------------------------------------
# DO NOT login one account across multiple devices, 
# Google's secruity policy might make the account unavailable to download new Google Play or others. (?)
TEST_ACCOUNT='wx.test2'
PASSWORD='G00gl3test'
WIFI_SSID='GoogleGuestPSK'
WIFI_PASSWORD='pUp3EkaP'
# specify bundletool path
bundletool='bundletool-all-1.8.2.jar'
# specify module apks path that for sideloading
module_apks_path='S_modules/'
# specify mobly apk path
mobly_apk_dir="./mobly-bundled-snippets-debug.apk"
# -------------------------------------------------

TEST_DATA_PATH = "./test_data/"
time_format = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S.%f")
VERSION_INFO_FILE= TEST_DATA_PATH + "version_info" + "_" + time_format + ".txt"
MODULE_INFO_FILE = TEST_DATA_PATH + "module_info" + "_" + time_format + ".txt"
MODULE_WITH_VERSION_FILE = TEST_DATA_PATH + "module_with_version" + "_" + time_format + ".txt"


def filename_generator(base_name):
    # time_format = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
    time_format = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S.%f")
    filename = base_name + "_" + time_format
    return filename

d = u2.connect()

class ManualUpdateTestCase(mt.MainlineTestCase):
    """
    Verify Manual Update when device on Wi-Fi.
    """

    # def __init__(self, *args, **kwargs):

    #     super(ManualUpdateTestCase, self).__init__(*args, **kwargs)
    #     self.version_info = {}
    #     self.module_info = []
    #     self.module_and_version = {}


    def test_01_enable_testharness(self):

        sysc.enable_testharness() 
        # # wait 2.5 minutes for the device to finish reset and reboot into desktop.
        # sleep(150)
        mt.device_waitor(120)


    def test_02_calm_the_screen(self):

        sysc.screen_stay_on()


    def test_03_introduce_mobly(self):

        sysc.install_apk(mobly_apk_dir)


    def test_04_connect_to_wifi(self):

        sysc.connect_to_wifi(WIFI_SSID, WIFI_PASSWORD)


    def test_05_play_signin(self):

        mt.play_login(TEST_ACCOUNT, PASSWORD)


    def test_06_play_check_version(self):

        mt.check_play_update_menu_shown()


    def test_07_train_get_version(self):

        print_whereami(self)
        # file_version_info = filename_generator("version_info")
        version_content = self.get_train_version()
        with open(VERSION_INFO_FILE, 'w') as f:
            f.write(str(version_content))
            # f.write(json.dumps(version_content))
        print_whereami(self)

    def test_08_train_get_module_list(self):

        print_whereami(self)
        module_content = self.get_module_list()
        with open(MODULE_INFO_FILE, 'w') as f:
            f.write(str(module_content))
        print_whereami(self)

    def test_09_train_trigger_instant_hygiene(self):

        print_whereami(self)
        mt.trigger_instant_hygiene()
        mt.check_play_update_menu_shown()
        print_whereami(self)

    def test_10_train_trigger_update(self):

        mt.trigger_module_update()
        # if d.wait_activity("com.google.android.finsky.systemupdateactivity.SettingsSecurityEntryPoint", timeout=10.0):
        # System update available
        if d(textContains="Download").exists(timeout=10.0):
            d.screenshot(TEST_DATA_PATH + "system_update_available.png")
            d(text="Download & install").click()
            # if d.wait_activity("com.google.android.finsky.systemupdateactivity.SystemUpdateActivity", timeout=10.0):
            self.assertTrue(d(textContains="Restart").wait(timeout=120.0), "Download & install probably not started or failed.")

        # Already silently installed updates
        elif d(textContains="Restart").wait(timeout=10.0):
            d.screenshot(TEST_DATA_PATH + "train_restart_to_update.png")
            d(text="Restart now").click()
        # Already up to date (installed and rebooted)
        elif d(textContains="up to date").wait(timeout=10.0):
            d.screenshot(TEST_DATA_PATH + "train_up_to_date.png")
        else:
            self.assertTrue(False, "update dialog not found, probably Play Store is too old.")

        mt.device_waitor(50)

    def test_11_train_verify_version(self):

        new_version_info = self.get_train_version()
        with open(VERSION_INFO_FILE, 'r') as f:
            old_version_info=eval(f.read()) # use eval() to covert string to it's "should be" intellgently.
        print("\nold version info:\n")
        print(old_version_info)

        with open(VERSION_INFO_FILE, 'a') as fv:
            fv.write("\n\n" + str(new_version_info))
            # fv.write("\n" + json.dumps(new_version_info))

        # old_version_info = json.loads(old_version_info)
        self.assertTrue(int(new_version_info['versionCode']) > int(old_version_info['versionCode']))
        self.assertTrue(int(new_version_info['minSdk']) >= int(old_version_info['minSdk']))
        self.assertTrue(int(new_version_info['targetSdk']) >= int(old_version_info['targetSdk']))

        # covert like '2022-01-01' into python standard date format.
        old_date = time.strptime(old_version_info['versionName'], '%Y-%m-%d')
        new_date = time.strptime(new_version_info['versionName'], '%Y-%m-%d')
        self.assertTrue(new_date > old_date)


    def test_12_train_verify_module_list(self):

        new_module_info = self.get_module_list()
        with open(MODULE_INFO_FILE, 'r') as f:
            old_module_info = eval(f.read())

        with open(MODULE_INFO_FILE, 'a') as f:
            f.write("\n\n" + str(new_module_info) )


        difference_set = set(new_module_info) - set(old_module_info)
        # if the new set is greater than the old one, iow, the combined set has content
        # self.assertTrue(difference_set, "mainline train update probably failed, module packages not updated.")
        if difference_set:
            print("\nmainline train update succeeds.\n")
            print("new added modules:\n " + str(difference_set))
        else:
            # print("mainline train update failed.")
            self.assertTrue(False, "mainline train update probably failed, module packages not updated.")


class SideloadModulesTestCase(mt.MainlineTestCase):
    """
    Verify update on OEM devices via sideloading moduels. 
    """

    maxDiff=None
    version_info={'versionCode': '310000000', 'minSdk': '29', 'targetSdk': '31', 'versionName': '2021-09-01'}
    module_info=['com.google.android.ext.services', 'com.google.android.permissioncontroller']
    module_and_version={'com.google.android.ext.services': '310727000', 'com.google.android.permissioncontroller': '310733000', 'com.google.android.documentsui': '310727000'}

    # def setUp(self):
    #     # self.maxDiff=None
    #     print_whereami(self)

    # def tearDown(self):
    #     print_whereami(self)


    def set_prop(self, pname, pvalue):
        # self.__setattr__(pname, pvalue)
        setattr(SideloadModulesTestCase, pname, pvalue)

    def get_prop(self, pname):
        # return self.__getattribute__(pname)
        return getattr(SideloadModulesTestCase, pname)

    def test_01_enable_testharness(self):

        sysc.enable_testharness() 
        # wait 2.5 minutes for the device to finish reset and reboot into desktop.
        mt.device_waitor(120)


    def test_02_calm_the_screen(self):

        sysc.screen_stay_on()


    def test_03_train_get_version(self):

        print_whereami(self)
        # global old_version_info
        # old_version_info = self.get_train_version()
        self.set_prop('version_info', self.get_train_version())
        print_whereami(self)


    def test_04_train_get_module_list(self):

        print_whereami(self)
        # global old_module_info
        # old_module_info = self.get_module_list()
        self.set_prop('module_info', self.get_module_list())
        print_whereami(self)

    def test_05_train_get_module_and_version(self):

        print_whereami(self)
        # global old_module_and_version
        # old_module_and_version = self.get_train_module_and_version()
        self.set_prop('module_and_version', self.get_train_module_and_version())
        print(self.get_prop('module_and_version'))
        print_whereami(self)


    def test_06_train_sideload_modules(self):

        print_whereami(self)
        self.sideload_modules(bundletool, module_apks_path)

        # sleep(6) # time buffer
        new_version_info = self.get_train_version()
        old_version_info = self.get_prop('version_info')
        print("\nold version info:\n")
        print(old_version_info)
        self.assertTrue(int(new_version_info['versionCode']) > int(old_version_info['versionCode']))
        self.assertTrue(int(new_version_info['minSdk']) >= int(old_version_info['minSdk']))
        self.assertTrue(int(new_version_info['targetSdk']) >= int(old_version_info['targetSdk']))

        # covert like '2022-01-01' into python standard date format.
        old_date = time.strptime(old_version_info['versionName'], '%Y-%m-%d')
        new_date = time.strptime(new_version_info['versionName'], '%Y-%m-%d')
        self.assertTrue(new_date > old_date)

        new_module_info = self.get_module_list()
        old_module_info = self.get_prop('module_info')
        print("\nold modules:\n" + str(old_module_info))

        # difference_set = set(new_module_info) - set(old_module_info)
        # # if the new set is greater than the old one, iow, the combined set has content
        # self.assertTrue(difference_set, "sideloading modules update probably failed, module packages not updated.")
        # print("\nnew added modules:\n " + str(difference_set))

        listc = [item for item in old_module_info if item not in new_module_info]
        # listc should not have elements, otherwise new_module_info does not fully contain old_module_info.
        # self.assertFalse(listc, “old_module_info has elements not in new_module_info”)
        if listc:
          self.assertFalse(listc, "sideloading modules update failed, the amount of new modules after reboot is smaller than old ones before sideloading.")
        else: # listc is empty
          listd = [item for item in new_module_info if item not in old_module_info]
          print("sideloading modules update succeeds, new added modules(could be empty):\n")
          print(listd, "\n") # listd is also allowed to be empty, since new_module_info could be equal to old_module_info.

        print_whereami(self)


    def test_07_train_rollback_modules(self):

        print_whereami(self)
        try:
            # self.sideloading(bundletool, module_apks_path)

            # rollback primary train modules, no effect for rollbacking moduels after sideloading..
            os.system("adb shell pm rollback-app com.google.android.modulemetadata")
            old_module_and_version = self.get_prop('module_and_version')
            rollbacked_module_and_version = self.get_train_module_and_version()
            print("\ndetailed modules with their versionCode after rollback.\n")
            print(rollbacked_module_and_version, "\n")
            print("\ndetailed old modules with versionCode:\n")
            print(old_module_and_version, "\n")
            print("\ndifference between two sets:\n")
            print(set(old_module_and_version.items())^set(rollbacked_module_and_version.items()), "\n")
            self.assertDictEqual(old_module_and_version, rollbacked_module_and_version, "rollback failed, some module not rollbacked.")
        finally:
            print_whereami(self)


    def check_particular_module_rollback(self, intent_name, package_name):

        print_whereami_head(self)
        try:
            self.module_killer(intent_name, package_name, 2)
            sleep(5)
            old_mav = self.get_prop('module_and_version')
            print(old_mav)
            old_versioncode = old_mav[package_name]
            current_mav = self.get_train_module_and_version()
            print(current_mav)
            current_versioncode = current_mav[package_name]
            self.assertEqual(old_versioncode, current_versioncode, "rollback for " + package_name + " failed.")
        except KeyError:
            print(package_name + " Not found in " + str(old_mav))
        finally:
            print_whereami_tail(self)


    def test_08_train_rollback_particular_module(self):
        testm1_intent="android.intent.action.OPEN_DOCUMENT_TREE"
        testm1_packagename="com.google.android.documentsui"
        testm2_intent=""
        testm2_packagename=""
        testm3_intent=""
        testm3_packagename=""
        print_whereami(self)
        try:
            # self.sideloading(bundletool, module_apks_path)
            self.check_particular_module_rollback(testm1_intent, testm1_packagename)
            sleep(6)
            # self.check_particular_module_rollback(testm2_intent, testm2_packagename)
            # sleep(6)
            # self.check_particular_module_rollback(testm3_intent, testm3_packagename)
            # self.check_particular_module_rollback()
        finally:
            print_whereami(self)



if __name__ == '__main__':

    suite = unittest.TestSuite()
    suite.addTest(ManualUpdateTestCase("test_07_train_get_version"))
    # suite.addTest(ManualUpdateTestCase("test_08_train_get_module_list"))
    # suite.addTest(ManualUpdateTestCase("test_09_train_trigger_instant_hygiene"))
    # suite.addTest(ManualUpdateTestCase("test_10_train_trigger_update"))
    suite.addTest(ManualUpdateTestCase("test_11_train_verify_version"))
    # suite.addTest(ManualUpdateTestCase("test_12_train_verify_module_list"))

    runner = unittest.TextTestRunner()
    runner.run(suite)

    # c1 = ManualUpdateTestCase()
    # c1.test_07_train_get_version()

    