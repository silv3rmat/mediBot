from selenium import webdriver

from pages import LoggedOutPage, LoginPage

driver = webdriver.Chrome()

start_page = LoggedOutPage(driver)

start_page.get_page()
main_window = driver.current_window_handle
start_page.click_login()


login_window = LoginPage(driver)



