from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, render_template, send_file
from werkzeug.utils import secure_filename
import os
from video_processor import process_video

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file'}), 400
    
    video = request.files['video']
    if video.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if video:
        filename = secure_filename(video.filename)
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        video.save(video_path)
        
        # 处理视频
        result = process_video(video_path)
        
        if 'error' in result:
            return jsonify(result), 500
        
        return jsonify(result), 200

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
