# pageobjects/pim_page.py
from __future__ import annotations
from typing import Optional

from selenium.common import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pageobjects.base_page import BasePage, Locator


class PIMPage(BasePage):
    # --- robust, label-based locators where possible ---
    _add_new_emp: Locator = (By.XPATH, "//button[normalize-space() = 'Add']")
    _first_name: Locator = (By.XPATH, "//input[@placeholder='First Name']")
    _middle_name: Locator = (By.XPATH, "//input[@placeholder='Middle Name']")
    _last_name: Locator = (By.XPATH, "//input[@placeholder='Last Name']")
    # Add Employee form's emp id (may be auto-generated) - use label-based locator
    _empid: Locator = (By.XPATH, "//label[normalize-space()='Employee Id']/following::input[1]")

    _create_login_details_btn: Locator = (By.XPATH, "//div//p[normalize-space()='Create Login Details']/following::label[1]")
    _username_txt: Locator = (By.XPATH, "//label[normalize-space()='Username']/following::input[1]")
    _password_txt: Locator = (By.XPATH, "//label[normalize-space()='Password']/following::input[@type='password'][1]")
    _cnf_password_txt: Locator = (By.XPATH, "//label[normalize-space()='Confirm Password']/following::input[@type='password'][1]")
    _save_details: Locator = (By.XPATH, "//button[normalize-space()='Save']")

    # Employee list/search locators
    _emp_list_menu: Locator = (By.XPATH, "//a[normalize-space()='Employee List']")
    _emp_info_empname: Locator = (By.XPATH, "//label[normalize-space()='Employee Name']/following::input[1]")
    _emp_info_empid: Locator = (By.XPATH, "//label[normalize-space()='Employee Id']/following::input[1]")
    _emp_info_search_button: Locator = (By.XPATH, "//button[normalize-space()='Search']")
    _emp_record_found: Locator = (By.XPATH, "//span[normalize-space()='(1) Record Found']")

    # Toast
    _toast: Locator = (By.XPATH, "//div[contains(@class,'oxd-toaster') or @id='oxd-toaster_1' or contains(., 'Successfully')]")
    #delete employee records
    _delete_employee_record:Locator=(By.XPATH,"//span[contains(@class,'oxd-text--span') and contains(normalize-space(.),'Records')]/following::i[2]")
    _confirm_delete_employee_popup:Locator=(By.XPATH,"//button[normalize-space()='Yes, Delete']")
    _delete_toast_container_btn:Locator=(By.XPATH,"//div[@id='oxd-toaster_1']")
    #--------PIM--------
    _pim_option_btn:Locator=(By.XPATH,"//a[@class='oxd-main-menu-item active']")
    # -------- actions --------
    def add_new_employee(self) -> None:
        self.click(self._add_new_emp)

    def enter_f_name(self, f_name: str) -> None:
        self.type(self._first_name, f_name)

    def enter_middle_name(self, m_name: str) -> None:
        self.type(self._middle_name, m_name)

    def enter_l_name(self, l_name: str) -> None:
        self.type(self._last_name, l_name)

    def enter_emp_id(self, empid: str) -> str:
        """
        Type the requested empid using BasePage.type() and return the actual UI value via element_value().
        This is minimal: we do not copy wait logic here — BasePage handles waits via find_visible/find_clickable.
        """
        self.type(self._empid, empid)
        return self.element_value(self._empid)

    def get_emp_id_value(self) -> str:
        return self.element_value(self._empid)

    def create_login_details_toggle(self) -> None:
        self.click(self._create_login_details_btn)

    def enter_username(self, username: str):
        self.type(self._username_txt, username)

    def enter_password(self, password: str):
        self.type(self._password_txt, password)

    def enter_cnf_password(self, cnf_password: str):
        self.type(self._cnf_password_txt, cnf_password)

    def save_details(self):
        self.click(self._save_details)

    # -------- verification / search helpers --------
    def wait_for_toast(self, timeout: int = None) -> Optional[str]:
        # delegate to BasePage.get_text/find_visible behavior
        try:
            txt = self.get_text(self._toast, timeout=timeout)
            return txt
        except Exception:
            return None

    def go_to_employee_list(self) -> None:
        self.click(self._emp_list_menu)

    def search_by_employee_id(self, id):
        self.type(self._emp_info_empid,id, clear_first=True)
        self.click(self._emp_info_search_button)

    def confirm_record_found(self):
        confirmation_text=self.get_text(self._emp_record_found)
        return confirmation_text

    def click_pim_btn(self):
        self.click(self._pim_option_btn)

    def click_delete_btn(self):
        self.click(self._delete_employee_record)
    def cnf_click_delete_toast(self):
        self.click(self._confirm_delete_employee_popup)

    def get_taost_confirmation_of_delete(self):
        self.is_visible(self._delete_toast_container_btn)

