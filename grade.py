import datetime
import os
import numpy as np

def main():
    #Daylight saving time start and end dates
    dst_start = datetime.datetime(year=2025, month=3, day=9)
    dst_end = datetime.datetime(year=2025, month=11, day=2)

    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri"]

    #Get the Monday of the week of problem session
    print("Enter the date of the Monday of the week of problem session (MM/DD/YYYY)")
    monday = 0
    while True:
        monday = input().split("/")
        monday = datetime.datetime(month=int(monday[0]), day=int(monday[1]), year=int(monday[2]))
        if monday.weekday() != 0:
            print("Date entered is not a Monday.")
            print("Enter the date of the Monday of the week of problem session (MM/DD/YYYY)")
        else:
            if (monday.year != dst_start.year) or (monday.year != dst_end.year):
                print("Error: Modify script DST start and end dates for current year")
                return
            break

    #read section times
    sections = []
    #Section times are represented as an offset from UTC midnight on monday
    #ZyBooks logs show time in UTC
    sec_times = dict()
    infile = open("section_times.csv", "r")
    for line in infile.read().splitlines()[1:]:
        data = line.split(",")
        section = int(data[0])
        sections.append(section)
        hours, minutes = data[2].split(":")
        hours = int(hours)
        minutes = int(minutes)
        start_offset = datetime.timedelta(days=weekdays.index(data[1]), hours=hours, minutes=minutes)
        if(monday < dst_start) or (monday > dst_end):
            start_offset += datetime.timedelta(hours=5)
        else:
            start_offset += datetime.timedelta(hours=4)
        end_offset = start_offset + datetime.timedelta(hours=1, minutes=50)
        sec_times[section] = [start_offset, end_offset]
    infile.close()

    #Read class section rosters for generating final tables to input into Moodle
    rosters = dict()
    for file in os.listdir():
        if "roster" in file:
            section = int(file.split("_")[1].split(".")[0])
            rosters[section] = np.genfromtxt(file, delimiter=",", dtype=str, skip_header=True)

if __name__ == "__main__":
    main()