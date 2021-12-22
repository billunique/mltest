# coding: utf-8
#
import uiautomator2 as u2
import logging

d = u2.connect()

def play_login(test_account, pswd):

	logging.info("Go to Home screen and open Google Play.")
	d.press("home")
	d(text="Play Store").click()
	d(resourceId="com.android.vending:id/0_resource_name_obfuscated", text="Sign in").click()
	d.wait_activity(".auth.uiflows.minutemaid.MinuteMaidActivity", timeout=30)
	d(resourceId="identifierId").click()
	# d.send_keys(test_account)
	d.send_keys(test_account, clear=True)
	d(text="Next").click()
	d.send_keys(pswd, clear=True)
	d(text="Next").click()
	# agree the TOS
	d(text="I agree").click()
	d.wait_activity(".setupservices.GoogleServicesActivity", timeout=30)
	d(text="More").click()
	d(text="Accept").click()
	d.wait_activity(".AssetBrowserActivity", timeout=30)



if __name__ == '__main__':

	play_login("wx.test1", "G00gl3test")