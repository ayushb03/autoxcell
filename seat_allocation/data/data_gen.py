import pandas as pd
from faker import Faker
import random

# Initialize Faker
fake = Faker()

# Number of students to generate
num_students = 100  # Change this to generate more or fewer students

# List of example courses
courses = ['DL', 'ML', 'AI', 'DB', 'WE', 'OS', 'SE']

# Generate student data
student_data = {
    'UID': [f'{random.randint(201700000, 202300000)}' for _ in range(num_students)],
    'Course': [random.choice(courses) for _ in range(num_students)],
}

# Create a DataFrame
df = pd.DataFrame(student_data)

# Save to CSV
df.to_csv('generated_students.csv', index=False)

print(f"Generated {num_students} student records and saved to 'generated_students.csv'.")