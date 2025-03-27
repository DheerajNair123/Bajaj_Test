import pandas as pd
import re

def find_absent_streaks(attendance_df):
    attendance_df['prev_date'] = attendance_df.groupby('student_id')['attendance_date'].shift(1)
    attendance_df['next_date'] = attendance_df.groupby('student_id')['attendance_date'].shift(-1)

    attendance_df['gap'] = (attendance_df['attendance_date'] - attendance_df['prev_date']).dt.days
    attendance_df['group'] = (attendance_df['gap'] > 1).cumsum()

    absence_streaks = attendance_df[attendance_df['status'] == 'Absent'].groupby(['student_id', 'group']).agg(
        absence_start_date=('attendance_date', 'first'),
        absence_end_date=('attendance_date', 'last'),
        total_absent_days=('attendance_date', 'count')
    ).reset_index()

    latest_absence = absence_streaks.sort_values('absence_end_date').drop_duplicates('student_id', keep='last')
    return latest_absence[['student_id', 'absence_start_date', 'absence_end_date', 'total_absent_days']]

def is_valid_email(email):
    return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*@[a-zA-Z]+\.(com)$', email))

def run():
    attendance_data = {
        'student_id': [1, 1, 1, 1, 1, 2, 2, 2, 3, 3],
        'attendance_date': pd.to_datetime([
            '2025-03-20', '2025-03-21', '2025-03-22', '2025-03-23', '2025-03-24',
            '2025-03-21', '2025-03-22', '2025-03-23', '2025-03-22', '2025-03-23'
        ]),
        'status': ['Present', 'Absent', 'Absent', 'Absent', 'Present',
                   'Absent', 'Absent', 'Absent', 'Present', 'Absent']
    }

    students_data = {
        'student_id': [1, 2, 3],
        'student_name': ['Alice', 'Bob', 'Charlie'],
        'parent_email': ['alice_parent@gmail.com', 'bob123@domain.com', 'charlie@domaincom']
    }

    attendance_df = pd.DataFrame(attendance_data)
    students_df = pd.DataFrame(students_data)

    absence_df = find_absent_streaks(attendance_df)
    final_df = absence_df.merge(students_df, on='student_id', how='left')

    final_df['email'] = final_df['parent_email'].apply(lambda x: x if is_valid_email(x) else None)
    final_df['msg'] = final_df.apply(lambda row: f"Dear Parent, your child {row['student_name']} was absent from {row['absence_start_date'].date()} to {row['absence_end_date'].date()} for {row['total_absent_days']} days. Please ensure their attendance improves."
                                      if row['email'] else None, axis=1)

    return final_df[['student_id', 'absence_start_date', 'absence_end_date', 'total_absent_days', 'email', 'msg']]

if __name__ == "__main__":
    output_df = run()
    print(output_df)
