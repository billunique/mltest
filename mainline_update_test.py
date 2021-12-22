# coding: utf-8
#
import uiautomator2 as u2
import system_common_op as sysop
import play_store_common as psc
import train_common as tc
import subprocess
import os
import sys
from time import sleep
import time

import unittest
from TestRunner import HTMLTestRunner

# variables that need to be specified.
# -------------------------------------------------

# DO NOT login one account across multiple devices, Google's secruity policy could make the account unavailable to download new Google Play or others.
TEST_ACCOUNT='wx.test2'
PASSWORD='G00gl3test'
WIFI_SSID='GoogleGuestPSK'
WIFI_PASSWORD='pUp3EkaP'
# specify bundletool path
bundletool='bundletool-all-1.8.2.jar'
# specify module apks that for sideloading
module_apks_path='S_modules/'

# -------------------------------------------------

# created the dict and show as a sample, will be overrided anyway.
old_version_info={'versionCode': '310000000', 'minSdk': '29', 'targetSdk': '31', 'versionName': '2021-09-01'}
old_module_info=['com.google.android.ext.services', 'com.google.android.permissioncontroller', 'com.google.android.captiveportallogin', 'com.google.android.modulemetadata', 'com.google.android.networkstack']


d = u2.connect()

class ManualUpdateTestCase(unittest.TestCase):
    """
    Verify Manual Update when device on Wi-Fi.
    """

    def test_01_enable_testharness(self):

        sysop.enable_testharness() 
        # # wait 2.5 minutes for the device to finish reset and reboot into desktop.
        # sleep(150)
        sleep(120)
        while True:
            sleep(1)
            print("waiting for device to be connected...")
            adb_devices_line = os.popen('adb devices |grep device |wc -l').read().strip()
            if int(adb_devices_line) > 1:
                sleep(5)
                break


    @unittest.skip("skip case")
    def test_init_uiautomator(self):
        # process = subprocess.run(["python3", "-m uiautomator2", "init"])
        # os.system('python3 -m uiautomator2 init') # u2.connect() does the auto initialization.
        pass

    def test_02_calm_the_screen(self):

        # sysop.disable_screen_lock()
        # sysop.setup_screen_timeout()
        sysop.screen_stay_on()


    def test_03_introduce_mobly(self):

        sysop.install_mobly_apk()


    def test_04_connect_to_wifi(self):

        sysop.connect_to_wifi(WIFI_SSID, WIFI_PASSWORD)


    def test_05_play_signin(self):

        psc.play_login(TEST_ACCOUNT, PASSWORD)


    def test_06_play_check_version(self):

        latest = psc.check_if_latest()
        if not latest:
            while True:
                sleep(2)
                print("wait the update of Google Play to complete...")
                sysop.to_Settings_Security()
                if d(text="Google Play system update").exists(timeout=2.0):
                    print("Google Play system update menu has showed.")
                    sleep(1)
                    break
                else:
                    sysop.stop_Settings_activity()
                    continue


    def test_07_train_get_version(self):

        global old_version_info
        old_version_info = tc.get_train_version()


    def test_08_train_get_module_list(self):

        global old_module_info
        old_module_info = tc.get_module_list()


    # def test_09_play_force_stop(self):

    #     psc.force_stop_play()


    def test_10_train_trigger_update(self):

        tc.trigger_module_update()
        # if d.wait_activity("com.google.android.finsky.systemupdateactivity.SettingsSecurityEntryPoint", timeout=10.0):
        # System update available
        if d(textContains="Download").exists(timeout=10.0):
            d(text="Download & install").click()
            # if d.wait_activity("com.google.android.finsky.systemupdateactivity.SystemUpdateActivity", timeout=10.0):
            self.assertTrue(d(textContains="Restart").wait(timeout=120.0), "Download & install probably not started or failed.")

        # Already silently installed updates
        elif d(textContains="Restart").wait(timeout=10.0):
            d(text="Restart now").click()
        # Already up to date (installed and rebooted)
        elif d(textContains="up to date").wait(timeout=10.0):
            pass
        else:
            self.assertTrue(False, "update dialog not found, probably Play Store is too old.")

        # sleep(120)
        # sysop.detect_if_device_connected()

    def test_11_train_verify_version(self):

        new_version_info = tc.get_train_version()
        print("\nold version info:\n")
        print(old_version_info)
        self.assertTrue(int(new_version_info['versionCode']) > int(old_version_info['versionCode']))
        self.assertTrue(int(new_version_info['minSdk']) >= int(old_version_info['minSdk']))
        self.assertTrue(int(new_version_info['targetSdk']) >= int(old_version_info['targetSdk']))

        # covert like '2022-01-01' into python standard date format.
        old_date = time.strptime(old_version_info['versionName'], '%Y-%m-%d')
        new_date = time.strptime(new_version_info['versionName'], '%Y-%m-%d')
        self.assertTrue(new_date > old_date)


    def test_12_train_verify_module_list(self):

        new_module_info = tc.get_module_list()
        difference_set = set(new_module_info) - set(old_module_info)
        # if the new set is greater than the old one, iow, the combined set has content
        # self.assertTrue(difference_set, "mainline train update probably failed, module packages not updated.")
        if difference_set:
            print("\nmainline train update succeeds.\n")
            print("new added modules:\n " + str(difference_set))
        else:
            # print("mainline train update failed.")
            self.assertTrue(False, "mainline train update probably failed, module packages not updated.")



