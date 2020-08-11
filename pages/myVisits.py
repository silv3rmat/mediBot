from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .base import BasePage


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
