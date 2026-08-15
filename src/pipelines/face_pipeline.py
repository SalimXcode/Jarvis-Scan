import dlib
import numpy as np
import cv2
from sklearn.svm import SVC
import streamlit as st
from src.database.db import get_all_students
import os
import urllib.request
import bz2

# Force setuptools fix
try:
    import pkg_resources
except ImportError:
    import setuptools
    import pkg_resources

@st.cache_resource
def load_dlib_models():
    detector = dlib.get_frontal_face_detector()
    
    # Model files download karo
    import urllib.request
    import os
    import bz2
    
    shape_predictor_file = "shape_predictor_68_face_landmarks.dat"
    if not os.path.exists(shape_predictor_file):
        print("Downloading shape predictor model...")
        urllib.request.urlretrieve(
            "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2",
            shape_predictor_file + ".bz2"
        )
        with open(shape_predictor_file + ".bz2", 'rb') as f_in:
            with open(shape_predictor_file, 'wb') as f_out:
                f_out.write(bz2.decompress(f_in.read()))
    
    face_rec_model_file = "dlib_face_recognition_resnet_model_v1.dat"
    if not os.path.exists(face_rec_model_file):
        print("Downloading face recognition model...")
        urllib.request.urlretrieve(
            "http://dlib.net/files/dlib_face_recognition_resnet_model_v1.dat.bz2",
            face_rec_model_file + ".bz2"
        )
        with open(face_rec_model_file + ".bz2", 'rb') as f_in:
            with open(face_rec_model_file, 'wb') as f_out:
                f_out.write(bz2.decompress(f_in.read()))
    
    sp = dlib.shape_predictor(shape_predictor_file)
    facerec = dlib.face_recognition_model_v1(face_rec_model_file)
    return detector, sp, facerec

def get_face_embeddings(image_np):
    detector, sp, facerec = load_dlib_models()
    
    # Convert to RGB if needed
    if len(image_np.shape) == 2:
        rgb = cv2.cvtColor(image_np, cv2.COLOR_GRAY2RGB)
    else:
        rgb = image_np
    
    faces = detector(rgb, 1)
    encodings = []
    
    for face in faces:
        shape = sp(rgb, face)
        face_descriptor = facerec.compute_face_descriptor(rgb, shape, 1)
        encodings.append(np.array(face_descriptor))
    
    return encodings

@st.cache_resource
def get_trained_model():
    x = []
    y = []
    student_db = get_all_students()

    if not student_db:
        return None

    for student in student_db:
        embedding = student.get('face_embedding')
        if embedding:
            x.append(np.array(embedding))
            y.append(student.get('student_id'))

    if len(x) == 0:
        return None

    clf = SVC(kernel="linear", probability=True, class_weight="balanced")
    try:
        clf.fit(x, y)
    except ValueError:
        return None

    return {'clf': clf, 'X': x, "y": y}

def train_classifier():
    st.cache_resource.clear()
    model_data = get_trained_model()
    return bool(model_data)

def predict_attendance(class_image_np):
    encodings = get_face_embeddings(class_image_np)
    detected_students = {}
    model_data = get_trained_model()

    if not model_data:
        return detected_students, [], len(encodings)

    clf = model_data['clf']
    X_train = model_data['X']
    y_train = model_data['y']
    all_students = sorted(list(set(y_train)))

    for encoding in encodings:
        if len(all_students) >= 2:
            predicted_id = int(clf.predict([encoding])[0])
        else:
            predicted_id = int(all_students[0])

        matching_indices = [i for i, sid in enumerate(y_train) if sid == predicted_id]
        if matching_indices:
            student_embeddings = X_train[matching_indices[0]]
            best_match_score = np.linalg.norm(student_embeddings - encoding)
            resemblance_threshold = 0.6
            if best_match_score <= resemblance_threshold:
                detected_students[predicted_id] = True

    return detected_students, all_students, len(encodings)