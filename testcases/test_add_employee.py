# tests/test_add_employee.py
import pytest
from utilities.customlogger import CustomLogger
from pageobjects.pim_page import PIMPage
from pageobjects.user_dashboard_page import UserDashboardPage

class Test_add_employee:
    logger = CustomLogger().get_logger()

    def test_add_employee(self, driver, login_fixture, employee_record):
        self.logger.info("-------Starting add employee Test----------")
        udp = UserDashboardPage(driver)
        udp.click_pim_btn()

        pim = PIMPage(driver)
        pim.add_new_employee()

        # create using fixture values
        pim.enter_f_name(employee_record["first_name"])

        pim.enter_middle_name(employee_record["middle_name"])
        pim.enter_l_name(employee_record["last_name"])

        # Try set employee id and read back the actual value
        final_empid = pim.enter_emp_id(employee_record["employee_id"])
        self.logger.info(f"Requested empid={employee_record['employee_id']} final_empid={final_empid}")

        pim.create_login_details_toggle()
        pim.enter_username(employee_record["username"])
        pim.enter_password(employee_record["password"])
        pim.enter_cnf_password(employee_record["confirm_password"])
        pim.save_details()

        # optional: verify toast shown (UX check)
        toast = pim.wait_for_toast(timeout=6)
        if toast:
            self.logger.info(f"Toast: {toast}")

        # go to Employee List and search by the actual final_empid
        pim.go_to_employee_list()
        pim.search_by_employee_id(final_empid)
        actual_text = pim.confirm_record_found()

        assert actual_text == "(1) Record Found", f"Expected '(1) Record Found' but got '{actual_text}'"
