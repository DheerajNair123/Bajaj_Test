import pandas as pd
import re

def find_absent_streaks(attendance_df):
    attendance_df['prev_date'] = attendance_df.groupby('student_id')['attendance_date'].shift(1)
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
        'student_id': [101, 101, 101, 101, 101, 102, 102, 102, 102, 103, 103, 103, 103, 103],
        'attendance_date': pd.to_datetime([
            '2024-02-28', '2024-03-01', '2024-03-02', '2024-03-03', '2024-03-04',
            '2024-03-01', '2024-03-02', '2024-03-03', '2024-03-04', '2024-03-05',
            '2024-03-06', '2024-03-07', '2024-03-08', '2024-03-09'
        ]),
        'status': ['Present', 'Absent', 'Absent', 'Absent', 'Absent',
                   'Present', 'Absent', 'Absent', 'Absent', 'Absent',
                   'Absent', 'Absent', 'Absent', 'Absent']
    }

    students_data = {
        'student_id': [101, 102, 103],
        'student_name': ['Alice Johnson', 'Bob Smith', 'Charlie Brown'],
        'parent_email': ['alice_parent@example.com', 'bob_parent@example.com', 'invalid_email.com']
    }

    attendance_df = pd.DataFrame(attendance_data)
    students_df = pd.DataFrame(students_data)

    absence_df = find_absent_streaks(attendance_df)
    final_df = absence_df.merge(students_df, on='student_id', how='left')

    final_df['email'] = final_df['parent_email'].apply(lambda x: x if is_valid_email(x) else None)
    final_df['msg'] = final_df.apply(lambda row: f"Dear Parent, your child {row['student_name']} was absent from {row['absence_start_date'].strftime('%Y-%m-%d')} to {row['absence_end_date'].strftime('%Y-%m-%d')} for {row['total_absent_days']} days. Please ensure their attendance improves."
                                      if row['email'] else None, axis=1)

    # Format dates as DD-MM-YYYY for expected output
    final_df['absence_start_date'] = final_df['absence_start_date'].dt.strftime('%d-%m-%Y')
    final_df['absence_end_date'] = final_df['absence_end_date'].dt.strftime('%d-%m-%Y')

    return final_df[['student_id', 'absence_start_date', 'absence_end_date', 'total_absent_days', 'email', 'msg']]

if __name__ == "__main__":
    output_df = run()
    print(output_df)
