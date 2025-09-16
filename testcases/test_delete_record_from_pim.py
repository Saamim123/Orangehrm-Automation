import pytest
from utilities.customlogger import CustomLogger
from pageobjects.pim_page import PIMPage
from pageobjects.user_dashboard_page import UserDashboardPage

class Test_delete_PIM_record:
    logger=CustomLogger().get_logger()

    def test_delete_record_from_PIM(self,driver,login_fixture):
        self.logger.info("-------Starting deleting PM record Test----------")
        userdashboardpage=UserDashboardPage(driver)
        userdashboardpage.click_pim_btn()
        pimpage=PIMPage(driver)

        pimpage.click_delete_btn()
        self.logger.info("-------confirming delete toast message----------")
        #assert pimpage.get_taost_confirmation_of_delete()



