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
            sec_times[int(sec)][2] += datetime.timedelta(days=7)
            if monday < dst_start and monday + sec_times[int(sec)][2] > dst_start:
                sec_times[int(sec)][2] -= datetime.timedelta(hours=1)
            elif monday < dst_end and monday + sec_times[int(sec)][2] > dst_end:
                sec_times[int(sec)][2] += datetime.timedelta(hours=1)
    
    for sec in sections:
        sec_times[sec][0] = monday + sec_times[sec][0]
        sec_times[sec][1] = monday + sec_times[sec][1]
        sec_times[sec][2] = monday + sec_times[sec][2]

    print(sec_times)

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
    student_times = dict() #student email is the key, format is [[full credit start, full credit end], [half credit start, half credit end]]

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
                student_times[d[3]][0][1] = student_times[d[3]][0][0] - datetime.timedelta(seconds=1)
            
    lastname_col = 0
    firstname_col = 0
    email_col = 0
    grade_col = 0
    submit_datetime_col = 0
    section_col = 0
    submissions_filename = 0

    student_grades = dict()

    for f in os.listdir(f"./{ps_num}"):
        if "zylab" in f:
            submissions_filename = f"./{ps_num}/{f}"
    


    sub_file = open(submissions_filename, "r")
    for line in sub_file.read().splitlines():
        #Remove the commas that are between quotation marks
        splitquote = line.split("\"")
        i = 1
        while i < len(splitquote):
            splitquote[i] = splitquote[i].replace(",", "")
            i += 2
        fixedline = "".join(splitquote)
        d = fixedline.split(",")

        #Skip the solution line
        if d[5] == "Solution":
            continue

        #Get the columns for the needed data
        if d[0] == "zybook_code":
            email_col = d.index("email")
            grade_col = d.index("score")
            submit_datetime_col = d.index("date_submitted(UTC)")
            section_col = d.index("class_section")
            lastname_col= d.index("last_name")
            firstname_col= d.index("first_name")
        else:
            email = d[email_col].lower()
            if email not in student_times:
                print(f"Skipping {email}")
                continue
            grade = float(d[grade_col])
            submission_datetime = datetime.datetime.strptime(d[submit_datetime_col], "%Y-%m-%d %H:%M:%S")
            class_sec = d[section_col]
            first = d[firstname_col]
            last = d[lastname_col]
            early = False
            late = False
            half_credit = False
            tmpgrade = 0
            if submission_datetime >= student_times[email][0][0] and submission_datetime <= student_times[email][0][1]:
                tmpgrade = grade
            elif submission_datetime >= student_times[email][1][0] and submission_datetime <= student_times[email][1][1]:
                tmpgrade = grade * 0.5
                half_credit = True
            elif submission_datetime > student_times[email][1][1]:
                late = True
            else:
                early = True
            if email not in student_grades:
                student_grades[email] = [last, first, email, class_sec, submission_datetime, tmpgrade, 0, 0, 0]
            else:
                if student_grades[email][5] < tmpgrade:
                    student_grades[email][4] = submission_datetime
                    student_grades[email][5] = tmpgrade
                if early:
                    student_grades[email][6] += 1
                if half_credit:
                    student_grades[email][7] += 1
                if late:
                    student_grades[email][8] += 1
                    

    grades_list = []
    for g in student_grades:
        grades_list.append(student_grades[g])
    
    grades_list.sort(key=lambda x: (x[3],x[0],x[1]))
    
    class_sections = []
    for g in grades_list:
        if g[3] not in class_sections:
            class_sections.append(g[3])

    for s in class_sections:
        outfile = open(f"./{ps_num}/{s}.csv", "w")
        for g in grades_list:
            if g[3] == s:
                outfile.write(f"{g[0]},{g[1]},{g[2]},{g[4]},{g[5]},")
                if g[6] > 0:
                    outfile.write(f"{g[6]} Early submissions,")
                if g[7] > 0:
                    outfile.write(f"{g[7]} Half-credit submissions,")
                if g[8] > 0:
                    outfile.write(f"{g[8]} Late submissions,")
                outfile.write("\n")
        outfile.close()



if __name__ == "__main__":
    main()