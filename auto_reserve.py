import os
import json
from time import sleep
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import time
from datetime import datetime, timedelta
import sched

driver_path = os.environ['SELENIUM_DRIVER_PATH']


def reserve_hospital(is_debug=True, is_using_mockup=True):
    driver = webdriver.Chrome(driver_path)
    sleep_duration = 0.5

    # Choose to use mockup credential OR real credential
    if is_using_mockup == True:
        patient_info = {
            "url_reserve": f'file://{os.getcwd()}/hospital-website-mockup/1.html',
            "id": 12345,
            "birth_era": "平成",
            "birth_year": 1,
            "birth_month": 1,
            "birth_day": 1,
            "mail": "m.date@sendai.com"
    }
    else:
        patient_info = json.loads(os.environ['PATIENT_INFO'])

    # Open the browser
    driver.get(patient_info["url_reserve"])

    sleep(sleep_duration)

    try:
        # Input on page: "診療予約 TOP"
        if is_using_mockup == True:
            driver.find_element_by_xpath(
                "//a[@href='./2.html']").click()
        else:
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

        sleep(sleep_duration)

        driver.find_element_by_xpath(
            "//button[@onmousedown='chg(this,2);']"
        ).click()

        # Input on page: "メニュー"
        sleep(sleep_duration)
        driver.find_element_by_xpath(
            "//button[@name='yoyaku']").click()

        # Input on page: "空き状況"
        sleep(sleep_duration)
        if is_using_mockup == True:
            driver.find_element_by_xpath(
                "//a[contains(@href, '5.html')]"
            ).click()
        else:
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

        sleep(sleep_duration)

        driver.find_element_by_xpath(
            "//button[contains(text(), '次へ')]"
        ).click()

        # If this is the run for debugging, don't confirm the reservation
        if is_debug is True and is_using_mockup is False:
            print("Aborting: This is the run for debug.")
            sleep(3)
            return

        # Input on page: "受付内容の確認"
        # Finalize the reservation
        sleep(sleep_duration)
        driver.find_element_by_xpath(
            "//button[contains(text(), '次へ')]"
        ).click()

    except NoSuchElementException as e:
        print(e)
        print("Oops, maybe the hospital isn't accepting reservation now? \
            Or perhaps the website changed its layout?")

    sleep(3)
    driver.close()

    return


def get_schedule(is_debug=True):
    '''Returns time to reserve hospital.
    This hospital starts to accept a reservation after 6:00 AM every morning.

    Returns: (str)
        UNIX time
    '''
    now = datetime.now()

    if is_debug:
        # To test scheduling function, run retrieval function soon
        sched_time = now + timedelta(seconds=2)
    else:
        # If it's 6:00-24:00 now, set to the next day
        if(now.hour >= 6):
            sched_time = now + timedelta(days=1)

        # Set time to 6:00
        sched_time = sched_time.replace(
            hour=6,
            minute=0,
            second=3,
            microsecond=0)

    print("Scheduled at: ", sched_time)
    return sched_time.timestamp()


def test_google(driver):
    driver = webdriver.Chrome(driver_path)

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

    # When set True, reservation will be set soon
    # instead of 6:00 next morning,
    # and the reservation will be aborted before final confirmation
    is_debug = True

    s = sched.scheduler(time.time, sleep)
    s.enterabs(
        get_schedule(is_debug),
        1,
        reserve_hospital,
        argument=(is_debug, )  # Seemingly this "," can't be omitted
    )
    s.run()
