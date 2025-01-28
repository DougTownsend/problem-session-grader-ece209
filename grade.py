import datetime
import os
import numpy as np
import io

def main():
    #Daylight saving time start and end dates
    dst_start = datetime.datetime(year=2025, month=3, day=9)
    dst_end = datetime.datetime(year=2025, month=11, day=2)

    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri"]

    #Get the Monday of the week of problem session
    monday = 0
    while True:
        monday = input("Enter the date of the Monday of the week of problem session (MM/DD/YYYY): ").split("/")
        monday = datetime.datetime(month=int(monday[0]), day=int(monday[1]), year=int(monday[2]))
        if monday.weekday() != 0:
            print("Date entered is not a Monday.")
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
        week_offset = start_offset + datetime.timedelta(days=7)
        if(monday < dst_start and monday + week_offset > dst_start):
           week_offset -= datetime.timedelta(hours=1)
        if(monday < dst_end and monday + week_offset > dst_end):
           week_offset += datetime.timedelta(hours=1)
        sec_times[section] = [start_offset, end_offset, week_offset]
    infile.close()
    
    resp = input("Where any sections delayed a week? (y/n): ")
    if resp == 'y':
        delayed_sections = input("Enter delayed sections, separated by commas (ex: 401,402,403): ").split(",")
        for sec in delayed_sections:
            sec_times[int(sec)][0] += datetime.timedelta(days=7)
            if monday < dst_start and monday + sec_times[int(sec)][0] > dst_start:
                sec_times[int(sec)][0] -= datetime.timedelta(hours=1)
            elif monday < dst_end and monday + sec_times[int(sec)][0] > dst_end:
                sec_times[int(sec)][0] += datetime.timedelta(hours=1)
            sec_times[int(sec)][1] += datetime.timedelta(days=7)
            if monday < dst_start and monday + sec_times[int(sec)][1] > dst_start:
                sec_times[int(sec)][1] -= datetime.timedelta(hours=1)
            elif monday < dst_end and monday + sec_times[int(sec)][1] > dst_end:
                sec_times[int(sec)][1] += datetime.timedelta(hours=1)
    
    for sec in sections:
        sec_times[sec][0] = monday + sec_times[sec][0]
        sec_times[sec][1] = monday + sec_times[sec][1]
        sec_times[sec][2] = monday + sec_times[sec][2]

    ps_num = input("Which problem session was this (1-6)?: ")
    ps_num = "PS" + ps_num

    attend = 0
    for f in os.listdir():
        if "attend" in f:
            attend = f

    attend_file = open(attend, "r")
    attend_str = attend_file.read()
    attend_str = attend_str.replace("\"", "")
    attend_file.close()

    current_sec = 0
    attend_col = 0
    student_times = dict() #student email is the key

    for line in attend_str.split("\n"):
        d = line.split(",")
        if d[0] == "Section":
            current_sec = int(d[1])
        elif d[0] == "ID":
            attend_col = d.index(ps_num)
        else:
            student_times[d[3]] = [[sec_times[current_sec][0], sec_times[current_sec][1]], [sec_times[current_sec][0], sec_times[current_sec][2]]]
            if d[attend_col] == "2":
                student_times[d[3]][0][1] = student_times[d[3]][1][1]
            if d[attend_col] == "0" or d[attend_col] == "":
                student_times[d[3]][0][1] = student_times[d[3]][0][0]
            
    print(student_times)

    email_col = 0
    grade_col = 0
    submit_datetime_col = 0
    submissions_file = 0

    for f in os.listdir(f"./{ps_num}"):
        if "zylab" in f:
            submissions_file = f"./{ps_num}/{f}"
    
    print(submissions_file)



    #Read class section rosters for generating final tables to input into Moodle
    rosters = dict()
    for file in os.listdir():
        if "roster" in file:
            section = int(file.split("_")[1].split(".")[0])
            rosters[section] = np.genfromtxt(file, delimiter=",", dtype=str, skip_header=True)

if __name__ == "__main__":
    main()