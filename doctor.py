from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    ElementNotInteractableException
)
from time import sleep
import random
import traceback
import datetime
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from datetime import datetime, timedelta
from urllib3.exceptions import NewConnectionError, MaxRetryError
import sys
from sms import send_sms
from medi_creds import *
from preferences import PreferenceParser, HourPreference, HourTarget, DatePreference, DateTarget
from pages import LoggedOutPage, LoginPage, AppointmentManagerPage, SearchVisitPage


from doctor_data import DOC_IDS, SPEC_IDS

class Medicover:
    def __init__(self, card_no, password, pref_parser: PreferenceParser):
        self.card_no = card_no
        self.password = password
        self.driver = webdriver.Chrome('./chromedriver')
        self.driver.get("https://mol.medicover.pl")
        self.main_window = self.driver.current_window_handle
        self.pref_parser = pref_parser

    def close_browser(self):
        self.driver.quit()

    def logged(self):
        self.driver.switch_to.window(self.main_window)
        return len(self.driver.find_elements_by_id("logoff")) == 1

    def login(self):
        if not self.logged():
            start_page = LoggedOutPage(self.driver).get_page()
            start_page.click_login()
            login_window = LoginPage(self.driver)
            login_window_handle = list(set(self.driver.window_handles) - {self.main_window})[0]
            self.driver.switch_to.window(login_window_handle)
            login_window.login(self.card_no, self.password)

    def find_current_visits(self, searched_specialty):
        appo_page = AppointmentManagerPage(self.driver).get_page()
        appointments = appo_page.get_appointments(searched_specialty)

        for appointment in appointments:
            appointment['distance'] = self.pref_parser.compile_distance(appointment)

        return appointments

    def find_doc(self, region, specialty, doctor, start_hour, end_hour):
        if self.logged():
            current_visits = self.find_current_visits(specialty)
            print(current_visits)
            for visit in current_visits:
                print(self.pref_parser.compile_distance(visit))
            search_page = SearchVisitPage(
                self.driver,
                doctor=doctor,
                specialty=specialty,
                region=region,
                start_hour=start_hour,
                end_hour=end_hour).set_parameters()
            while True:
                sleep(5+20*random.random())
                search_page.search()

                print("Checking " + datetime.now().strftime('%H:%M'))
                if "zostały już zarezerwowane przez innych pacjentów." not in self.driver.page_source:
                    while True:
                        try:
                            self.driver.find_element_by_xpath("//button[text()='Pokaż więcej ...']").click()
                            sleep(7)
                        except NoSuchElementException:
                            break
                        except ElementClickInterceptedException:
                            self.driver.find_element_by_id('btn-session-refresh').click()
                    free_slots = []
                    attribute = self.driver.find_element_by_css_selector("app-root").get_property('attributes')[0]['name'].split('-')[1]
                    appointment_dates = self.driver.find_elements_by_css_selector(f"app-visit-list div[_ngcontent-{attribute}-c3]")
                    for appo_date in appointment_dates:
                        try:
                            day_date = appo_date.find_element_by_css_selector("h3.visitListDate").text
                            print(day_date)
                            for slot in appo_date.find_elements_by_css_selector('div.freeSlot'):
                                hour = slot.find_element_by_css_selector('div.slot-time').text
                                specialty = slot.find_element_by_css_selector('div.specialization').text
                                doctor = slot.find_element_by_css_selector('div.doctorName').text
                                appointment = {
                                    'date': polish_date_to_datetime(day_date),
                                    'hour': hour,
                                    'element': slot,
                                    'specialty': specialty,
                                    'doctor': doctor
                                }
                                appointment['distance'] = self.pref_parser.compile_distance(appointment)
                                if appointment['distance']<1:
                                    free_slots.append(appointment)
                            print(free_slots)
                            print([self.pref_parser.compile_distance(slot) for slot in free_slots])
                        except NoSuchElementException:
                            if len(free_slots)==0:
                                continue
                            minimal_distance_appointment = min(free_slots, key=lambda x: x['distance'])
                            if len(current_visits) ==0 :
                                maximum_distance_current_visit=1000
                            else:
                                maximum_distance_current_visit = max(current_visits, key=lambda x: x['distance'])
                            if minimal_distance_appointment['distance'] < maximum_distance_current_visit['distance'] or len(current_visits)<2:
                                if len(current_visits) == 0:
                                    minimal_distance_appointment['element'].find_element_by_xpath("//button[text()=' Umów ']").click()
                                    wait = WebDriverWait(self.driver, 15)
                                    wait.until(
                                        ec.visibility_of_element_located((By.XPATH, "//*[text()='Potwierdź wizytę']")))
                                    apo_time = self.driver.find_element_by_css_selector("div.visit-date").text
                                    specialization = self.driver.find_element_by_id('FormModel_SpecializationName').get_attribute('value')
                                    doc_name = self.driver.find_element_by_id('FormModel_DoctorName').get_attribute('value')
                                    clinic = self.driver.find_element_by_id('FormModel_ClinicPublicName').get_attribute('value')
                                    self.driver.find_element_by_id("bookAppointmentButton").click()
                                    print(apo_time)
                                    print(specialization)
                                    print(doc_name)

                                    print(clinic)
                                    send_sms(f'{apo_time} {specialization} {doc_name} {clinic}')
                                    return
                                if len(current_visits) == 1:
                                    minimal_distance_appointment['element'].find_element_by_xpath(
                                        "//button[text()=' Umów ']").click()
                                    wait = WebDriverWait(self.driver, 15)
                                    wait.until(
                                        ec.visibility_of_element_located((By.XPATH, "//*[text()='Umów nową wizytę lub zmień termin']")))
                                    self.driver.find_element_by_xpath("//*[text()='Umów nową wizytę']").click()
                                    wait = WebDriverWait(self.driver, 15)
                                    wait.until(
                                        ec.visibility_of_element_located((By.XPATH, "//*[text()='Potwierdź wizytę']")))
                                    apo_time = self.driver.find_element_by_css_selector("div.visit-date").text
                                    specialization = self.driver.find_element_by_id(
                                        'FormModel_SpecializationName').get_attribute('value')
                                    doc_name = self.driver.find_element_by_id('FormModel_DoctorName').get_attribute(
                                        'value')
                                    clinic = self.driver.find_element_by_id('FormModel_ClinicPublicName').get_attribute(
                                        'value')
                                    self.driver.find_element_by_id("bookAppointmentButton").click()
                                    print(apo_time)
                                    print(specialization)
                                    print(doc_name)

                                    print(clinic)
                                    send_sms(f'{apo_time} {specialization} {doc_name} {clinic}')
                                    return
                                if len(current_visits)==2:
                                    minimal_distance_appointment['element'].find_element_by_xpath(
                                        "//button[text()=' Umów ']").click()
                                    wait = WebDriverWait(self.driver, 15)
                                    wait.until(
                                        ec.visibility_of_element_located(
                                            (By.XPATH, "//*[text()='Zmień termin wizyty']")))
                                    available_visits = self.driver.find_elements_by_css_selector('div.appointments.ng-scope div.row')
                                    for available_visit in available_visits:
                                        apo_date = available_visit.find_element_by_css_selector('div.date.ng-scope').text.strip().replace('/','-')
                                        apo_time = available_visit.find_element_by_css_selector('div.time.ng-binding').text.strip()
                                        apo_special = available_visit.find_element_by_css_selector('div.specialty.ng_binding').text.strip()
                                        if apo_date == maximum_distance_current_visit['date'] and apo_time == maximum_distance_current_visit['hour'] and apo_special ==maximum_distance_current_visit['specialty']:
                                            available_visit.find_element_by_css_selector('i.fa.fa-square-o').click()
                                            self.driver.find_element_by_xpath("//button[text()='Potwierdź zmianę wizyty']").click()
                                            wait = WebDriverWait(self.driver, 15)
                                            wait.until(
                                                ec.visibility_of_element_located(
                                                    (By.XPATH, "//*[text()='Potwierdź wizytę']")))
                                            apo_time = self.driver.find_element_by_css_selector("div.visit-date").text
                                            specialization = self.driver.find_element_by_id(
                                                'FormModel_SpecializationName').get_attribute('value')
                                            doc_name = self.driver.find_element_by_id(
                                                'FormModel_DoctorName').get_attribute(
                                                'value')
                                            clinic = self.driver.find_element_by_id(
                                                'FormModel_ClinicPublicName').get_attribute(
                                                'value')
                                            self.driver.find_element_by_id("bookAppointmentButton").click()
                                            print(apo_time)
                                            print(specialization)
                                            print(doc_name)

                                            print(clinic)
                                            send_sms(f'{apo_time} {specialization} {doc_name} {clinic}')
                                            return


                        except ElementClickInterceptedException:
                            self.driver.find_element_by_id('btn-session-refresh').click()

    def make_appointment(self, current_visits):
        if len(current_visits)== 0:
            pass

    def run(self, specialty, doctor=None, start_hour=0, end_hour=0, region=202):
        try:
            while True:
                if self.driver:
                    if self.logged():
                        try:
                            self.find_doc(region=region, specialty=specialty, doctor=doctor, start_hour=start_hour,
                                          end_hour=end_hour)
                        except ElementNotInteractableException:
                            self.close_browser()
                    else:
                        self.login()
                else:
                    self.driver.get('https://mol.medicover.pl')
        except (NewConnectionError, MaxRetryError):
            self.driver = webdriver.Chrome('./chromedriver')
            self.driver.get('https://mol.medicover.pl')
            self.main_window = self.driver.current_window_handle
            sleep(60)
            self.run(specialty=specialty, doctor=doctor, start_hour=start_hour, end_hour=end_hour, region=region)
            print("New connection error.")
        except:
            now = datetime.now().strftime('%d-%m-%Y %H:%M')
            self.driver.save_screenshot(f'./{now}.png')
            traceback.print_exc()
            sys.exit()


