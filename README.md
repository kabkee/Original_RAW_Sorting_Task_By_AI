# Photo Organizer Web App

A user-friendly web application for organizing photos into groups based on their capture time. This tool helps you easily group photos taken within a specified time interval and ungroup them when needed.

## Features

- **Upload Photos**: Drag and drop or click to upload multiple photos at once
- **Group Photos**: Automatically group photos taken within a specified time interval
- **Ungroup Photos**: Move all photos back to the main directory
- **Responsive Design**: Works on both desktop and mobile devices
- **Photo Previews**: See thumbnails of your photos and groups

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. Clone or download this repository
2. Navigate to the project directory
3. Install the required packages:

```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the Flask development server:

```bash
python app.py
```

2. Open your web browser and go to:

```
http://localhost:5000
```

## How to Use

1. **Upload Photos**:
   - Click on the upload area or drag and drop your photos
   - Supported formats: JPG, JPEG, PNG, CR2, ARW, NEF

2. **Group Photos**:
   - Enter the time interval (in seconds) for grouping
   - Click "Group Photos"
   - Photos taken within the specified time interval will be grouped together

3. **Ungroup Photos**:
   - Click "Ungroup All Photos" to move all photos back to the main directory
   - This will also remove all empty group folders

## Project Structure

- `app.py`: Main Flask application
- `templates/`: HTML templates
  - `base.html`: Base template with common structure
  - `index.html`: Main page with photo upload and organization interface
- `origin_photos/`: Directory where uploaded photos are stored
- `requirements.txt`: Python dependencies

## License

This project is open source and available under the [MIT License](LICENSE).
