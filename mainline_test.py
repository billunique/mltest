# coding: utf-8
#

import subprocess
import os
import sys
import time
from time import sleep
import datetime
import unittest

import uiautomator2 as u2
# from uiautomator2 import UiObjectNotFoundError
import system_common as sysc
from utils import print_whereami_head, print_whereami_tail, whereami_logger


TEST_ACCOUNT='wx.test1'
PASSWORD='G00gl3test'

d = u2.connect()

def open_google_play():

    os.system("adb shell am start -n com.android.vending/.AssetBrowserActivity")


def force_stop_play():

    # d.press("home")
    # d(text="Play Store").long_click()
    # d(description="App info").click()
    # # Force stop button
    # d(resourceId="com.android.settings:id/button3").click()
    # # OK button
    # d(resourceId="android:id/button1").click()

    os.system("adb shell am force-stop com.android.vending")


def open_play_account_menu():

    try:
        # open_google_play_by_icon()
        open_google_play()
        sleep(1)
        # account menu already opened.
        if d(text="Library").wait(timeout=2.0):
            pass
        # click the account avatar by coordinate, no better ways.
        else:
            d.click(0.89, 0.072)
            # for older version Google Play
            if not d(text="Settings").exists(timeout=2.0):
                d.press("back")
                d.xpath('//*[@content-desc="Show navigation drawer"]/android.widget.ImageView[1]').click()  # open menu by clicking the left corner image button.

    except u2.UiObjectNotFoundError:
        # exit all activity to return to home screen.
        for i in range(1, 6):
            d.press("back")

        open_play_account_menu()


def is_play_latest():

    attempts = 3
    for i in range(attempts):
        try:
            open_play_account_menu()
            d(text="Settings").click()
            time.sleep(2)
            if d(scrollable=True):
                d(scrollable=True).fling.toEnd()
            d(text="About").click()
            if d(scrollable=True):
                d(scrollable=True).fling.toEnd()
            d(text="Play Store version").click()
            if d(textContains="A new version").wait(timeout=3.0):
                print('\nPlay store need to be updated.')
                d.screenshot("test_data/play_store_need_update.png")
                uptodate = False
            else:
                print("\nPlay store is already up-to-date.")
                d.screenshot("test_data/play_store_latest.png")
                uptodate = True
            if d(text="Got it").exists():
                d(text="Got it").click()
            else:
                d(text="OK").click()
            return uptodate

        except u2.UiObjectNotFoundError:
            if i < attempts -1: # i steps from 0
                continue
            else:
                raise
        break


def check_play_update_menu_shown(timeout=90):
    try:
        latest = is_play_latest()
    except u2.UiObjectNotFoundError:
        play_login(TEST_ACCOUNT, PASSWORD)

    if not latest:
        timeout = timeout
        deadline = time.time() + timeout
        while time.time() < deadline:
        # for i in range(10):
            # sleep(2)
            print("\nwait the update of Google Play to complete...")
            sysc.to_Settings_Security()
            # check if the Google Play system update item has shown, thus the test can go next.
            if d(text="Google Play system update").exists(timeout=2.0):
                print("Google Play system update menu has shown.")
                sleep(1)
                # break
                return True
            else:
                sysc.stop_Settings_activity()
                sleep(5)
                continue
    else:
        print("\nIt has been the lastest Google Play.")
        sysc.to_Settings_Security()
        return d(text="Google Play system update").exists(timeout=2.0)




def trigger_module_update():

    os.system("adb shell am start -a android.settings.MODULE_UPDATE_SETTINGS")
    # os.system("adb shell am start -n com.android.vending/com.google.android.finsky.systemupdateactivity.SystemUpdateActivity")


def trigger_instant_hygiene():

    os.system("adb shell am start-foreground-service -n com.android.vending/com.google.android.finsky.shellservice.ProdShellService --es command trigger_instant_hygiene")


def trigger_instant_self_update():

    os.system("adb shell am start-foreground-service -n com.android.vending/com.google.android.finsky.shellservice.ProdShellService --es command trigger_instant_self_update")




def play_login(account_name, pswd):

    attempts = 3
    for i in range(attempts):
        try:
            open_google_play()
            sleep(3)
            # d(resourceId="com.android.vending:id/0_resource_name_obfuscated", text="Sign in").click()
            # "SIGN IN" case fits for some old version Google Play.
            for text in ["Sign in", "SIGN IN"]:
                try:
                    d(text=text).click()
                except u2.UiObjectNotFoundError:
                    pass
                    continue
            sleep(3)
            if d(text="Couldn't sign in").exists(timeout=2.0): # Wifi's not ready in this case.
                continue
            minutemaid_login(account_name, pswd)

        except u2.UiObjectNotFoundError:
            if i < attempts -1: # i steps from 0
                continue
            else:
                raise
        break
    if d.wait_activity(".AssetBrowserActivity", timeout=20):
        print("Play login with " + account_name + " successfully!")


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
        sleep(2)
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
            os.system("adb shell am start -a android.settings.ADD_ACCOUNT_SETTINGS")
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
    #   if d.wait_activity(".setupservices.GoogleServicesActivity", timeout=30):
    #       d(text="More").click()
    #       d(text="Accept").click()

    stop_Settings_activity()


def remove_google_account(account_name):

    # open Passwords & accounts
    to_Settings_PaA()
    # d(scrollable=True).fling()
    d(textContains=account_name).click()
    d(text="Remove account").click()
    # confirm
    d(resourceId="android:id/button1").click()
    stop_Settings_activity()


