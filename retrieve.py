# coding: UTF-8
import os
import urllib.request
from bs4 import BeautifulSoup
import sched
import time
import re
import json
from datetime import datetime, date, timedelta

# User vaiable
retrieval_cycle = 1


def get_next_time(status, period):
    """Returns the time on which the following retrieval should run
    Args:
        status (str): status of hospital business
            Status types are defined in summarize_website():
                "accepting"
                "preparing"
                "beginning"
                "finished"
                "holiday"
        period (int): Time length (minutes) of each retrieval cycle.
            This value should be the divisor of 60, 
            i.e. 60, 30, 20, 12, 10, 6, 5, 4, 3, 2, 1.
            or it won't run on the regular cycles with certain time span
    Returns:
        datetime object: Returned when next retrieval time is planned
        None: Returned when not sure which time to set
    """

    now = datetime.now()

    # Set the next time of retrieval
    # according to the hospital status & current time
    if (status in {"accepting", "beginning"}) \
            or (status == "preparing" and 9 <= now.hour < 24):
        if now.minute + period < 60:
            next_min = (now.minute // period + 1) * period
            next_time = now.replace(minute=next_min)
        else:
            next_time = now + timedelta(hours=1)
            next_time = next_time.replace(minute=0)
    elif status in {"preparing"}:
        # Set to 9:00 during 0:00-9:00 in the day
        # Note that during 9:00-9:30 with "preparing" status,
        # program goes to the first "if" part, not this "elif" part
        next_time = now.replace(hour=9, minute=0)
    elif status in {"finished", "holiday"}:
        # Set to 9:00 in the following day
        next_time = now.replace(hour=9, minute=0) + timedelta(days=1)
    else:
        print("Error: Unknown Status: ", status)
        return None

    # Seconds & milliseconds don't matter,
    # therefore remove it to prevent undexpected side effect
    return next_time.replace(second=0, microsecond=0)


def summarize_website(url):
    """Retrieve current patient number from the website
    Args:
        url (str): URL of the page of interest
    Returns:
        (dict):
            key: "status" (str), reception status of the hospital
            value: "patient_num" (int)
        (None):
            On error (No keyword expected found)
    """

    # Define the mapping from hospital service status
    # to the keyword which are specific to the website status.
    keywords = {
        "accepting": r'診察済の番号',  # first-last
        "preparing": r'開始前',  # 0:00-9:30
        "beginning": r'診察開始',  # 9:30-first ???
        "finished": r'診察終了',  # last-23:59
        "holiday": r'休診日',  # 0:00-23:59 ???
    }

    # Retrieve HTML file and parse it
    html = urllib.request.urlopen(url)
    soup = BeautifulSoup(html, "html.parser")

    # Dict to return
    curr_status = {}

    # "<span class="mark>" tag appears only during service hours"
    tag_span = soup.find("span", {"class": "mark"})
    if(tag_span is not None):
        curr_status["status"] = "accepting"
        curr_status["patient_num"] = int(tag_span.contents[0])
        return curr_status
    else:
        # Match every keyword to the retrieved text
        for status, pattern in keywords.items():
            # Skip "accepting" because this will never match
            if status == "accepting":
                continue

            match_obj = re.search(pattern, soup.get_text())
            if (match_obj is not None):
                curr_status["status"] = status
                curr_status["patient_num"] = None
                return curr_status

    # Save error log with soup when the keyword is unknown
    print("Error: none of the target word found.\n\
        Check retrieved text in the log file.")
    log_path = os.getcwd() + "/html_error_log"
    with open(log_path, "w", encoding="utf-8") as f:
        f.writelines(str(soup))
    return None


def write_csv(reception_num):
    """Get number, and output it with timestamp
    Args:
        reception_num(int)
    Returns:
        0: When successfully output csv file
        1: When output csv file fails
    """
    # Format time
    d = datetime.now().isoformat(' ')
    new_line = "{},{}\n".format(d, reception_num)
    today = date.today().isoformat()  # YYYY-MM-DD

    csv_path = os.getcwd() + "/csv/" + today + ".csv"

    # Error handling for file I/O
    try:
        with open(csv_path, mode='a', encoding="utf-8") as f:
            f.write(new_line)
    except IOError:
        print("IOError: Is the CSV file path correct?")
        return 1
    except Exception as e:
        print("Unknown error in writing file:", e)
        return 1

    return 0


def main_loop():
    """Periodically check the webpage.
    Retrieval loop breaks:
        when failed to specify the hospital status from the website
        when timeteller function doesn't know the status referred
        when writing CSV file is failed
    """

    # Scheduler can't return the value from callback.
    # Therefore I use empty function as a callback.
    # This empty function is still useful as a periodic event trigger.
    def dummy():
        pass

    # Tell if this is the very time you started this program
    is_first_round = True

    # Error flag for saving CSV, such as IOError
    has_output_error = False

    while True:
        s = sched.scheduler(time.time, time.sleep)

        # If task queue is empty, set task
        if s.empty():

            site_summary = summarize_website(json.loads(
                os.environ['PATIENT_INFO'])["url_retrieve"])
            if (site_summary is None):  # Hospital status is unknown
                return 1
            next_run_time = get_next_time(
                site_summary["status"], retrieval_cycle)

            # Skip retrieval on the first round
            if is_first_round:
                is_first_round = False
            else:
                # Set patient num
                if (site_summary["status"] == "accepting"):
                    patient_num = site_summary["patient_num"]
                # Set patient num as 0 when it is the beginning
                elif (site_summary["status"] == "beginning"):
                    petient_num = 0

                # Save to CSV
                has_output_error = write_csv(patient_num)
                print("=> Current reception number:", patient_num)

            # Get out of the while loop on errors
            if (next_run_time is None) or \
                    has_output_error:
                return 1

            print("Next scheduled check: ", next_run_time)

            # Writing action with "()" won't work
            # Function without "()" is actually a function pointer in Python
            s.enterabs(next_run_time.timestamp(), 1, dummy)
            s.run()


if __name__ == "__main__":
    main_loop()
