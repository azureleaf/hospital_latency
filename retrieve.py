# coding: UTF-8
import os
import urllib.request
from bs4 import BeautifulSoup
import sched
import time
import re
from datetime import datetime, date, timedelta

# User variables
hospital_url = "HOSPITAL_URL_HERE"
retrieval_cycle = 30


def get_next_time(status, period):
    """Returns the time on which the following retrieval should run
    Args:
        status (str): status of hospital business
            Status types are defined in check_website()
        period (int): Time length (minutes) of each retrieval cycle.
            This value should be the divisor of 60 (e.g. 30, 20, 10, 5)
            or it won't run on the regular cycles with even time span
    Returns:
        datetime object: Returned when next retrieval time is planned
        None: Returned when not sure which time to set
    """

    now = datetime.now()

    # Returns time according to the hospital status & current time
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
    # therefore remove it for clarity
    return next_time.replace(second=0, microsecond=0)


def check_website(url):
    """Retrieve current hospital information from the website
    Args:
        url (str): URL of the page of interest
    Returns:
        dictionary:
            key: "status", tells which reception status the hospital is in
            value: "result of regular expression match",
                reception number is stored if available
        None:
            Returned when no matching keyword is found (that is, error)
    """

    # Definition of hospital service status,
    # and the keyword which is included in the website for each status
    # Each keyword is used to specify the status.
    # Keyword for "accepting" won't be used.
    keywords = {
        "accepting": None,  # first-last
        "preparing": r'開始前',  # 0:00-9:30
        "beginning": r'診察開始',  # 9:30-first ???
        "finished": r'診察終了',  # last-23:59
        "holiday": r'休診日',  # 0:00-23:59 ???
    }

    # Retrieve HTML file and parse it
    html = urllib.request.urlopen(url)
    soup = BeautifulSoup(html, "html.parser")

    # Dictionary to return
    curr_status = {
        "status": None,
        "patient_num": None
    }

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
                return curr_status

    # Keep log when there's no match to "keywords"
    print("Error: none of the target word found.\n\
        Check retrieved text in the log file.")
    log_path = os.getcwd() + "/html_error_log"
    with open(log_path, "w", encoding="utf-8") as f:
        # f.writelines(soup.get_text())
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
    today = date.today().isoformat()  # YYYY-MM-DD format

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
    """Periodically check the webpage
    Args:
        void
    Returns:
        void
    Breaks:
        when failed to specify the hospital status from the website
        when timeteller function doesn't know the status referred
        when writing CSV file is failed
    """

    #   Scheduler function can't return the value from callback,
    #   while I want to use the value.
    #   Therefore I use empty function as a callback.
    #   Even with empty function like this,
    #   this is still useful as a periodic event trigger.
    def dummy():
        pass

    #   Because you're not interested in the reception number
    #   on the very time you started this program,
    #   you need to skip the first round
    is_first_round = True

    # This flag goes True when there's any Error in outputting csv
    # Most likely one is IOError caused by wrong path
    has_output_error = False

    while True:
        s = sched.scheduler(time.time, time.sleep)

        # If task queue is empty, set task
        if s.empty():

            result = check_website(hospital_url)
            if (result is None):
                return 1
            next_run_time = get_next_time(result["status"], retrieval_cycle)

            # Don't retrieve data if it's the first time
            if is_first_round:
                is_first_round = False
            else:
                # Record to CSV file, and set error flag
                if (result["status"] == "accepting"):
                    has_output_error = write_csv(result["patient_num"])
                # When it is the beginning of the office hours,
                # output patient numbers as "0"
                elif (result["status"] == "beginning"):
                    has_output_error = write_csv(0)

            # Get out of the while loop on errors
            if (next_run_time is None) or \
                    has_output_error:
                return 1

            print("Next scheduled check: ", next_run_time)

            # Don't write action with "()", it won't work correctly;
            # If so, enterabs() will just set "returned value" as an action,
            # rathan than function itself.
            # Function without "()" is actually a function pointer in Python
            s.enterabs(next_run_time.timestamp(), 1, dummy)
            s.run()


main_loop()
