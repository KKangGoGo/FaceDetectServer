from retinaface import RetinaFace


def detect_face(img):
    return RetinaFace.detect_faces(img)


def extract_face(img):
    return RetinaFace.extract_faces(img)
