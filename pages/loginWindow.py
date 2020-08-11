from .base import BasePage

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class LoginPage(BasePage):

    def __init__(self, driver):
        super().__init__(driver)
        self.url = BasePage.BASE_URL

        self.card_number_locator = (By.ID, "UserName")
        self.password_locator = (By.ID, "Password")
        self.login_button_locator = (By.ID, "loginBtn")
        self.page_locator = (By.ID, "loginBtn")

    def login(self, card_number, password):
        self.enter_text(card_number, self.card_number_locator)
        self.enter_text(password, self.password_locator)
        self.click(self.login_button_locator)
