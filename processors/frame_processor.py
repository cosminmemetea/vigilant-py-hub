# processors/frame_processor.py
import cv2
import logging

class FrameProcessor:
    def __init__(self, mediapipe_adapter, kpi_manager):
        self.mediapipe_adapter = mediapipe_adapter
        self.kpi_manager = kpi_manager
        logging.debug(f"FrameProcessor initialized with calculators: {[calc.name() for calc in self.kpi_manager.calculators]}")

    def process_frame(self, frame):
        logging.debug(f"Processing frame: {frame.shape}")
        results = {}
        
        # Process the image with MediaPipe
        processed_landmarks = self.mediapipe_adapter.process(frame)
        if processed_landmarks and hasattr(processed_landmarks, 'multi_face_landmarks') and processed_landmarks.multi_face_landmarks:
            logging.debug(f"Landmarks detected: {len(processed_landmarks.multi_face_landmarks[0].landmark)}")
            image_size = (frame.shape[1], frame.shape[0])  # (width, height)
            landmarks = processed_landmarks.multi_face_landmarks[0]  # Take the first face
            
            # Apply each calculator to the original frame
            for calculator in self.kpi_manager.calculators:
                logging.debug(f"Running calculator: {calculator.name()}")
                calc_result = calculator.calculate(landmarks, image_size, frame)
                if isinstance(calc_result, dict):
                    results.update(calc_result)  # For calculators like eyelid_openness
                else:
                    results[calculator.name()] = calc_result
        else:
            logging.warning("No landmarks detected in frame.")
            for calculator in self.kpi_manager.calculators:
                default_value = "None" if calculator.name() != "eyelid_openness" else {"left_eye_openness": 0.0, "right_eye_openness": 0.0}
                results[calculator.name()] = default_value
        
        logging.debug(f"Frame processing results: {results}")
        return results