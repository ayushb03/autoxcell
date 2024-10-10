from flask import Flask, jsonify, request, send_from_directory, render_template
import statistics
import numpy as np
import os

app = Flask(__name__)

# Example data format
data = {
    "course": "Mathematics 101",
    "marks": [85, 78, 92, 88, 67, 95, 74, 83, 60, 55, 70, 90],
    "person_marks": 92,  # The marks of the person you want to analyze
    "person_id": "student_3"  # Unique identifier of the person
}

# Helper function to compute percentile
def calculate_percentile(rank, total_students):
    return (rank / total_students) * 100

# Serve the index.html file from the templates folder
@app.route('/')
def index():
    return render_template('index.html')

# Course analysis API
@app.route('/course_analysis', methods=['GET'])
def course_analysis():
    marks = data['marks']
    
    # Statistical analysis
    average_marks = statistics.mean(marks)
    median_marks = statistics.median(marks)
    min_marks = min(marks)
    max_marks = max(marks)
    stddev_marks = statistics.stdev(marks)
    total_students = len(marks)
    
    # Quantile distribution
    quantiles = np.percentile(marks, [25, 50, 75])
    q1, q2, q3 = quantiles[0], quantiles[1], quantiles[2]
    
    # Proportion of students above and below average
    above_avg = len([m for m in marks if m > average_marks])
    below_avg = len([m for m in marks if m < average_marks])
    
    # Range distribution with finer intervals
    range_distribution = {
        "90-100": len([m for m in marks if 90 <= m <= 100]),
        "80-89": len([m for m in marks if 80 <= m <= 89]),
        "70-79": len([m for m in marks if 70 <= m <= 79]),
        "60-69": len([m for m in marks if 60 <= m <= 69]),
        "50-59": len([m for m in marks if 50 <= m <= 59]),
        "below 50": len([m for m in marks if m < 50])
    }
    
    # Response
    course_analysis_result = {
        "course_name": data['course'],
        "total_students": total_students,
        "average_marks": average_marks,
        "median_marks": median_marks,
        "min_marks": min_marks,
        "max_marks": max_marks,
        "stddev_marks": stddev_marks,
        "quantiles": {
            "25th_percentile": q1,
            "50th_percentile": q2,
            "75th_percentile": q3
        },
        "students_above_average": above_avg,
        "students_below_average": below_avg,
        "range_distribution": range_distribution
    }
    
    return jsonify(course_analysis_result)

# Person's performance API based on marks and person ID
@app.route('/person_performance', methods=['GET'])
def person_performance():
    person_marks = data['person_marks']  # The specific person's marks
    marks = data['marks']
    total_students = len(marks)
    
    # Sorting marks to determine rank
    sorted_marks = sorted(marks, reverse=True)
    person_rank = sorted_marks.index(person_marks) + 1  # 1-based index for ranking
    
    # Percentile calculation
    person_percentile = calculate_percentile(person_rank, total_students)
    
    # Deviation from average
    average_marks = statistics.mean(marks)
    deviation_from_average = person_marks - average_marks
    
    # Quartiles for person comparison
    quantiles = np.percentile(marks, [25, 50, 75])
    q1, q2, q3 = quantiles[0], quantiles[1], quantiles[2]
    
    # Check which quantile the person's marks fall into
    if person_marks <= q1:
        quantile_category = "Lower Quartile (0-25%)"
    elif q1 < person_marks <= q2:
        quantile_category = "Second Quartile (25-50%)"
    elif q2 < person_marks <= q3:
        quantile_category = "Third Quartile (50-75%)"
    else:
        quantile_category = "Top Quartile (75-100%)"
    
    # Response
    person_performance_result = {
        "person_id": data['person_id'],
        "person_marks": person_marks,
        "rank": person_rank,
        "total_students": total_students,
        "percentile": person_percentile,
        "deviation_from_average": deviation_from_average,
        "quantile_category": quantile_category
    }
    
    return jsonify(person_performance_result)

# Serve static files (if any)
@app.route('/<path:path>')
def static_file(path):
    return send_from_directory('', path)

if __name__ == '__main__':
    app.run(debug=True)
