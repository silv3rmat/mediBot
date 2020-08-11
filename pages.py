from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

from doctor_data import DOC_IDS, SPEC_IDS

class BasePage:
    BASE_URL = "https://mol.medicover.pl/"

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
        self.url = self.BASE_URL

    def get_page(self):
        self.driver.get(self.url)
        return self


class LoggedOutPage(BasePage):

    def __init__(self, driver):
        super().__init__(driver)
        self.url = BasePage.BASE_URL

        self.login_button_locator = (By.ID, "oidc-submit")

    def click_login(self):
        self.wait.until(EC.element_to_be_clickable(self.login_button_locator))
        self.driver.find_element(*self.login_button_locator).click()


class LoginPage(BasePage):

    def __init__(self, driver):
        super().__init__(driver)
        self.url = BasePage.BASE_URL

        self.card_number_locator = (By.ID, "UserName")
        self.password_locator = (By.ID, "Password")
        self.login_button_locator = (By.ID, "loginBtn")

    def enter_username(self, card_number):
        self.wait.until(EC.presence_of_element_located(self.card_number_locator))
        self.driver.find_element(*self.card_number_locator).send_keys(card_number)

    def enter_password(self, password):
        self.wait.until(EC.presence_of_element_located(self.password_locator))
        self.driver.find_element(*self.password_locator).send_keys(password)

    def click_login(self):
        self.wait.until(EC.element_to_be_clickable(self.login_button_locator))
        self.driver.find_element(*self.login_button_locator).click()

    def login(self, card_number, password):
        self.enter_username(card_number)
        self.enter_password(password)
        self.click_login()


class AppointmentManagerPage(BasePage):

    def __init__(self, driver):
        super().__init__(driver)

        self.url = BasePage.BASE_URL + "MyVisits/AppointmentsManager"
        self.zrealizowane_locator = (By.XPATH, "//*[text()='Zrealizowane']")
        self.appointment_locator = (By.CSS_SELECTOR, 'div.appointment-item')

        self.specialty_locator = (By.CSS_SELECTOR, 'div.specialty')
        self.doctor_locator = (By.CSS_SELECTOR, 'div.doctor')
        self.date_locator = (By.CSS_SELECTOR, 'div.date')
        self.hour_locator = (By.CSS_SELECTOR, 'div.time')

    def get_appointments(self, searched_specialty):
        self.wait.until(EC.presence_of_element_located(self.zrealizowane_locator))
        appointments = []
        appointment_elements = self.driver.find_elements(*self.appointment_locator)
        for row in appointment_elements:
            specialty = row.find_element(*self.specialty_locator).text.strip()
            doctor = row.find_element(*self.doctor_locator).text.strip()
            date = row.find_element(*self.date_locator).text.strip()
            hour = row.find_element(*self.hour_locator).text.strip()
            visit_datetime = datetime(*[int(item) for item in reversed(date.split('-'))], *[int(item) for item in hour.split(':')])

            if visit_datetime > datetime.now() and searched_specialty == specialty:
                appointments.append(
                    {
                        'date': date,
                        'hour': hour,
                        'specialty': specialty,
                        'doctor': doctor,
                        'visit_datetime':visit_datetime
                    }
                )
        return appointments


class SearchVisitPage(BasePage):

    def __init__(self, driver, doctor, specialty, region, start_hour, end_hour):
        super().__init__(driver)
        self.doctor = doctor
        self.specialty = specialty
        self.region = region
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.url = "https://mol.medicover.pl/MyVisits?bookingTypeId=2&mex=True&pfm=1"
        self.search_button_locator = (By.XPATH, "//button[text()='Szukaj']")
        self.refresh_button_locator = (By.ID, 'btn-session-refresh')

    def set_parameters(self):
        if self.doctor:
            doc_id = '&doctorId=' + str(DOC_IDS[self.doctor])
        search_since = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:02.156Z')
        self.driver.get(f"https://mol.medicover.pl/MyVisits?"
                        f"regionId={self.region}&"
                        f"bookingTypeId=2&"
                        f"specializationId={SPEC_IDS[self.specialty]}&"
                        f"languageId=-1"
                        f"{doc_id}&"
                        f"searchSince={search_since}&"
                        f"startTime={self.start_hour}&"
                        f"endTime={self.end_hour}"
                        )
        return self

    def click_refresh(self):
        self.wait.until(EC.presence_of_element_located(self.refresh_button_locator))
        self.driver.find_element(*self.refresh_button_locator).click()

    def click_search(self):
        self.wait.until(EC.element_to_be_clickable(self.search_button_locator))
        self.driver.find_element(*self.search_button_locator).click()

    def search(self):
        try:
            self.click_search()
        except (TimeoutException,ElementClickInterceptedException):
            try:
                self.click_refresh()
            except TimeoutException:
                self.set_parameters()


