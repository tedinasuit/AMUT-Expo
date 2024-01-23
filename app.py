from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import tobii_research as tr
import time
import threading
from flask_cors import CORS
import subprocess
import psutil
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'media'  # Adjust the folder name accordingly
socketio = SocketIO(app)
latest_prompt = ""

found_eyetrackers = tr.find_all_eyetrackers()
my_eyetracker = found_eyetrackers[0]

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

@app.route('/add_prompt', methods=['POST'])
def add_prompt():
    global latest_prompt
    data = request.get_json()
    latest_prompt = data.get('prompt')
    return jsonify(success=True)

@app.route('/run_script', methods=['GET'])
def run_script():
    global latest_prompt
    # Replace this command with the actual command to run your Python script
    subprocess.run(['python', 'AMUT_workflow_SDXLTurbo.py', latest_prompt])
    return jsonify(success=True)

@app.route('/delete_files', methods=['POST'])
def delete_files():
    try:
        folder_path = "ComfyUI_windows_portable/ComfyUI/output/"
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