def test_add_remove_account():

    PASSWORD = "G00gl3test"
    add_google_account("wx.test2", PASSWORD)
    add_google_account("wx.test1", PASSWORD)
    add_google_account("wx.test3", PASSWORD)
    # remove_google_account("wx.test1")


def test_remove_all_google_accounts():

    to_Settings_PaA()
    sleep(2)
    while d(textContains='gmail.com'):
        d(textContains='gmail.com').click()
        d(text="Remove account").click()
        # confirm
        d(resourceId="android:id/button1").click()
        stop_Settings_activity()
        os.system("adb shell am start -a android.settings.SYNC_SETTINGS")
        sleep(2)
        continue
    else:
        stop_Settings_activity()


def open_traineng():
    os.system("adb shell am start -n com.google.android.trainengineer/.TrainEngineer")


def _install_traineng_and_capture():

    apk_dir = './archive/trainengineer.apk'
    if apk_dir:
        sysc.install_apk(apk_dir)
        time.sleep(3)
        open_traineng()
        time.sleep(2)
        time_format = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S.%f")
        d.screenshot('./test_data/traineng1_' + time_format + '.png')
        d(scrollable=True).fling.toEnd()
        d.screenshot('./test_data/traineng2_' + time_format + '.png')



class MainlineTestCase(unittest.TestCase):
    """ Base test case class of all mainline test cases. 

    Data Examples:
    version_info={'versionCode': '310000000', 'minSdk': '29', 'targetSdk': '31', 'versionName': '2021-09-01'}
    module_info=['com.google.android.ext.services', 'com.google.android.permissioncontroller']
    module_and_version={'com.google.android.ext.services': '310727000', 'com.google.android.permissioncontroller': '310733000', 'com.google.android.captiveportallogin': '310727000', 'com.google.android.modulemetadata': '310005800'}
    """

    # def __init__(self, *args, **kwargs):

    #     super(MainlineTestCase, self).__init__(*args, **kwargs)
        
    maxDiff=None

    def get_train_version(self) -> dict:

        print_whereami_head(self)

        #only take the first 2 matches for parsing and comparing.
        version_info = os.popen("adb shell dumpsys package com.google.android.modulemetadata | grep -m 2 -E 'versionName|versionCode'").read()
        print("\nraw version info:\n")
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
        print_whereami_tail(self)
        return dict_version_info


    def get_module_list(self) -> list:
        """ 
        sample returned: 
        ['com.google.android.ext.services', 'com.google.android.permissioncontroller', 'com.google.android.captiveportallogin', 'com.google.android.modulemetadata', 'com.google.android.networkstack']
        """

        print_whereami_head(self)
        module_info = os.popen("adb shell pm get-moduleinfo").read()
        list_module_pkg = []
        for i in module_info.splitlines():
            list_module_pkg.append(i.split(":")[1].strip())

        # listl = [x.split(":")[1].strip() for x in module_info.splitlines()]
        
        print("\nlist current modules in package names:\n")
        print(list_module_pkg, "\n")
        print("\nraw current moudules info:\n")
        print(module_info, "\n")
        print_whereami_tail(self)
        return list_module_pkg


    def get_train_module_and_version(self) -> dict:

        print_whereami_head(self)
        list_module = self.get_module_list()
        output1 = os.popen("adb shell cmd package list packages --show-versioncode").readlines()
        output2 = os.popen("adb shell cmd package list packages --show-versioncode --apex-only").readlines()
        output_list = output1 + output2
        matched_line = []
        for l in list_module:
            for line in output_list:
                if l in line:
                    matched_line.append(line.strip())
        print("\ndetailed train modules with their versionCode:\n")
        for _ in matched_line:
            print(_)

        print("\ndetailed train modules with their versionCode in pure mode:\n")

        matched_line_lite = [(x.split(":")[1].replace(" versionCode", "") + ":" + x.split(":")[2]) for x in matched_line]
        for _ in matched_line_lite:
            print(_)
        dict_module_and_versioncode = dict(pair.split(":") for pair in matched_line_lite)
        print("\nreturn a dict including the modules info:\n")
        print(dict_module_and_versioncode)
        print_whereami_tail(self)
        return dict_module_and_versioncode


    def sideload_modules(self, bundletool_path, module_apks_path):

        apks_list = os.listdir(module_apks_path)
        print("\nmodules that will be sideloaded:\n")
        print(apks_list, "\n")
        # to generate the command string that feed to the bundletool
        bundle_apks_string = ''
        for x in apks_list:
            bundle_apks_string = bundle_apks_string + module_apks_path + x + ','
        # remove the last ','
        bundle_apks_string = bundle_apks_string[:len(bundle_apks_string) - 1]
        # print(bundle_apks_string)
        install_cmd = 'java -jar ' + bundletool_path + ' install-multi-apks --enable-rollback --apks ' + bundle_apks_string
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
        sysc.device_waitor(40)



if __name__ == '__main__':

    # globals()[sys.argv[1]]()
    _install_traineng_and_capture()
    
    # is_play_latest()
    # play_login(TEST_ACCOUNT, PASSWORD)
    # c1 = MainlineTestCase()
    # c1.get_train_version()
    # c1.get_module_list()
    # c1.get_train_module_and_version()
    # c1.sideload_modules('bundletool-all-1.8.2.jar', 'S_modules/')

