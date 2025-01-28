#ECE 209 Problem Session Grader

1. Export the attendance sheet to CSV and place in main directory (same directory as grade.py)
2. Download the submission log from zybooks. For the old style zylabs that do not have the built in VSCode environment
open the lab section in zybooks, go to "Lab statistics and submissions" and click "Download log of all runs." For
the new style zylabs go to "Student activity" and click "Download student activity data."
3. Put the downloaded CSV into the directory that corresponds to that problem session.
4. Run grade.py
5. Enter the date of the monday at the start of the problem session week.
6. If any sections were delayed a week, answer "y" and then enter the delayed section numbers seperated by commas.
7. Enter which problem session number needs to be graded.
8. The directory that corresponds to that problem session will now have CSV files for each class section with the grades.
Students that did not submit anything will not show up in the grades CSV.