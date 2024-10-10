import pandas as pd
import numpy as np

def generate_student_grades(num_students=100, mean=75, std_dev=10, min_score=0, max_score=100):
    """
    Generate a dataset of student grades.
    
    Parameters:
        num_students (int): The number of students to simulate.
        mean (float): The mean score of the distribution.
        std_dev (float): The standard deviation of the distribution.
        min_score (int): Minimum possible score.
        max_score (int): Maximum possible score.

    Returns:
        pd.DataFrame: DataFrame containing student grades.
    """
    # Generate grades using a normal distribution
    grades = np.random.normal(loc=mean, scale=std_dev, size=num_students)

    # Clip grades to ensure they are within the specified bounds
    grades = np.clip(grades, min_score, max_score)

    # Create a DataFrame
    df = pd.DataFrame({
        'Student_ID': [f'STUD{i+1}' for i in range(num_students)],
        'Marks': grades
    })

    return df

def save_dataset_to_csv(df, filename='student_grades.csv'):
    """
    Save the dataset to a CSV file.
    
    Parameters:
        df (pd.DataFrame): The DataFrame to save.
        filename (str): The name of the output CSV file.
    """
    df.to_csv(filename, index=False)
    print(f'Dataset saved to {filename}')

if __name__ == "__main__":
    num_students = 100  # Number of students
    mean_score = 75     # Mean score
    std_dev = 10        # Standard deviation of scores

    # Generate dataset
    student_grades = generate_student_grades(num_students, mean_score, std_dev)

    # Save to CSV
    save_dataset_to_csv(student_grades)