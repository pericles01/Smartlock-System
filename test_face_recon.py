from manage.rpi_face_recon import *
import os
import cv2


if __name__ == "__main__":
    print("Training KNN classifier...")
    path = os.path.join(os.getcwd(), ".cache/face_recon")
    save_path = os.path.join(os.getcwd(), ".cache/trained_knn_model.clf")
    classifier = train(path, model_save_path=save_path, n_neighbors=2)
    print("Training complete!")
    # process one frame in every 3 frames for speed
    process_this_frame = 0
    cap = cv2.VideoCapture(0)
    while 1:
        ret, frame = cap.read()
        if ret:
            # Different resizing options can be chosen based on desired program runtime.
            # Image resizing for more stable streaming
            img = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            # process_this_frame = process_this_frame + 1
            # if process_this_frame % 3 == 0:
            predictions = predict(img, model_path=save_path)
            frame = show_prediction_labels_on_image(frame, predictions)
            cv2.imshow('camera', frame)
            if ord('q') == cv2.waitKey(10):
                cap.release()
                cv2.destroyAllWindows()
                exit(0)