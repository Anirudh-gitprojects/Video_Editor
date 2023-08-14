import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import uuid

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploaded_videos'
SUBTITLES_FOLDER = 'subtitles'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # Folder to save video uploads
app.config['SUBTITLES_FOLDER'] = SUBTITLES_FOLDER  # Folder to save subtitles
app.config['SUBTITLES'] = {}  # Dictionary to store subtitles data


#Uplaod route for videos
@app.route('/api/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400

    video_file = request.files['video']
    if video_file.filename == '':
        return jsonify({'error': 'No video file selected'}), 400

    # Generate a unique filename for the video
    video_filename = str(uuid.uuid4()) + '_' + video_file.filename
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
    video_file.save(video_path)

    return jsonify({'message': 'Video uploaded successfully', 'video_url': video_filename}), 200

# Uplaod route for subtitles
@app.route('/api/create_subtitles/<string:video_filename>', methods=['POST'])
def create_subtitles(video_filename):
    subtitles_data = request.json

    subtitles_filename = video_filename + '.json'
    subtitles_path = os.path.join(app.config['SUBTITLES_FOLDER'], subtitles_filename)

    with open(subtitles_path, 'w') as file:
        json.dump(subtitles_data, file)

    return jsonify({'message': 'Subtitles created successfully'}), 200

# Get route for subtitles
@app.route('/api/subtitles/<string:video_filename>', methods=['GET'])
def get_subtitles(video_filename):
    subtitles_filename = video_filename + '.json'
    subtitles_path = os.path.join(app.config['SUBTITLES_FOLDER'], subtitles_filename)

    if not os.path.exists(subtitles_path):
        return jsonify({'error': 'Subtitles not found for the video'}), 404

    with open(subtitles_path, 'r') as file:
        subtitles_data = file.read()

    return subtitles_data, 200, {'Content-Type': 'application/json'}

# Get route for videos
@app.route('/uploaded_videos/<string:video_filename>', methods=['GET'])
def get_video(video_filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], video_filename)

# Optional api to get saved videos with subtitles
'''@app.route('/api/generate_video_with_subtitles/<string:video_filename>', methods=['GET'])
def generate_video_with_subtitles(video_filename):
    # Get the video and subtitles filenames
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
    subtitles_filename = video_filename + '.json'
    subtitles_path = os.path.join(app.config['SUBTITLES_FOLDER'], subtitles_filename)

    # Load video clip
    video_clip = VideoFileClip(video_path)

    # Load subtitles data
    with open(subtitles_path, 'r') as file:
        subtitles_data = json.load(file)

    # Create a list of TextClips for subtitles
    text_clips = []
    for subtitle in subtitles_data:
        text_clip = TextClip(subtitle['text'], fontsize=24, color='white', bg_color='black')
        text_clip = text_clip.set_position(('center', 'bottom')).set_duration(subtitle['duration'])
        text_clips.append(text_clip)

    # Composite the video with subtitles
    video_with_subtitles = CompositeVideoClip([video_clip] + text_clips)

    # Write the final video with subtitles
    output_filename = video_filename.replace('.mp4', '_with_subtitles.mp4')
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    video_with_subtitles.write_videofile(output_path, codec='libx264')

    return jsonify({'message': 'Video with subtitles created successfully', 'video_url': output_filename}), 200'''
if __name__ == '__main__':
    app.run(debug=True)