def polish_date_to_datetime(date_string):
    values = date_string.split(' ')
    day = int(values[0])
    months ={
        'styczeń': 1,
        'stycznia': 1,
        'luty': 2,
        'lutego': 2,
        'marzec': 3,
        'marca': 3,
        'kwiecień': 4,
        'kwietnia': 4,
        'maj': 5,
        'maja': 5,
        'czerwiec': 6,
        'czerwca': 6,
        'lipiec': 7,
        'lipca': 7,
        'sierpień': 8,
        'sierpnia': 8,
        'wrzesień': 9,
        'września': 9,
        'październik': 10,
        'października': 10,
        'listopad': 11,
        'listopada': 11,
        'grudzień': 12,
        'grudnia': 12
    }
    month = months[values[1]]
    year = int(values[2][:-1])
    return datetime(year=year, month=month, day=day).strftime('%d-%m-%Y')


monika_prefs = PreferenceParser(
    [
        DatePreference(
            weight=80,
            targets=[DateTarget('09-07-2020'),]

        ),
        HourPreference(
            weight=20,
            targets=[
                HourTarget('09:00', '12:00'),
                HourTarget('18:00', '21:00'),
            ],
            required=True
        )
    ],
)

med_bot = Medicover(medi_login, medi_pwd, monika_prefs)

med_bot.run(specialty='Stomatolog - leczenie', doctor='Bałuszyńska Dagmara')
