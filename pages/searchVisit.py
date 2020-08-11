from .base import BasePage

from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

from doctor_data import DOC_IDS, SPEC_IDS


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


