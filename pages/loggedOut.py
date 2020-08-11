from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


from .base import BasePage


class LoggedOutPage(BasePage):

    def __init__(self, driver):
        super().__init__(driver)
        self.url = BasePage.BASE_URL

        self.login_button_locator = (By.ID, "oidc-submit")

    def click_login(self):
        self.click(self.login_button_locator)
