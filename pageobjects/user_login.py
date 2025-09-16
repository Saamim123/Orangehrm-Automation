from selenium.webdriver.common.by import By

from pageobjects.base_page import BasePage
from utilities.readproperties import ReadConfig




class UserLoginPage(BasePage):

    txtbox_username_xpath=(By.XPATH,"//input[@name='username']")
    password_xpath=(By.XPATH,"//input[@placeholder='Password']")
    btn_login_xpath=(By.XPATH,"//button[normalize-space()= 'Login']")
    company_logo=(By.XPATH,"//img[@alt='company-branding']")



    def get_user_login_url(self,url: str):
        self.open_url(url)

    def enter_username(self,username: str):
        self.type(self.txtbox_username_xpath,username)

    def enter_password(self,password: str):
        self.type(self.password_xpath,password)

    def click_login(self):
        self.click(self.btn_login_xpath)

    def is_logo_present(self):
        logo=self.find_visible(self.company_logo)
        return logo




        






