# coding: utf-8
#

import uiautomator2 as u2
import uiautomator2.ext.htmlreport as htmlreport


d = u2.connect()
hrp = htmlreport.HTMLReport(d)

# take screenshot before each click
hrp.patch_click()

d.unlock()
d.press("home")
d(scrollable=True).scroll.toEnd()
d(scrollable=True).scroll.to(text="Settings")
d(text="Settings").click()
