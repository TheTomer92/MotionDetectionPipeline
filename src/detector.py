import cv2
import zmq
import numpy as np
import imutils
import argparse
import logging


def detector(detector_address, presenter_address, min_contour_area):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.bind(detector_address)
    socket.setsockopt(zmq.RCVHWM, 10)

    presenter_socket = context.socket(zmq.PUSH)
    presenter_socket.connect(presenter_address)

    prev_frame = None

    try:
        while True:
            message = socket.recv()
            if message == b'END':
                logging.info("End of frames signaled.")
                break

            np_frame = np.frombuffer(message, dtype=np.uint8)
            frame = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if prev_frame is None:
                prev_frame = gray_frame
                continue

            diff = cv2.absdiff(gray_frame, prev_frame)
            thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            prev_frame = gray_frame

            contours = []
            for contour in cnts:
                if cv2.contourArea(contour) < min_contour_area:
                    continue
                x, y, w, h = cv2.boundingRect(contour)
                contours.append((x, y, w, h))

            presenter_socket.send_multipart([message, np.array(contours).tobytes()])

    except Exception as e:
        logging.error(f"An error occurred: {e}")

    finally:
        presenter_socket.send_multipart([b'END'])
        logging.info("Detector finished.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Detect motion in video frames and send results to the presenter.")
    parser.add_argument('detector_address', type=str, help="Address of the detector.")
    parser.add_argument('presenter_address', type=str, help="Address of the presenter.")
    parser.add_argument('min_contour_area', type=int, help="Minimum contour area for motion detection.")
    args = parser.parse_args()

    detector(args.detector_address, args.presenter_address, args.min_contour_area)
