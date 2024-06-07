# MotionDetector
Multi-process motion detection pipeline 

## Components

1. **Streamer**: Reads frames from a video file and sends them to the Detector.
2. **Detector**: Receives frames, performs motion detection, and sends the frame along with detection contours to the Presenter.
3. **Presenter**: Receives frames and detection contours, displays them, and handles user input to terminate the process.

## Prerequisites

- Python 3.6 or higher
- `pip` (Python package installer)

## Setup

1. Clone the repository:

    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2. Create a virtual environment (optional but recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Running the Components

### Presenter

The Presneter reads frames from the Detector and shows the detections in each frame on the screen. 

**Arguments:**
- `presentor_address`: Address of the Presenter (which port to listen for incoming frames).

**Example:**

```bash
cd src
python presenter.py tcp://*:5556
```

### Detector

The Detector reads frames from the Streamer, detects motion as contours, and send them to the Presenter. 

**Arguments:**
- `detector_address`: Address of the Detector (which port to listen for incoming frames).
- `presenter_address`: Address of the Presenter.
- `min_contour_area`: The minimum area of the contours (rectangles) to detect.

**Example:**

```bash
cd src
python detector.py tcp://*:5555 tcp://127.0.0.1:5556 500
```

### Streamer

The Streamer reads frames from a video file and sends them to the Detector. 

**Arguments:**
- `video_path`: Path to the video file.
- `detector_address`: Address of the Detector.

**Example:**

```bash
cd src
python streamer.py "path_to_your_video_file.mp4" tcp://127.0.0.1:5555
```

