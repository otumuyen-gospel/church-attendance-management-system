# utils.py
import os

import cv2
from django_extensions import settings
import numpy as np
from insightface.app import FaceAnalysis

class FaceRecognitionHandler:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FaceRecognitionHandler, cls).__new__(cls)
            # buffalo_l is the high-accuracy model; use buffalo_s for speed
            model_path = os.path.join(settings.BASE_DIR, 'models') 
            cls._instance.app = FaceAnalysis(name='buffalo_s', root=model_path, providers=['CPUExecutionProvider'], allowed_modules=['detection', 'recognition'])
            cls._instance.app.prepare(ctx_id=0, det_size=(224, 224), det_thresh=0.65)
        return cls._instance

    def get_embedding(self, image_bytes):
        # Convert bytes to OpenCV image
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        faces = self.app.get(img)
        if not faces:
            return None
        # Return the embedding of the first detected face
        if self.is_valid_face(faces[0]):
            return faces[0].embedding.tolist()
        return None
    def is_valid_face(self, face):
        # Rule 1: High confidence score
        if face.det_score < 0.6: return False
    
        # Rule 2: Reasonable bounding box size 
        # (Prevents tiny background blobs from being counted)
        bbox = face.bbox
        width = bbox[2] - bbox[0]
        if width < 50: return False
    
        return True
    def check_match(self,probe_vec, master_vec, threshold=0.4):
        # InsightFace vectors are usually normalized; 
        # Dot product = Cosine Similarity
        similarity = np.dot(probe_vec, master_vec)
        return similarity >= threshold, similarity
    def loadCache(self, known_encodings):
        # Build 2D matrix (N rows, 512 cols)
        self.matrix = np.array(known_encodings)
        # Crucial: Matrix must be normalized for dot product to equal cosine similarity
        self.matrix = self.matrix / np.linalg.norm(self.matrix, axis=1, keepdims=True)
    def find_best_match(self, known_encodings, probe_vec):
        self.loadCache(known_encodings)
        probe_vec = probe_vec / np.linalg.norm(probe_vec)
        # Result is an array of N scores
        scores = np.dot(self.matrix, probe_vec)
        best_idx = np.argmax(scores)
        return best_idx, scores[best_idx]

# it was initialized  in apps.py 
