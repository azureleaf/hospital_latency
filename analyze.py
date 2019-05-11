import pandas as pd
from os import listdir
import os
from os.path import isfile, join
from datetime import datetime as dt
import matplotlib.pyplot as plt
from datetime import timedelta

# User Variables
my_reception_num = 60
now_reception_num = 50
now_time = 1930


def read_csv_dir():
    """ Read csv files, and returns them as dataframes
        Args: void
        Return: dictionary of pandas dataframes
            key is string "YY-MM-DD.csv"
            value is pandas dataframe which includes timestamp & number
    """
    csv_dir = os.getcwd() + "/csv"
    fileNames = [f for f in listdir(csv_dir) if isfile(join(csv_dir, f))]

    # Dataframe dictionary
    # format: {csv file name, file content dataframe}
    dfs = {}

    # Read csv one by one, and store to the dictionary
    for fileName in fileNames:

        # Read and add header
        df = pd.read_csv(
            os.getcwd() + "/csv/" + fileName,
            header=None,
            names=["time", "reception_number"])

        # Append new column, and fill with 0
        df["throughput"] = 0

        for i in range(len(df.index)):

            # For convenience, change time format
            #   into the lapse minutes from 0:00 of the day
            #   (Thus, 0:30 is 30, 23:59 is 1439)
            dt_obj = dt.strptime(df.loc[i, "time"], '%Y-%m-%d %H:%M:%S.%f')
            dt_obj = round_time(dt_obj)
            minutes = dt_obj.hour * 60 + dt_obj.minute
            df.loc[i, "time"] = minutes

            # calcuate throughput per cycle
            if(i != 0):
                df.loc[i, "throughput"] = \
                    df.loc[i, "reception_number"] \
                    - df.loc[i-1, "reception_number"]

        # Append dataframe to the dictionary
        dfs[fileName] = df

    return dfs


def round_time(dt_obj):
    """Ignore the small gap in the "minute" part
    (This is statistically inaccurate and unfavorable, though)

    Args: dt_obj (datetime object)
        (with small gap, like 10:02, 10:29)
    Return: dt_obj (datetime object)
        (gap removed, like 10:00, 10:30)
    """
    if (dt_obj.minute > 15 and dt_obj.minute < 45):
        dt_obj = dt_obj.replace(minute=30)
    elif (dt_obj.minute >= 45):
        dt_obj += timedelta(hours=1)
        dt_obj = dt_obj.replace(minute=0)
    else:
        dt_obj = dt_obj.replace(minute=0)
    return dt_obj


def show_daily_chart(dfs, date):
    """ Draw the chart of each day in the external window
    Args:
        dfs: dictionary of dataframes
            its key is string "YY-MM-DD.csv"
        date: string
            "YY-MM-DD"
    Return:
        Void
    """
    key = date + ".csv"
    df = dfs[key]
    print(df)
    df.plot(x="time", y="throughput")
    plt.show()


def get_average(dfs):
    """ Draw the chart of each day in the external window
    Args:
        dfs (dictionary of pandas dataframes)
            its key is string "YY-MM-DD.csv"
        date (str)
            "YY-MM-DD"
    Return:
        avg (array)
    """
    sum = {}

    # Access to every dataframe
    for key, df in dfs.items():

        # Access to each row in the single dataframe
        for i in range(len(df.index)):

            time = df.loc[i, "time"]

            # Number of patients processed in that time span
            throughput = df.loc[i, "throughput"]

            if(time in sum):
                sum[time]["sum"] += throughput
                sum[time]["count"] += 1
            else:
                sum[time] = {
                    "sum": throughput,
                    "count": 1,
                }

    # Array to store dictionaries: {time, average throughtput}
    avg = []
    for time, value in sum.items():

        # Convert time format: minutes to HHMM
        time = (time // 60)*100 + time % 60

        avg.append([
            time,
            round(value["sum"] / value["count"], 1)
        ])

    return avg


def analyze_main(my_num, curr_num, curr_time):
    """ Wrapper
    args:
        my_num (int)
            my reception number
        curr_num (int)
            reception number of the patient in the doctor's room
        curr_time (int)
            time of interest in the format of 0930, 1000, 1030, etc.
    return:
        void
    """
    dfs = read_csv_dir()
    # show_daily_chart(dfs, "2019-03-12")

    df = pd.DataFrame(get_average(dfs), columns=["time", "average_throughput"])
    df = df.sort_values(by=['time'])
    df = df.reset_index(drop=True)

    # Return the predicted reception time of you
    waiting_num = 0
    for index, row in df.iterrows():

        # Throughput before current time doesn't matter, so just ignore them
        if row["time"] < curr_time:
            continue

        if my_num < curr_num + waiting_num:
            print(
                "You will be seen by the doctor at: ",
                round(row["time"], 0))
            break

        waiting_num += row["average_throughput"]

    # Plot chart
    df.plot(x="time", y="average_throughput")
    plt.show()
    print(df)


if __name__ == "__main__":
    analyze_main(
        my_num=my_reception_num,
        curr_num=now_reception_num,
        curr_time=now_time
        )
