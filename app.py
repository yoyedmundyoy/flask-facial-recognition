from flask import Flask, request, jsonify
from deepface import DeepFace
import os
import uuid
import werkzeug

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/verify', methods=['POST'])
def verify_faces():
    # Check if two images were uploaded
    if 'image1' not in request.files or 'image2' not in request.files:
        return jsonify({'error': 'Two images required'}), 400
    
    image1 = request.files['image1']
    image2 = request.files['image2']
    
    # Validate files
    if image1.filename == '' or image2.filename == '':
        return jsonify({'error': 'No selected files'}), 400
    
    # Create unique filenames
    filename1 = str(uuid.uuid4()) + werkzeug.utils.secure_filename(image1.filename)
    filename2 = str(uuid.uuid4()) + werkzeug.utils.secure_filename(image2.filename)
    
    # Save files
    filepath1 = os.path.join(UPLOAD_FOLDER, filename1)
    filepath2 = os.path.join(UPLOAD_FOLDER, filename2)
    
    image1.save(filepath1)
    image2.save(filepath2)
    
    try:
        # Verify faces
        result = DeepFace.verify(img1_path=filepath1, img2_path=filepath2)
        
        # Clean up files after processing
        os.remove(filepath1)
        os.remove(filepath2)
        
        return jsonify(result)
    
    except Exception as e:
        # Clean up files in case of error
        if os.path.exists(filepath1):
            os.remove(filepath1)
        if os.path.exists(filepath2):
            os.remove(filepath2)
        
        return jsonify({'error': str(e)}), 500