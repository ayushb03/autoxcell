from flask import Flask, request, jsonify, send_file, render_template
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import random
from datetime import datetime
import itertools
import os
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Global variable to store uploaded CSV path
uploaded_csv_path = ''

@app.route('/')
def index():
    """Render the main index page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    """Handle file upload.

    Expects a file to be uploaded in a POST request. 
    Saves the uploaded file to the 'uploads' directory and logs the action.

    Returns:
        JSON response with a success message or an error message.
    """
    global uploaded_csv_path
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    uploaded_csv_path = os.path.join('uploads', file.filename)
    file.save(uploaded_csv_path)
    logging.info(f'Uploaded file saved at: {uploaded_csv_path}')
    return jsonify({'message': 'File uploaded successfully'}), 200

@app.route('/generate_timetable', methods=['GET'])
def generate_timetable():
    """Generate a timetable based on uploaded student data.

    Loads student data from a CSV file and creates a timetable based on 
    subject overlaps. Implements a greedy coloring algorithm for scheduling 
    and generates a visual representation of the class network.

    Returns:
        JSON response with a success message or an error message.
    """
    global uploaded_csv_path
    if uploaded_csv_path == '':
        return jsonify({'error': 'No uploaded file found'}), 400

    # Load student data
    student_data = pd.read_csv(uploaded_csv_path)

    # Check if 'uid' column exists
    if 'uid' not in student_data.columns:
        return jsonify({'error': "CSV file must contain a 'uid' column."}), 400

    student_data = student_data.set_index('uid')

    # Retrieve the number of rooms from the request args
    num_rooms = int(request.args.get('num_rooms', 1))  # Default to 1 if not provided

    courses = list(student_data.columns)
    class_network = nx.Graph()
    class_network.add_nodes_from(courses)

    without_subj = student_data.T
    
    list_of_overlaps = []
    name_list = without_subj.columns
    for student in name_list:
        list_of_overlaps.append(list(without_subj.loc[without_subj[student]].index))

    for sublist in list_of_overlaps:
        for pair in itertools.combinations(sublist, 2):
            class_network.add_edge(pair[0], pair[1])

    colors = ["lightcoral", "gray", "lightgray", "firebrick", "red", "chocolate", "darkorange", 
              "moccasin", "gold", "yellow", "darkolivegreen", "chartreuse", "forestgreen", 
              "lime", "mediumaquamarine", "turquoise", "teal", "cadetblue", "dodgerblue", 
              "blue", "slateblue", "blueviolet", "magenta", "lightsteelblue"]
    
    def greedy_coloring_algorithm(network, colors):
        """Apply a greedy coloring algorithm to the class network.

        Assigns colors to nodes in the network such that no adjacent nodes share the same color.

        Args:
            network (nx.Graph): The class network graph.
            colors (list): A list of colors to be used for coloring the graph.
        """
        nodes = list(network.nodes())
        random.shuffle(nodes)
        for node in nodes:
            dict_neighbors = dict(network[node])
            nodes_neighbors = list(dict_neighbors.keys())

            forbidden_colors = []
            for neighbor in nodes_neighbors:
                if 'color' in network.nodes[neighbor]:  # Check if the 'color' attribute exists
                    forbidden_color = network.nodes[neighbor]['color']
                    forbidden_colors.append(forbidden_color)
            for color in colors:
                if color not in forbidden_colors:
                    network.nodes[node]['color'] = color
                    break

    greedy_coloring_algorithm(class_network, colors)
    
    dates = []
    calendar = {}
    for i in range(14, 20):
        for j in range(10, 18, 2):
            date = datetime(2024, 5, i, j, 0)
            dates.append(date)
            calendar[date] = []

    from_color_to_date = {col: dates[i] for i, col in enumerate(colors) if i < len(dates)}

    for v, data in class_network.nodes(data=True):
        color = data.get('color')
        if color in from_color_to_date:
            calendar[from_color_to_date[color]].append(v)

    # Ensure that rooms do not exceed the specified number
    rooms = ["Room " + str(i) for i in range(num_rooms)]
    
    # Create a DataFrame to hold the timetable
    if len(calendar) > 0:
        max_exams = len(max(list(calendar.values()), key=len))
        df = pd.DataFrame.from_dict(calendar, orient='index', columns=rooms[:max_exams])
    else:
        df = pd.DataFrame(columns=rooms)

    # Save to CSV
    timetable_csv_path = 'timetable.csv'
    df.to_csv(timetable_csv_path)

    # Generate class network image
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(class_network)
    nx.draw(class_network, pos, with_labels=True, node_color=[data['color'] for _, data in class_network.nodes(data=True)])
    plt.title('Class Network Graph')
    graph_image_path = 'class_network.png'
    plt.savefig(graph_image_path)
    plt.close()

    return jsonify({'message': 'Timetable generated'}), 200

@app.route('/download_image', methods=['GET'])
def download_image():
    """Download the generated class network image.

    Returns:
        Image file as an attachment if it exists, otherwise returns an error message.
    """
    graph_image_path = 'class_network.png'
    if not os.path.isfile(graph_image_path):
        logging.error(f"Image file not found: {graph_image_path}")
        return jsonify({'error': 'Image file not found'}), 404
    return send_file(graph_image_path, as_attachment=True)

@app.route('/download_csv', methods=['GET'])
def download_csv():
    """Download the generated timetable CSV file.

    Returns:
        CSV file as an attachment if it exists, otherwise returns an error message.
    """
    timetable_csv_path = 'timetable.csv'
    if not os.path.isfile(timetable_csv_path):
        logging.error(f"File not found: {timetable_csv_path}")
        return jsonify({'error': 'File not found'}), 404
    return send_file(timetable_csv_path, as_attachment=True)

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)   
    app.run(debug=True)
