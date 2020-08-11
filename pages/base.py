from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class BasePage:
    BASE_URL = "https://mol.medicover.pl/"

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
        self.url = self.BASE_URL
        self.page_locator = (By.CSS_SELECTOR, 'html')

    def ensure_loaded(self, locator ='', ec=EC.presence_of_element_located):
        locator = locator or self.page_locator
        self.wait.until(ec(locator))

    def get_page(self):
        self.driver.get(self.url)
        self.ensure_loaded()
        return self

    def click(self, locator):
        self.ensure_loaded()
        self.wait.until(EC.element_to_be_clickable(locator))
        self.driver.find_element(*locator).click()

    def enter_text(self, text, locator):
        self.ensure_loaded()
        self.wait.until(EC.presence_of_element_located(locator))
        self.driver.find_element(*locator).send_keys(text)
