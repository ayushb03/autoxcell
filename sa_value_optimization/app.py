from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from scipy import stats

app = Flask(__name__, static_folder='static')

# Function to calculate grade ranges
def calculate_grade_ranges(SA, Span, median):
    AA_range = f"Greater than {SA} upto 100"
    AB_start = SA - Span + 1
    AB_range = f"{AB_start} to {SA}"
    BB_start = SA - 2 * Span + 1
    BB_end = SA - Span
    BB_range = f"{BB_start} to {BB_end}"
    BC_start = SA - 3 * Span + 1
    BC_end = SA - 2 * Span
    BC_range = f"{BC_start} to {BC_end}"
    CC_start = SA - 4 * Span + 1
    CC_end = SA - 3 * Span
    CC_range = f"{CC_start} to {CC_end}"
    CD_start = SA - 5 * Span + 1
    CD_end = SA - 4 * Span
    CD_range = f"{CD_start} to {CD_end}"
    median = np.ceil(median)
    DD_start = median / 2 if median % 2 == 0 else (median + 1) / 2
    DD_range = f"{int(DD_start)} to {CD_start - 1}"
    FF_range = f"Less than {int(DD_start)}"

    return {
        'AA': AA_range, 'AB': AB_range, 'BB': BB_range, 'BC': BC_range,
        'CC': CC_range, 'CD': CD_range, 'DD': DD_range, 'FF': FF_range
    }

# Function to categorize marks
def categorize_marks(mark, SA, Span, median):
    if mark > SA:
        return "AA"
    elif SA - Span + 1 <= mark <= SA:
        return "AB"
    elif SA - 2 * Span + 1 <= mark <= SA - Span:
        return "BB"
    elif SA - 3 * Span + 1 <= mark <= SA - 2 * Span:
        return "BC"
    elif SA - 4 * Span + 1 <= mark <= SA - 3 * Span:
        return "CC"
    elif SA - 5 * Span + 1 <= mark <= SA - 4 * Span:
        return "CD"
    elif mark >= (median / 2 if median % 2 == 0 else (median + 1) / 2):
        return "DD"
    else:
        return "FF"

# Function to calculate normality using Shapiro-Wilk test
def calculate_normality(grade_counts):
    grade_values = {'FF': 1, 'DD': 2, 'CD': 3, 'CC': 4, 'BC': 5, 'BB': 6, 'AB': 7, 'AA': 8}
    numerical_data = []
    for grade, count in grade_counts.items():
        numerical_data.extend([grade_values[grade]] * count)

    if len(set(numerical_data)) == 1:
        return 0

    _, p_value = stats.shapiro(numerical_data)
    return p_value

# Analyze distributions
def analyze_distributions(df, st, en, span):
    median = df['Marks'].median()
    best_sa = None
    best_p_value = 0
    best_grade_counts = None

    for sa in range(st, en):
        df['Grade'] = df['Marks'].apply(lambda x: categorize_marks(x, sa, span, median))
        grade_counts = df['Grade'].value_counts().sort_index()

        p_value = calculate_normality(grade_counts)

        if p_value > best_p_value:
            best_p_value = p_value
            best_sa = sa
            best_grade_counts = grade_counts

    return best_sa, best_p_value, best_grade_counts

# Save chart
def save_chart(best_grade_counts, sa_value, subject_name):
    plt.figure(figsize=(12, 6))
    ax = best_grade_counts.plot(kind='bar', color='skyblue')
    plt.title(f'Distribution of Grades (SA={sa_value}) for {subject_name}')
    plt.xlabel('Grade')
    plt.ylabel('Number of Students')
    plt.tight_layout()

    chart_path = os.path.join('static', f'grade_distribution_{sa_value}.png')
    plt.savefig(chart_path)
    plt.close()
    return chart_path

# Route for homepage
@app.route('/')
def index():
    return render_template('index.html')

# API route for analyzing grades
@app.route('/api/analyze', methods=['POST'])
def analyze():
    sa_value = int(request.form['saValue'])
    file = request.files['filePath']
    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)

    df = pd.read_csv(file_path)

    sa_ranges = [[60, 71], [70, 81], [80, 91], [90, 101]]
    results = {}

    for st, en in sa_ranges:
        best_sa, best_p_value, best_grade_counts = analyze_distributions(df, st, en, 9)

        results[best_sa] = {
            'gradeRanges': calculate_grade_ranges(best_sa, 9, df['Marks'].median()),
            'gradeCounts': best_grade_counts.to_dict()
        }

        # Save the chart
        chart_path = save_chart(best_grade_counts, best_sa, "Student Marks")
        results[best_sa]['chartPath'] = f'/static/grade_distribution_{sa_value}.png'

    return jsonify(results)

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    app.run(debug=True)
