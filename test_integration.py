import unittest
from habit_recommender import HabitRecommender
from firebase_service import FirebaseService
import os
from datetime import datetime

class TestHabitSystemIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment before running tests"""
        # Initialize Firebase service with test credentials
        cls.firebase_service = FirebaseService()
        cls.recommender = HabitRecommender(firebase_service=cls.firebase_service)
        
        # Test user data
        cls.test_user_id = "test_user_" + datetime.now().strftime("%Y%m%d%H%M%S")
        cls.test_preferences = ["physical_activity", "mindfulness"]
    
    def test_1_habit_suggestion_generation(self):
        """Test if habit suggestions are generated correctly"""
        print("\nTesting habit suggestion generation...")
        
        # Test different moods
        test_cases = [
            {
                "mood": "stressed",
                "screen_time": 240,
                "expected_categories": ["relaxation", "mindfulness"]
            },
            {
                "mood": "tired",
                "screen_time": 60,
                "expected_categories": ["physical_activity"]
            },
            {
                "mood": "happy",
                "screen_time": 120,
                "expected_categories": ["productivity", "physical_activity"]
            }
        ]
        
        for case in test_cases:
            suggestion = self.recommender.get_habit_suggestion(
                self.test_user_id,
                case["mood"],
                case["screen_time"],
                self.test_preferences,
                store_in_firebase=True
            )
            
            print(f"\nTesting mood: {case['mood']}")
            print(f"Screen time: {case['screen_time']} minutes")
            print(f"Generated suggestion: {suggestion['suggested_habit']}")
            
            # Verify suggestion structure
            self.assertIn('suggestion_id', suggestion)
            self.assertIn('suggested_habit', suggestion)
            self.assertIn('mood', suggestion)
            self.assertIn('screen_time_minutes', suggestion)
            
            # Verify suggestion matches mood
            self.assertEqual(suggestion['mood'], case['mood'])
            
            # Verify screen time is stored
            self.assertEqual(suggestion['screen_time_minutes'], case['screen_time'])
    
    def test_2_firebase_storage(self):
        """Test if suggestions are properly stored in Firebase"""
        print("\nTesting Firebase storage...")
        
        # Generate and store a test suggestion
        suggestion = self.recommender.get_habit_suggestion(
            self.test_user_id,
            "neutral",
            120,
            self.test_preferences,
            store_in_firebase=True
        )
        
        # Verify suggestion was stored
        stored_suggestion = self.firebase_service.get_suggestion(
            self.test_user_id,
            suggestion['suggestion_id']
        )
        
        print(f"Stored suggestion: {stored_suggestion}")
        self.assertIsNotNone(stored_suggestion)
        self.assertEqual(stored_suggestion['suggested_habit'], suggestion['suggested_habit'])
    
    def test_3_habit_status_updates(self):
        """Test if habit status updates work correctly"""
        print("\nTesting habit status updates...")
        
        # Generate a test suggestion
        suggestion = self.recommender.get_habit_suggestion(
            self.test_user_id,
            "neutral",
            120,
            self.test_preferences,
            store_in_firebase=True
        )
        
        # Test completing a habit
        self.firebase_service.update_suggestion_status(
            self.test_user_id,
            suggestion['suggestion_id'],
            "completed",
            True
        )
        
        # Verify status update
        updated_suggestion = self.firebase_service.get_suggestion(
            self.test_user_id,
            suggestion['suggestion_id']
        )
        
        print(f"Updated suggestion status: {updated_suggestion['status']}")
        self.assertEqual(updated_suggestion['status'], "completed")
        self.assertTrue(updated_suggestion['completed'])
    
    def test_4_invalid_inputs(self):
        """Test system behavior with invalid inputs"""
        print("\nTesting invalid inputs...")
        
        # Test invalid mood
        with self.assertRaises(ValueError):
            self.recommender.get_habit_suggestion(
                self.test_user_id,
                "invalid_mood",
                120,
                self.test_preferences
            )
        
        # Test invalid screen time
        with self.assertRaises(ValueError):
            self.recommender.get_habit_suggestion(
                self.test_user_id,
                "happy",
                -1,
                self.test_preferences
            )
        
        print("Invalid input tests passed!")

def main():
    # Run the tests
    unittest.main(verbosity=2)

if __name__ == '__main__':
    main() 