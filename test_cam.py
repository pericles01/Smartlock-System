try:
    from picamera2 import Picamera2
except ImportError:
    pass
import time
import io
import cv2

def is_raspberrypi():
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except Exception: pass
    return False

def test_rpi_cam():
    picam2 = Picamera2()
    config = picam2.create_still_configuration({"size": (400, 400), "format": "RGB888"})
    picam2.configure(config)
    #picam2.start_preview(Preview.NULL)
    picam2.start(show_preview=False)
    print("Starting Camera")
    while 1:
        #picam2.capture_file(f"demo{i}.jpg")
        #print(f"Saved demo{i}")

        image = picam2.capture_array()
        print(f"Img: {image.shape}")
        qr_detector = cv2.QRCodeDetector()
        data, bbox, _ = qr_detector.detectAndDecode(image)
        detected = False
        if bbox is not None:
            for points_array in bbox:
                if data:
                    print(f"Detected QR Code Data: {data}")
                    color = (0, 255, 0)
                else:
                    color = (0, 0, 255)

                cv2.polylines(image, [points_array.astype(int)], isClosed=True, color=color,
                                thickness=2)
                detected = True
                print("QR Code detected")
        else:
            print("No QR Code detected")
        cv2.imwrite("demo.jpg", image)
        print("saved")
        if detected:
            break
        time.sleep(1)

    picam2.stop_preview()
    picam2.stop()

def test_webcam():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow('frame', gray)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    if is_raspberrypi():
        test_rpi_cam()
    else:
        test_webcam()
