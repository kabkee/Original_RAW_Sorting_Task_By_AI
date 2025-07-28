import os
import shutil
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from PIL import Image
from PIL.ExifTags import TAGS
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key
app.config['UPLOAD_FOLDER'] = 'origin_photos'
app.config['MAX_CONTENT_LENGTH'] = 1000 * 1024 * 1024  # 500MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'cr2', 'arw', 'nef'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_datetime_original(path):
    try:
        img = Image.open(path)
        exif_data = img._getexif()
        if not exif_data:
            return None
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == 'DateTimeOriginal':
                return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
    except Exception as e:
        print(f"Error reading {path}: {e}")
    return None

def group_photos(seconds_threshold=60):
    photo_dir = app.config['UPLOAD_FOLDER']
    files = [f for f in os.listdir(photo_dir) if f.lower().endswith(tuple(f'.{ext}' for ext in ALLOWED_EXTENSIONS))]
    
    file_times = []
    for f in files:
        path = os.path.join(photo_dir, f)
        dt = get_datetime_original(path)
        if dt:
            file_times.append((f, dt))
    
    if not file_times:
        return 0  # No valid photos found
    
    # Sort files by datetime
    file_times.sort(key=lambda x: x[1])
    
    # Group photos
    groups = []
    current_group = []
    last_time = None
    
    for fname, dt in file_times:
        if not last_time or (dt - last_time).total_seconds() > seconds_threshold:
            if current_group:
                groups.append(current_group)
            current_group = [fname]
        else:
            current_group.append(fname)
        last_time = dt
    
    if current_group:
        groups.append(current_group)
    
    # Move files to group directories
    for idx, group in enumerate(groups, 1):
        group_dir = os.path.join(photo_dir, f'group_{idx}')
        os.makedirs(group_dir, exist_ok=True)
        for fname in group:
            src = os.path.join(photo_dir, fname)
            dst = os.path.join(group_dir, fname)
            shutil.move(src, dst)
    
    return len(groups)

def ungroup_photos():
    photo_dir = app.config['UPLOAD_FOLDER']
    moved_count = 0
    
    # Move all files from subdirectories to the main directory
    for root, dirs, files in os.walk(photo_dir, topdown=False):
        if root == photo_dir:
            continue  # Skip the root directory
            
        for file in files:
            if any(file.lower().endswith(f'.{ext}') for ext in ALLOWED_EXTENSIONS):
                src_path = os.path.join(root, file)
                dst_path = os.path.join(photo_dir, file)
                
                # Handle filename conflicts
                counter = 1
                while os.path.exists(dst_path):
                    name, ext = os.path.splitext(file)
                    new_filename = f"{name}_{counter}{ext}"
                    dst_path = os.path.join(photo_dir, new_filename)
                    counter += 1
                
                shutil.move(src_path, dst_path)
                moved_count += 1
    
    # Remove empty directories
    for root, dirs, files in os.walk(photo_dir, topdown=False):
        if root == photo_dir:
            continue  # Skip the root directory
        try:
            if not os.listdir(root):
                os.rmdir(root)
        except Exception as e:
            print(f"Error removing directory {root}: {e}")
    
    return moved_count

@app.route('/')
def index():
    # Get list of all photos in the upload directory
    photo_dir = app.config['UPLOAD_FOLDER']
    all_photos = [f for f in os.listdir(photo_dir) if f.lower().endswith(tuple(f'.{ext}' for ext in ALLOWED_EXTENSIONS))]
    
    # Get list of group directories
    group_dirs = [d for d in os.listdir(photo_dir) 
                 if os.path.isdir(os.path.join(photo_dir, d)) and d.startswith('group_')]
    
    # Count photos in each group
    groups = {}
    for group_dir in group_dirs:
        group_path = os.path.join(photo_dir, group_dir)
        group_photos = [f for f in os.listdir(group_path) 
                       if f.lower().endswith(tuple(f'.{ext}' for ext in ALLOWED_EXTENSIONS))]
        if group_photos:  # Only include non-empty groups
            groups[group_dir] = group_photos
    
    # Count ungrouped photos (in the root directory)
    ungrouped_photos = [f for f in all_photos 
                       if not any(f in group_photos for group_photos in groups.values())]
    
    # Add ungrouped photos to the groups dictionary
    if ungrouped_photos:
        groups['Ungrouped'] = ungrouped_photos
    
    return render_template('index.html', 
                         groups=groups, 
                         group_count=len([g for g in groups.keys() if g != 'Ungrouped']),
                         photo_count=len(all_photos))

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files[]' not in request.files:
        flash('No files selected')
        return redirect(request.url)
    
    files = request.files.getlist('files[]')
    uploaded_count = 0
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            uploaded_count += 1
    
    if uploaded_count > 0:
        flash(f'Successfully uploaded {uploaded_count} files')
    else:
        flash('No valid files were uploaded')
    
    return redirect(url_for('index'))

@app.route('/group', methods=['POST'])
def group():
    try:
        seconds = int(request.form.get('seconds', 180))
        if seconds <= 0:
            flash('Grouping time must be a positive number')
            return redirect(url_for('index'))
        
        group_count = group_photos(seconds)
        flash(f'Successfully grouped photos into {group_count} groups')
    except Exception as e:
        flash(f'Error grouping photos: {str(e)}')
    
    return redirect(url_for('index'))

@app.route('/ungroup')
def ungroup():
    try:
        moved_count = ungroup_photos()
        flash(f'Successfully ungrouped {moved_count} photos')
    except Exception as e:
        flash(f'Error ungrouping photos: {str(e)}')
    
    return redirect(url_for('index'))

@app.route('/photos/<path:filename>')
def uploaded_file(filename):
    upload_folder = app.config['UPLOAD_FOLDER']
    # First try to find the file directly in the upload folder
    file_path = os.path.join(upload_folder, filename)
    if os.path.isfile(file_path):
        return send_from_directory(upload_folder, filename)
    
    # If not found, search in subdirectories
    for root, dirs, files in os.walk(upload_folder):
        if filename in files:
            return send_from_directory(root, filename)
    
    # If file is not found, return 404
    return "File not found", 404

if __name__ == '__main__':
    app.run(debug=True)
