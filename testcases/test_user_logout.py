import pytest
from utilities.customlogger import CustomLogger
from pageobjects.user_dashboard_page import UserDashboardPage
from pageobjects.user_login import UserLoginPage


class Test_user_logout:
    logger=CustomLogger().get_logger()


    def test_user_logout(self,driver,login_fixture):
        self.logger.info("-------Starting User Logout Test----------")

        udp=UserDashboardPage(driver)
        udp.click_profile_drpdown()
        self.logger.info("Clicking logout button")
        udp.click_logout_btn()
        ulp=UserLoginPage(driver)
        assert ulp.is_logo_present()
        self.logger.info("Logout successful, login page logo is visible.")



