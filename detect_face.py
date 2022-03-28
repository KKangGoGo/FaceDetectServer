from retinaface import RetinaFace


def detect_face(img):
    detect = RetinaFace.detect_faces(img)
    return detect
