import cv2
import zmq
import numpy as np
import datetime
import logging
import argparse


def presenter(presenter_address):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.bind(presenter_address)
    socket.setsockopt(zmq.RCVHWM, 10)

    try:
        while True:
            message = socket.recv_multipart()
            if message[0] == b'END':
                logging.info("End of frames signaled.")
                break

            frame_bytes = message[0]
            contours_bytes = message[1]

            np_frame = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)
            contours = np.frombuffer(contours_bytes, dtype=np.int32).reshape(-1, 4)

            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
           
            for (x, y, w, h) in contours:
                roi = frame[y:y+h, x:x+w]
                blurred_roi = cv2.GaussianBlur(roi, (15, 15), 0)
                frame[y:y+h, x:x+w] = blurred_roi

                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            cv2.putText(frame, current_time, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
            cv2.imshow('Presenter', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                logging.info("Exit requested by user.")
                break

    except Exception as e:
        logging.error(f"An error occurred: {e}")

    finally:
        cv2.destroyAllWindows()
        logging.info("Presenter finished.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Present video frames with detected motion contours.")
    parser.add_argument('presenter_address', type=str, help="Address of the presenter.")
    args = parser.parse_args()

    presenter(args.presenter_address)
