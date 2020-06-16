import os
import json
from time import sleep
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


driver_path = os.environ['SELENIUM_DRIVER_PATH']
patient_info = json.loads(os.environ['PATIENT_INFO'])
driver = webdriver.Chrome(driver_path)


def reserve_hospital(driver, is_debugging=True):

    # Open the browser
    driver.get(patient_info["url"])

    try:
        # Input on page: "診療予約 TOP"
        driver.find_element_by_xpath(
            "//a[@href='./php/id_pass_1.php']").click()

        # Input on page: "診察券番号と生年月日（和暦）の入力"
        driver.find_element_by_xpath(
            "//input[@name='card_1']"
        ).send_keys(patient_info["id"])

        driver.find_element_by_xpath(
            "//select[@name='gengo_1']/option[text()='{}']"
            .format(patient_info["birth_era"])
        ).click()

        driver.find_element_by_xpath(
            "//input[@name='year_1']"
        ).send_keys(patient_info["birth_year"])

        driver.find_element_by_xpath(
            "//select[@name='month_1']"
        ).send_keys(patient_info["birth_month"])

        driver.find_element_by_xpath(
            "//select[@name='day_1']"
        ).send_keys(patient_info["birth_day"])

        driver.find_element_by_xpath(
            "//button[@onmousedown='chg(this,2);']"
        ).click()

        # Input on page: "メニュー"
        driver.find_element_by_xpath(
            "//button[@name='yoyaku']").click()

        # Input on page: "空き状況"
        driver.find_element_by_xpath(
            "//a[contains(@href, 'yoyaku_decide.php')]"
        ).click()

        # Input on page: "メール送信の選択"
        driver.find_element_by_xpath(
            "//input[@name='osi_mail_1']"
        ).click()

        driver.find_element_by_xpath(
            "//select[@name='osi_kankaku_1']"
        ).send_keys("10")

        driver.find_element_by_xpath(
            "//input[@name='send_address_1']"
        ).clear()

        driver.find_element_by_xpath(
            "//input[@name='send_address_1']"
        ).send_keys(patient_info["mail"])

        driver.find_element_by_xpath(
            "//button[contains(text(), '次へ')]"
        ).click()

        # If this is the run for debugging, don't confirm the reservation
        if is_debugging is True:
            return

        # Input on page: "受付内容の確認"
        driver.find_element_by_xpath(
            "//button[contains(text(), '次へ')]"
        ).click()

    except NoSuchElementException as e:
        print(e)
        print("Oops, maybe the hospital isn't accepting reservation now? \
            Or perhaps the website changed its layout?")

    sleep(10)
    driver.close()

    return



def test_google(driver):

    # Open the browser
    driver.get("https://www.google.com/")

    driver.find_element_by_xpath(
        "//input[@name='q']"
    ).send_keys("仙台")

    sleep(1)

    driver.find_element_by_xpath(
        "//input[@name='btnK']"
    ).click()

    sleep(10)


if __name__ == "__main__":
    # test_google(driver)

    reserve_hospital(driver, is_debugging=True)
