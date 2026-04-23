# utils.py
import cv2
import numpy as np
from insightface.app import FaceAnalysis

class FaceRecognitionHandler:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FaceRecognitionHandler, cls).__new__(cls)
            # buffalo_l is the high-accuracy model; use buffalo_s for speed
            cls._instance.app = FaceAnalysis(name='buffalo_s', providers=['CPUExecutionProvider'], allowed_modules=['detection', 'recognition'])
            cls._instance.app.prepare(ctx_id=0, det_size=(224, 224))
        return cls._instance

    def get_embedding(self, image_bytes):
        # Convert bytes to OpenCV image
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        faces = self.app.get(img)
        if not faces:
            return None
        # Return the embedding of the first detected face
        return faces[0].normed_embedding

# it was initialized  in apps.py 
