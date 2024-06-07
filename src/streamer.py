import cv2
import zmq
import argparse
import logging


def streamer(video_path, detector_address):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.connect(detector_address)
    socket.setsockopt(zmq.SNDHWM, 10)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logging.error("Error opening video file.")
        return

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            _, buffer = cv2.imencode('.jpg', frame)
            socket.send(buffer.tobytes())

            if cv2.waitKey(1) & 0xFF == ord('q'):
                logging.info("Exit requested by user.")
                break

    except Exception as e:
        logging.error(f"An error occurred: {e}")

    finally:
        cap.release()
        socket.send_multipart([b'END'])  # Signal the end of the stream
        logging.info("Streamer finished.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Stream video frames to the detector.")
    parser.add_argument('video_path', type=str, help="Path to the video file.")
    parser.add_argument('detector_address', type=str, help="Address of the detector.")
    args = parser.parse_args()

    streamer(args.video_path, args.detector_address)
