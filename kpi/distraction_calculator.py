# kpi/distraction_calculator.py
from kpi.kpi_calculator import KpiCalculator
from kpi.owl_looking_calculator import OwlLookingCalculator
from kpi.lizard_looking_calculator import LizardLookingCalculator
import time

class DistractionCalculator(KpiCalculator):
    def __init__(self):
        self.last_owl_looking = "Center"
        self.last_lizard_looking = "Center"
        self.direction_start_time = time.time()
        self.glance_history = []
        self.long_distraction_threshold = 3.0
        self.short_distraction_window = 6.0
        self.min_glance_duration = 0.5
        self.phone_detection_threshold = 3
    
    def name(self) -> str:
        return "distraction"
    
    def calculate(self, landmarks, image_size, frame=None) -> str:
        owl_looking = OwlLookingCalculator().calculate(landmarks, image_size)
        lizard_looking = LizardLookingCalculator().calculate(landmarks, image_size)
        current_time = time.time()
        
        current_direction = owl_looking if owl_looking != "Center" else lizard_looking
        
        if (owl_looking != self.last_owl_looking or 
            lizard_looking != self.last_lizard_looking):
            duration = current_time - self.direction_start_time
            if duration >= self.min_glance_duration and (self.last_owl_looking != "Center" or self.last_lizard_looking != "Center"):
                self.glance_history.append((self.last_owl_looking, self.last_lizard_looking, duration))
            self.direction_start_time = current_time
            self.last_owl_looking = owl_looking
            self.last_lizard_looking = lizard_looking
        
        if current_direction != "Center":
            distraction_duration = current_time - self.direction_start_time
            if distraction_duration >= self.long_distraction_threshold:
                if owl_looking != "Center" and lizard_looking == "Center":
                    return "Long (Owl)"
                elif lizard_looking != "Center" and owl_looking == "Center":
                    return "Long (Lizard)"
                return "Long (Mixed)"
        
        self.glance_history = [(o, l, t) for o, l, t in self.glance_history 
                              if current_time - (self.direction_start_time - t) <= self.short_distraction_window]
        cumulative_off_road_time = sum(t for o, l, t in self.glance_history if o != "Center" or l != "Center")
        if len(self.glance_history) >= 2 and cumulative_off_road_time >= self.long_distraction_threshold:
            downward_lizard_glances = sum(1 for o, l, _ in self.glance_history if l == "Down" and o == "Center")
            lizard_glances = sum(1 for o, l, _ in self.glance_history if l != "Center" and o == "Center")
            owl_glances = sum(1 for o, _, _ in self.glance_history if o != "Center")
            
            if downward_lizard_glances >= self.phone_detection_threshold:
                return "Phone"
            elif lizard_glances > owl_glances:
                return "Short (Lizard)"
            elif owl_glances > lizard_glances:
                return "Short (Owl)"
            return "Short (Mixed)"
        
        return "None"