class SideloadModulesTestCase(unittest.TestCase):
    """
    Verify update on OEM devices via sideloading moduels. 
    """
    # def test_01_enable_testharness(self):

    #     sysop.enable_testharness() 
    #     # wait 2.5 minutes for the device to finish reset and reboot into desktop.
    #     sleep(120)
    #     sysop.detect_if_device_connected()


    def test_02_calm_the_screen(self):

        sysop.screen_stay_on()


    def test_03_train_get_version(self):

        global old_version_info
        old_version_info = tc.get_train_version()


    def test_04_train_get_module_list(self):

        global old_module_info
        old_module_info = tc.get_module_list()


    def test_05_train_sideload_modules(self):

        apks_list = os.listdir(module_apks_path)
        print("\nmodules that will be sideloaded:\n")
        print(apks_list)
        # to generate the command string that feed to the bundletool
        bundle_apks_string = ''
        for x in apks_list:
            bundle_apks_string = bundle_apks_string + module_apks_path + x + ','
        # remove the last ','
        bundle_apks_string = bundle_apks_string[:len(bundle_apks_string) - 1]
        # print(bundle_apks_string)
        install_cmd = 'java -jar ' + bundletool + ' install-multi-apks --apks ' + bundle_apks_string
        # os.system(install_cmd)
        # use split() to perfectly prepare the command format (a list) to subprocess
        proc = subprocess.Popen(install_cmd.split(), stdout=subprocess.PIPE, universal_newlines=True)
        (output, err) = proc.communicate()

        while True:
            sleep(1)
            # poll() function to check the return code of the process. It will return None while the process is still running.
            return_code = proc.poll()
            if return_code is not None:
                # Process has finished
                sleep(3) # time buffer
                break

        # sleep(66)
        os.system('adb reboot')
        sysop.detect_if_device_connected()

        sleep(6) # time buffer

        new_version_info = tc.get_train_version()
        print("\nold version info:\n")
        print(old_version_info)
        self.assertTrue(int(new_version_info['versionCode']) > int(old_version_info['versionCode']))
        self.assertTrue(int(new_version_info['minSdk']) >= int(old_version_info['minSdk']))
        self.assertTrue(int(new_version_info['targetSdk']) >= int(old_version_info['targetSdk']))

        # covert like '2022-01-01' into python standard date format.
        old_date = time.strptime(old_version_info['versionName'], '%Y-%m-%d')
        new_date = time.strptime(new_version_info['versionName'], '%Y-%m-%d')
        self.assertTrue(new_date > old_date)
        print("\nold modules:\n" + str(old_module_info))
        new_module_info = tc.get_module_list()
        difference_set = set(new_module_info) - set(old_module_info)
        # if the new set is greater than the old one, iow, the combined set has content
        self.assertTrue(difference_set, "sideloading modules update probably failed, module packages not updated.")
        print("\nnew added modules:\n " + str(difference_set))





class TestDemo3(unittest.TestCase):

    def test_fail(self):
        self.assertEqual(3, 4)


if __name__ == '__main__':
    # globals()[sys.argv[1]](sys.argv[2], (sys.argv[3]))
    # globals()[sys.argv[1]]()
    # suite = unittest.makeSuite(ManualUpdateTestCase, 'test')
    # suite.addTest(unittest.makeSuite(SideloadModulesTestCase))
    suite = unittest.makeSuite(SideloadModulesTestCase, 'test')
    # suite = unittest.TestSuite()
    # suite.addTest(ManualUpdateTestCase("test_05_play_signin"))
    # suite.addTest(ManualUpdateTestCase("test_06_play_check_version"))
    # suite.addTest(ManualUpdateTestCase("test_07_train_get_version"))
    # suite.addTest(ManualUpdateTestCase("test_08_train_get_module_list"))
    # suite.addTest(ManualUpdateTestCase("test_10_train_trigger_update"))
    # suite.addTest(ManualUpdateTestCase("test_11_train_verify_version"))
    # suite.addTest(ManualUpdateTestCase("test_12_train_verify_module_list"))
    # suite.addTest(SideloadModulesTestCase("test_05_train_sideload_modules"))
    # # suite.addTest(TestDemo3("test_fail"))

    # with(open('test/result.html', 'wb')) as fp:
    #     runner = HTMLTestRunner(
    #         stream=fp,
    #         title='Mainline Update Test Report',
    #         description='Try, no give up.'
    #     )
    #     runner.run(suite)

    runner = unittest.TextTestRunner()
    runner.run(suite)