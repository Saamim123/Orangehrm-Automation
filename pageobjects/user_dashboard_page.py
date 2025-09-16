from typing import Optional

from selenium.webdriver.common.by import By
from pageobjects.base_page import BasePage, Locator
from utilities.readproperties import ReadConfig

class UserDashboardPage(BasePage):
    _dashboard_txt: Locator = (By.XPATH, '//span//h6[normalize-space()="Dashboard"]')
    profile_drpdown=(By.XPATH,"//i[@class='oxd-icon bi-caret-down-fill oxd-userdropdown-icon']")
    logout_btn=(By.XPATH,"//a[@class='oxd-userdropdown-link' and contains(text(),'Logout')]")
    pim_btn=(By.XPATH,"//a[normalize-space()='PIM']")


    def capture_text(self):
        return self.get_text(self._dashboard_txt).strip()

    def is_dashboard_loaded(self):
        expected = "Dashboard"
        self.wait_for_text(self._dashboard_txt,expected)

    def click_profile_drpdown(self):
        self.click(self.profile_drpdown)

    def click_logout_btn(self):
        self.click(self.logout_btn)

    def click_pim_btn(self):
        self.click(self.pim_btn)



