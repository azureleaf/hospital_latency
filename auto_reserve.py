import os
from selenium import webdriver

driver_path = os.environ['SELENIUM_DRIVER_PATH']


def reserve_hospital():
    driver = webdriver.Chrome(driver_path)

    # Open the browser
    driver.get("https://www.google.com/")

    driver.find_element_by_xpath(
        "//input[@name='q']"
    ).send_keys("Sendai city")


reserve_hospital()
