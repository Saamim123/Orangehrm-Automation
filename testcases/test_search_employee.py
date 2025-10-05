import time

import pytest
from utilities.customlogger import CustomLogger
from pageobjects.pim_page import PIMPage
from pageobjects.user_dashboard_page import UserDashboardPage
from utilities.readproperties import ReadConfig


class Test_search_employee:
    logger=CustomLogger().get_logger()
    empname=ReadConfig.pim_emp_name()
    name=ReadConfig.select_emp_name()
    def test_search_employee(self,driver,login_fixture):
        self.logger.info("-------Starting search employee record Test----------")
        userdashboardpage=UserDashboardPage(driver)
        userdashboardpage.click_pim_btn()
        pimpage=PIMPage(driver)
        pimpage.type_emp_name(self.empname)
        time.sleep(7)
        pimpage.click_desired_employee_name(self.name)
        pimpage.click_search()

        first_name=pimpage.capture_found_f_emp_name()
        last_name = pimpage.capture_found_f_emp_name()

        assert first_name == "Sania", f"Expected first name 'Sania' but got '{first_name}'"
        #assert last_name == "Shaheen", f"Expected last name 'Shaheen' but got '{last_name}'"
