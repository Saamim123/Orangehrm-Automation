import pytest

from pageobjects.user_login import UserLoginPage
from pageobjects.user_dashboard_page import UserDashboardPage
from testcases.conftest import driver
from utilities.readproperties import ReadConfig
from utilities.customlogger import CustomLogger


@pytest.mark.usefixtures("driver")
class Test_user_login:

    user_login_url=ReadConfig.get_user_login_url()
    username=ReadConfig.get_user_email()
    password=ReadConfig.get_user_password()
    logger=CustomLogger().get_logger()
    #driver=None


    def test_userLogin(self,driver):
        self.logger.info("-------Starting User Login Test----------")
        self.logger.info(f"Opening URL: {self.user_login_url}")
        ulp = UserLoginPage(driver)
        ulp.get_user_login_url(self.user_login_url)
        ulp.enter_username(self.username)
        self.logger.info("------- Entering password ----------")
        ulp.enter_password(self.password)
        self.logger.info("Clicking login button")
        ulp.click_login()

        udp = UserDashboardPage(driver)
        actual_text = udp.capture_text()
        assert actual_text == "Dashboard", f"Expected 'Dashboard' but got '{actual_text}'"













