import pandas as pd
import random

# Define the number of students and courses
num_students = 200  # Number of students
courses = [
    'CC', 'ADV', 'CSD', 'CE', 'AIH', 'RMV', 'BCT', 'SMA', 'DL', 'CA', 'RS', 'CSS'
]

# Generate student IDs
student_ids = [f'202130{str(i).zfill(4)}' for i in range(num_students)]

# Create an empty DataFrame to hold student enrollments with 'uid' as the first column
student_data = pd.DataFrame(index=student_ids, columns=courses)
student_data.reset_index(inplace=True)
student_data.rename(columns={'index': 'uid'}, inplace=True)

# Randomly assign enrollment status
for course in courses:
    student_data[course] = [random.choice([True, False]) for _ in range(num_students)]

# Optionally, ensure that some courses are more popular
# For example, we can enforce a minimum number of students enrolled in each course
for course in courses:
    # Randomly select a few students to ensure they are enrolled in this course
    students_to_enroll = random.sample(student_ids, k=random.randint(20, 50))  # 20 to 50 students
    for student in students_to_enroll:
        student_data.loc[student_data['uid'] == student, course] = True

# Fill any remaining NaNs with False (indicating not enrolled)
student_data.fillna(False, inplace=True)

# Save the DataFrame to a CSV file
student_data.to_csv('courses.csv', index=False)

print("Dataset created and saved as 'courses.csv'.")