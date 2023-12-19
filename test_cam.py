from picamera2 import Picamera2, Preview
import time
import io
import cv2

def is_raspberrypi():
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except Exception: pass
    return False

rpi = is_raspberrypi()
print(rpi)
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
