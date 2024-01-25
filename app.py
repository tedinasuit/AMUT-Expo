from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO
import tobii_research as tr
import time
import threading
from flask_cors import CORS
import subprocess
import psutil
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/media'  # Adjust the folder structure accordingly
socketio = SocketIO(app)
CORS(app)
latest_prompt = ""

found_eyetrackers = tr.find_all_eyetrackers()
my_eyetracker = found_eyetrackers[0]

latest_generated_image = "amut_00001_.png"


gaze_data = {'left_gaze_point': (0, 0), 'right_gaze_point': (0, 0)}

def gaze_data_callback(gaze_data_dict):
    left_gaze_point = gaze_data_dict.get('left_gaze_point_on_display_area', (0, 0))
    right_gaze_point = gaze_data_dict.get('right_gaze_point_on_display_area', (0, 0))
    
    gaze_data['left_gaze_point'] = left_gaze_point
    gaze_data['right_gaze_point'] = right_gaze_point
    
    socketio.emit('update_gaze_data', gaze_data)

my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)

eye_tracker_thread = None  # Declare the thread variable globally

def start_eye_tracking():
    global eye_tracker_thread
    eye_tracker_thread = threading.Thread(target=eye_tracker_thread_function)
    eye_tracker_thread.daemon = True
    eye_tracker_thread.start()

def eye_tracker_thread_function():
    while True:
        time.sleep(0.1)  # Adjust the sleep time as needed
        tr.waitForCallbacks()


@app.route('/static/media/<filename>')
def serve_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/add_prompt', methods=['POST'])
def add_prompt():
    global latest_prompt
    data = request.get_json()
    latest_prompt = data.get('prompt')
    return jsonify(success=True)

@app.route('/run_script', methods=['GET'])
def run_script():
    global latest_prompt, latest_generated_image
    # Replace this command with the actual command to run your Python script
    subprocess.run(['python', 'AMUT_workflow_SDXLTurbo.py', latest_prompt])
    
    # Update the latest_generated_image variable
    image_files = [f for f in os.listdir('output') if f.endswith('_0001_')]
    if image_files:
        latest_generated_image = image_files[0]

    return jsonify(success=True)



@app.route('/get_latest_generated_image', methods=['GET'])
def get_latest_generated_image():
    global latest_generated_image
    return jsonify(filename=latest_generated_image)


@app.route('/get_latest_images', methods=['GET'])
def get_latest_images():
    # Retrieve the latest generated images in the 'output' folder
    image_folder = 'output'
    image_files = [f for f in os.listdir(image_folder) if f.endswith('_0001_')]
    return jsonify(images=image_files)

@app.route('/delete_files', methods=['POST'])
def delete_files():
    try:
        folder_path = "static\ComfyUI_windows_portable\ComfyUI\output"
        # Iterate over files in the folder and delete them
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

        return jsonify({'success': True, 'message': 'Files deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('start_eye_tracking')  # Added a new Socket.IO event for starting eye tracking
def handle_start_eye_tracking():
    start_eye_tracking()

if __name__ == '__main__':
    socketio.run(app)