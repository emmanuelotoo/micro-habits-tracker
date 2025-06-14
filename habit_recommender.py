import random
import json
from typing import List, Dict, Optional, Union
from datetime import datetime

# Try to import Firebase, but make it optional
try:
    from firebase_service import FirebaseService
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    # Create a dummy FirebaseService type for type hinting
    class FirebaseService:
        pass


class HabitRecommender:
    """A recommendation engine for suggesting micro-habits based on user data.
    
    This class implements a rule-based system to suggest personalized micro-habits
    based on a user's mood, screen time, and preferences.
    """
    
    def __init__(self, firebase_service: Optional[FirebaseService] = None):
        """Initialize the habit recommender with predefined habit categories.
        
        Args:
            firebase_service: Optional Firebase service instance for persistence
        """
        self.firebase_service = firebase_service
        self.habits = {
            'relaxation': [
                'Listen to calming music for 5 minutes',
                'Take a 5-minute breathing break',
                'Practice progressive muscle relaxation',
                'Do a quick guided meditation',
                'Take a mindful tea break'
            ],
            'mindfulness': [
                'Do a 5-minute meditation session',
                'Practice mindful breathing for 3 minutes',
                'Journal 3 things you\'re grateful for',
                'Do a body scan meditation',
                'Practice mindful walking for 5 minutes'
            ],
            'physical_activity': [
                'Go for a short 10-minute walk',
                'Do 5 minutes of stretching',
                'Do 10 jumping jacks',
                'Take the stairs instead of elevator',
                'Do a quick yoga flow'
            ],
            'productivity': [
                'Tidy your workspace',
                'Read a book for 10 minutes',
                'Write down your top 3 priorities',
                'Organize your digital files',
                'Learn something new for 10 minutes'
            ],
            'social': [
                'Send a message to a friend',
                'Call a family member',
                'Write a thank you note',
                'Compliment someone',
                'Reach out to an old friend'
            ],
            'creative': [
                'Doodle or sketch for 5 minutes',
                'Write a short poem or haiku',
                'Take 3 interesting photos',
                'Brainstorm ideas for a project',
                'Listen to a new genre of music'
            ],
            'digital_wellbeing': [
                'Turn off notifications for 30 minutes',
                'Do a quick digital declutter',
                'Take a short screen break',
                'Adjust your screen brightness',
                'Set app time limits'
            ],
            'nature': [
                'Step outside for fresh air',
                'Water your plants',
                'Look at the sky for a few minutes',
                'Listen to nature sounds',
                'Open a window for fresh air'
            ]
        }
        
        # Define valid moods
        self.valid_moods = [
            'stressed', 'anxious', 'overwhelmed',
            'tired', 'fatigued', 'exhausted',
            'happy', 'excited', 'motivated',
            'bored', 'understimulated', 'restless',
            'sad', 'down', 'depressed',
            'angry', 'frustrated', 'irritated'
        ]
        
        # Define mood categories for rule application
        self.mood_categories = {
            'stressed_anxious': ['stressed', 'anxious', 'overwhelmed'],
            'tired_fatigued': ['tired', 'fatigued', 'exhausted'],
            'happy_excited': ['happy', 'excited', 'motivated'],
            'understimulated': ['bored', 'understimulated', 'restless'],
            'negative': ['sad', 'down', 'depressed', 'angry', 'frustrated', 'irritated']
        }
        
        # Define valid preferences with display names
        self.valid_preferences = [
            'relaxation', 'mindfulness', 'physical_activity', 'productivity',
            'social', 'creative', 'digital_wellbeing', 'nature'
        ]
        
        # Map internal preference names to display names
        self.preference_display_names = {
            'relaxation': 'Relaxation',
            'mindfulness': 'Mindfulness',
            'physical_activity': 'Physical Activity',
            'productivity': 'Productivity',
            'social': 'Social',
            'creative': 'Creative',
            'digital_wellbeing': 'Digital Wellbeing',
            'nature': 'Nature'
        }
        
        # Define mood-preference affinity matrix
        self.mood_preference_affinity = {
            'stressed_anxious': ['relaxation', 'mindfulness', 'nature'],
            'tired_fatigued': ['physical_activity', 'nature', 'social'],
            'happy_excited': ['productivity', 'creative', 'social'],
            'understimulated': ['creative', 'physical_activity', 'productivity'],
            'negative': ['mindfulness', 'social', 'nature']
        }
    
    def get_habit_suggestion(self, mood: str, screen_time_minutes: int, 
                           preferences: List[str]) -> Dict[str, Union[str, List[str]]]:
        """Get a personalized habit suggestion based on user data.
        
        Args:
            mood: The user's current mood
            screen_time_minutes: Minutes of screen time today
            preferences: List of user's habit preferences
            
        Returns:
            Dictionary with suggested habit and metadata
        """
        # Validate inputs
        self._validate_inputs(mood, screen_time_minutes, preferences)
        
        # Normalize preferences to internal format
        normalized_preferences = self._normalize_preferences(preferences)
        
        # Determine mood category
        mood_category = None
        for category, moods in self.mood_categories.items():
            if mood.lower() in moods:
                mood_category = category
                break
        
        # Apply screen time rules
        filtered_habits = self._apply_screen_time_rules(screen_time_minutes)
        
        # Apply mood-based rules
        filtered_habits = self._apply_mood_rules(mood_category, filtered_habits, normalized_preferences)
        
        # Select a habit using weighted random selection
        selected_habit = self._weighted_random_selection(filtered_habits)
        
        # Generate reasoning for the suggestion
        reasoning = self._generate_reasoning(mood, mood_category, screen_time_minutes, normalized_preferences, selected_habit)
        
        # Create result dictionary
        result = {
            'habit': selected_habit,
            'mood': mood,
            'mood_category': mood_category,
            'screen_time_minutes': screen_time_minutes,
            'preferences': preferences,  # Keep original preferences for display
            'timestamp': datetime.now().isoformat(),
            'reasoning': reasoning
        }
        
        # Store in Firebase if available
        if self.firebase_service and FIREBASE_AVAILABLE:
            # Implementation would go here
            pass
        
        return result
    
    def _validate_inputs(self, mood: str, screen_time_minutes: int, preferences: List[str]) -> None:
        """Validate user inputs.
        
        Args:
            mood: The user's current mood
            screen_time_minutes: Minutes of screen time today
            preferences: List of user's habit preferences
            
        Raises:
            ValueError: If any inputs are invalid
        """
        # Validate mood
        if mood.lower() not in self.valid_moods:
            raise ValueError(f"Invalid mood: {mood}. Valid moods are: {', '.join(self.valid_moods)}")
        
        # Validate screen time
        if not isinstance(screen_time_minutes, (int, float)) or screen_time_minutes < 0:
            raise ValueError("Screen time must be a positive number of minutes")
        
        # Validate preferences
        normalized_preferences = self._normalize_preferences(preferences)
        for pref in normalized_preferences:
            if pref not in self.valid_preferences:
                raise ValueError(f"Invalid preference: {pref}. Valid preferences are: {', '.join(self.valid_preferences)}")
    
    def _normalize_preferences(self, preferences: List[str]) -> List[str]:
        """Normalize preference names to internal format.
        
        Args:
            preferences: List of user's habit preferences (can be display names or internal names)
            
        Returns:
            List of normalized preference names
        """
        normalized = []
        
        # Create a reverse mapping from display names to internal names
        display_to_internal = {v.lower(): k for k, v in self.preference_display_names.items()}
        
        for pref in preferences:
            pref_lower = pref.lower()
            # Check if it's a display name
            if pref_lower in display_to_internal:
                normalized.append(display_to_internal[pref_lower])
            # Check if it's already an internal name
            elif pref_lower in self.valid_preferences:
                normalized.append(pref_lower)
            else:
                # Keep original for error reporting in validation
                normalized.append(pref)
        
        return normalized
    
    def _apply_screen_time_rules(self, screen_time_minutes: int) -> Dict[str, List[str]]:
        """Apply rules based on screen time.
        
        Args:
            screen_time_minutes: Minutes of screen time today
            
        Returns:
            Filtered habits dictionary
        """
        # Start with all habits
        filtered_habits = self.habits.copy()
        
        # Apply screen time rules
        if screen_time_minutes > 240:  # 4+ hours
            # Prioritize digital wellbeing and physical activity
            for category in ['digital_wellbeing', 'physical_activity', 'nature']:
                # Double these options - multiply by 2 (integer)
                filtered_habits[category] = filtered_habits.get(category, []) * 2
        elif screen_time_minutes > 120:  # 2-4 hours
            # Slightly prioritize digital breaks
            for category in ['digital_wellbeing']:
                # Increase these options - can't use 1.5, so use 2 instead
                filtered_habits[category] = filtered_habits.get(category, []) * 2
        
        return filtered_habits
    
    def _apply_mood_rules(self, mood_category: str, filtered_habits: Dict[str, List[str]], 
                         preferences: List[str]) -> Dict[str, List[str]]:
        """Apply rules based on mood and preferences.
        
        Args:
            mood_category: The category of the user's mood
            filtered_habits: Pre-filtered habits dictionary
            preferences: List of user's habit preferences
            
        Returns:
            Further filtered habits dictionary
        """
        result_habits = {}
        
        # If we have preferences, prioritize those categories
        if preferences:
            # First, include preferred categories with higher weight
            for pref in preferences:
                if pref in filtered_habits:
                    result_habits[pref] = filtered_habits[pref] * 2  # Double weight for preferences
            
            # If the mood category has affinity with certain preferences, boost those further
            if mood_category in self.mood_preference_affinity:
                affinity_prefs = self.mood_preference_affinity[mood_category]
                for pref in affinity_prefs:
                    if pref in preferences and pref in result_habits:
                        # Triple weight for preferences with mood affinity
                        result_habits[pref] = filtered_habits[pref] * 3
        
        # If no matching preferences or no preferences specified, use mood-based defaults
        if not result_habits:
            if mood_category in self.mood_preference_affinity:
                affinity_prefs = self.mood_preference_affinity[mood_category]
                for pref in affinity_prefs:
                    if pref in filtered_habits:
                        # Higher weight for mood affinity - use 2 instead of 1.5
                        result_habits[pref] = filtered_habits[pref] * 2
        
        # If still no habits, fall back to all habits
        if not result_habits:
            return filtered_habits
        
        return result_habits
    
    def _weighted_random_selection(self, filtered_habits: Dict[str, List[str]]) -> str:
        """Select a habit using weighted random selection.
        
        Args:
            filtered_habits: Filtered habits dictionary with weights applied
            
        Returns:
            Selected habit string
        """
        # Flatten the dictionary into a list of habits
        all_habits = []
        for category_habits in filtered_habits.values():
            all_habits.extend(category_habits)
        
        # If no habits, return a default message
        if not all_habits:
            return "Take a 5-minute break and reflect on your day"
        
        # Select a random habit
        return random.choice(all_habits)
    
    def to_json(self, mood: str, screen_time_minutes: int, preferences: List[str]) -> str:
        """Get a habit suggestion as a JSON string.
        
        Args:
            mood: The user's current mood
            screen_time_minutes: Minutes of screen time today
            preferences: List of user's habit preferences
            
        Returns:
            JSON string with suggestion data
        """
        result = self.get_habit_suggestion(mood, screen_time_minutes, preferences)
        return json.dumps(result, indent=2)
    
    def _generate_reasoning(self, mood: str, mood_category: str, 
                          screen_time_minutes: int, preferences: List[str], 
                          selected_habit: str) -> str:
        """Generate reasoning for the habit suggestion.
        
        Args:
            mood: The user's current mood
            mood_category: The category of the user's mood
            screen_time_minutes: Minutes of screen time today
            preferences: List of user's normalized habit preferences
            selected_habit: The selected habit
            
        Returns:
            String explaining the reasoning behind the suggestion
        """
        reasons = []
        
        # Mood-based reasoning
        if mood_category == 'stressed_anxious':
            reasons.append(f"When you're feeling {mood}, activities that promote relaxation and mindfulness can help reduce stress.")
        elif mood_category == 'tired_fatigued':
            reasons.append(f"When you're feeling {mood}, light physical activity can actually boost your energy levels.")
        elif mood_category == 'happy_excited':
            reasons.append(f"When you're feeling {mood}, channeling that positive energy into productive or creative tasks can be fulfilling.")
        elif mood_category == 'understimulated':
            reasons.append(f"When you're feeling {mood}, engaging in stimulating activities can help increase your motivation.")
        elif mood_category == 'negative':
            reasons.append(f"When you're feeling {mood}, mindful activities and social connection can help improve your mood.")
        
        # Screen time reasoning
        if screen_time_minutes > 240:
            reasons.append("Your screen time is quite high today, so taking a break from devices could be beneficial.")
        elif screen_time_minutes > 120:
            reasons.append("You've had a moderate amount of screen time today, so a short break might be refreshing.")
        
        # Preference reasoning
        if preferences:
            # Convert internal preference names to display names for output
            display_prefs = [self.preference_display_names.get(p, p.capitalize()) for p in preferences]
            reasons.append(f"This suggestion aligns with your preference for {' and '.join(display_prefs)}.")
        
        # Combine reasons
        return " ".join(reasons)


# Example usage
if __name__ == "__main__":
    recommender = HabitRecommender()
    
    # Example 1: Stressed user with high screen time
    result = recommender.get_habit_suggestion("Stressed", 310, ["Relaxation", "Mindfulness"])
    print("\nExample 1: Stressed user with high screen time")
    print(recommender.to_json("Stressed", 310, ["Relaxation", "Mindfulness"]))
    
    # Example 2: Happy user with moderate screen time
    print("\nExample 2: Happy user with moderate screen time")
    print(recommender.to_json("Happy", 150, ["Productivity", "Creative"]))
    
    # Example 3: Tired user with low screen time
    print("\nExample 3: Tired user with low screen time")
    print(recommender.to_json("Tired", 45, ["Physical Activity", "Nature"]))
    
    # Example 4: Bored user with high screen time
    print("\nExample 4: Bored user with high screen time")
    print(recommender.to_json("Bored", 280, ["Creative", "Social"]))
    
    # Example 5: Sad user with no preferences
    print("\nExample 5: Sad user with no preferences")
    print(recommender.to_json("Sad", 120, []))