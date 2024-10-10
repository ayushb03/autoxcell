from flask import Flask, request, send_file, render_template
import pandas as pd
import random
import math
import csv
from io import StringIO, BytesIO

app = Flask(__name__)

# Initial configuration (random assignment)
def random_assignment(students):
    assignment = list(range(len(students)))  # Seats are 0, 1, 2, ...
    random.shuffle(assignment)  # Shuffle to create random assignment
    return assignment

# Objective function to calculate the number of adjacent same-course pairs
def objective_function(assignment, courses):
    conflicts = 0
    for i in range(len(assignment) - 1):
        if courses[assignment[i]] == courses[assignment[i + 1]]:
            conflicts += 1
    return conflicts

# Generate a neighbor solution by swapping two students
def generate_neighbor(assignment):
    neighbor = assignment[:]
    idx1, idx2 = random.sample(range(len(assignment)), 2)
    neighbor[idx1], neighbor[idx2] = neighbor[idx2], neighbor[idx1]
    return neighbor

# Simulated annealing algorithm
def simulated_annealing(students, courses, initial_temp=1000, cooling_rate=0.99, max_iterations=10000):
    current_solution = random_assignment(students)
    current_cost = objective_function(current_solution, courses)
    best_solution = current_solution[:]
    best_cost = current_cost

    temperature = initial_temp

    for iteration in range(max_iterations):
        neighbor = generate_neighbor(current_solution)
        neighbor_cost = objective_function(neighbor, courses)

        # Calculate the cost difference
        cost_diff = neighbor_cost - current_cost

        # Decide whether to accept the neighbor solution
        if cost_diff < 0 or random.random() < math.exp(-cost_diff / temperature):
            current_solution = neighbor
            current_cost = neighbor_cost

            # Update the best solution found
            if current_cost < best_cost:
                best_solution = current_solution[:]
                best_cost = current_cost

        # Cool down the temperature
        temperature *= cooling_rate

    return best_solution, best_cost

# Route to serve the HTML form
@app.route('/')
def index():
    return render_template('index.html')

# API route to handle the seat assignment process
@app.route('/assign-seats', methods=['POST'])
def assign_seats():
    # Load the input CSV
    file = request.files['file']
    df = pd.read_csv(file)

    students = df['UID'].tolist()
    courses = df['Course'].tolist()
    rooms = ['609', '601', '701', '605', '603']  # Define rooms

    # Run simulated annealing algorithm
    best_assignment, best_conflicts = simulated_annealing(students, courses)

    # Prepare the CSV output using StringIO first
    output_string = StringIO()  # Use StringIO for text output
    writer = csv.writer(output_string)

    writer.writerow(['Seat', 'UID', 'Course', 'Room'])

    current_capacity = 0
    current_room = 0
    limit = 35

    for seat, student_idx in enumerate(best_assignment):
        if current_capacity >= limit:
            current_room += 1
            current_capacity = 0
        current_capacity += 1
        writer.writerow([((seat) % limit) + 1, students[student_idx], courses[student_idx], rooms[current_room]])

    # Now convert the StringIO output to bytes
    output_string.seek(0)  # Move to the beginning of the StringIO stream
    output_bytes = BytesIO(output_string.getvalue().encode('utf-8'))  # Convert to bytes

    # Return the CSV file as a response
    return send_file(output_bytes, mimetype='text/csv', as_attachment=True, download_name='seat_assignment.csv')

if __name__ == '__main__':
    app.run(debug=True)
