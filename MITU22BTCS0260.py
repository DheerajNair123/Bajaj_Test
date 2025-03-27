import pandas as pd
import re

def find_absent_streaks(attendance_df):
    attendance_df = attendance_df.sort_values(['student_id', 'attendance_date'])
    attendance_df['prev_date'] = attendance_df.groupby('student_id')['attendance_date'].shift(1)
    attendance_df['gap'] = (attendance_df['attendance_date'] - attendance_df['prev_date']).dt.days
    
    absence_streaks = []
    for student, records in attendance_df.groupby('student_id'):
        streak_start, streak_end, total_absent = None, None, 0
        for _, row in records.iterrows():
            if row['status'] == 'Absent':
                if streak_start is None:
                    streak_start = row['attendance_date']
                streak_end = row['attendance_date']
                total_absent += 1
            else:
                if total_absent > 3:
                    absence_streaks.append([student, streak_start, streak_end, total_absent])
                streak_start, streak_end, total_absent = None, None, 0
        if total_absent > 3:
            absence_streaks.append([student, streak_start, streak_end, total_absent])
    
    return pd.DataFrame(absence_streaks, columns=['student_id', 'absence_start_date', 'absence_end_date', 'total_absent_days'])

def validate_email(email):
    return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*@[a-zA-Z]+\.[a-zA-Z]{2,}$', str(email)))

def process_attendance_data(path):
    xls = pd.ExcelFile(path)
    attendance_df = pd.read_excel(xls, sheet_name='Attendance_data')
    students_df = pd.read_excel(xls, sheet_name='Student_data')

    attendance_df['attendance_date'] = pd.to_datetime(attendance_df['attendance_date'])
    absent_streaks_df = find_absent_streaks(attendance_df)
    final_df = absent_streaks_df.merge(students_df[['student_id', 'student_name', 'parent_email']], on='student_id', how='left')

    final_df['valid_email'] = final_df['parent_email'].apply(validate_email)
    final_df['email'] = final_df['parent_email'].where(final_df['valid_email'])
    final_df['msg'] = final_df.apply(
        lambda x: f"Dear Parent, your child {x['student_name']} was absent from {x['absence_start_date'].date()} to {x['absence_end_date'].date()} for {x['total_absent_days']} days. Please ensure their attendance improves." 
        if x['valid_email'] else None, axis=1
    )

    return final_df[['student_id', 'absence_start_date', 'absence_end_date', 'total_absent_days', 'email', 'msg']]

sample_data_path = "data - sample.xlsx"
output_df = process_attendance_data(sample_data_path)
print(output_df.head())
