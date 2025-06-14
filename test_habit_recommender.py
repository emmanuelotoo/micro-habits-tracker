import unittest
from habit_recommender import HabitRecommender
from firebase_service import FirebaseService
from unittest.mock import Mock, patch


class TestHabitRecommender(unittest.TestCase):
    """Test cases for the HabitRecommender class."""
    
    def setUp(self):
        """Set up a recommender instance for each test."""
        self.recommender = HabitRecommender()
    
    def test_input_validation(self):
        """Test that invalid inputs raise appropriate exceptions."""
        # Invalid mood
        with self.assertRaises(ValueError):
            self.recommender.get_habit_suggestion('Invalid', 100, ['Relaxation'])
        
        # Invalid screen time
        with self.assertRaises(ValueError):
            self.recommender.get_habit_suggestion('Happy', -10, ['Relaxation'])
        
        # Invalid preferences type
        with self.assertRaises(ValueError):
            self.recommender.get_habit_suggestion('Happy', 100, 'Not a list')
    
    def test_stressed_mood_with_relaxation_preference(self):
        """Test that stressed mood with relaxation preference gives appropriate suggestions."""
        suggestion = self.recommender.get_habit_suggestion('Stressed', 200, ['Relaxation'])
        self.assertIn(suggestion, self.recommender.habits['relaxation'])
    
    def test_tired_mood_with_physical_activity(self):
        """Test that tired mood with physical activity preference gives light activities."""
        suggestion = self.recommender.get_habit_suggestion('Tired', 200, ['Physical activity'])
        # Should suggest light physical activity or stretching
        self.assertTrue('light' in suggestion.lower() or 'stretching' in suggestion.lower())
    
    def test_happy_mood_with_productivity(self):
        """Test that happy mood with productivity preference gives productivity suggestions."""
        suggestion = self.recommender.get_habit_suggestion('Happy', 200, ['Productivity'])
        self.assertIn(suggestion, self.recommender.habits['productivity'])
    
    def test_high_screen_time(self):
        """Test that high screen time suggests non-screen activities."""
        suggestion = self.recommender.get_habit_suggestion('Neutral', 300, ['Productivity'])
        # Should suggest physical activity or journaling
        physical_activities = set(self.recommender.habits['physical_activity'])
        journaling_activities = [h for h in self.recommender.habits['mindfulness'] 
                               if 'journal' in h.lower()]
        
        self.assertTrue(suggestion in physical_activities or suggestion in journaling_activities)
    
    def test_low_screen_time(self):
        """Test that low screen time suggests productive activities."""
        suggestion = self.recommender.get_habit_suggestion('Neutral', 100, ['Relaxation'])
        self.assertIn(suggestion, self.recommender.habits['productivity'])
    
    def test_no_matching_preferences(self):
        """Test that when no preferences match, general habits are suggested."""
        # Create a case where no preferences will match the mood rules
        suggestion = self.recommender.get_habit_suggestion('Stressed', 200, ['Productivity'])
        # Should fall back to general habits
        self.assertIn(suggestion, self.recommender.habits['general'])
    
    def test_to_json_output(self):
        """Test that the to_json method produces valid JSON with the expected structure."""
        import json
        
        # Get JSON output
        json_str = self.recommender.to_json('Happy', 100, ['Productivity'])
        
        # Parse the JSON
        result = json.loads(json_str)
        
        # Check structure
        self.assertEqual(result['mood'], 'Happy')
        self.assertEqual(result['screen_time_minutes'], 100)
        self.assertEqual(result['preferences'], ['Productivity'])
        self.assertIsInstance(result['suggested_habit'], str)


@pytest.fixture
def recommender():
    return HabitRecommender()

@pytest.fixture
def mock_firebase():
    return Mock(spec=FirebaseService)

def test_valid_mood_validation(recommender):
    """Test that valid moods are accepted."""
    valid_moods = ['happy', 'stressed', 'tired', 'neutral', 'anxious', 'energetic']
    for mood in valid_moods:
        suggestion = recommender.get_habit_suggestion(
            'test_user', mood, 120, ['physical_activity'], store_in_firebase=False
        )
        assert suggestion['mood'] == mood

def test_invalid_mood_validation(recommender):
    """Test that invalid moods raise ValueError."""
    with pytest.raises(ValueError):
        recommender.get_habit_suggestion(
            'test_user', 'invalid_mood', 120, ['physical_activity']
        )

def test_screen_time_rules(recommender):
    """Test that screen time rules are applied correctly."""
    # Test high screen time
    high_screen_time = recommender.get_habit_suggestion(
        'test_user', 'neutral', 360, ['physical_activity'], store_in_firebase=False
    )
    assert 'suggested_habit' in high_screen_time
    
    # Test low screen time
    low_screen_time = recommender.get_habit_suggestion(
        'test_user', 'neutral', 60, ['productivity'], store_in_firebase=False
    )
    assert 'suggested_habit' in low_screen_time

def test_mood_based_rules(recommender):
    """Test that mood-based rules are applied correctly."""
    # Test stressed mood
    stressed = recommender.get_habit_suggestion(
        'test_user', 'stressed', 120, ['relaxation', 'mindfulness'], 
        store_in_firebase=False
    )
    assert 'suggested_habit' in stressed
    
    # Test tired mood
    tired = recommender.get_habit_suggestion(
        'test_user', 'tired', 120, ['physical_activity'], 
        store_in_firebase=False
    )
    assert 'suggested_habit' in tired

def test_firebase_integration(mock_firebase):
    """Test Firebase integration."""
    recommender = HabitRecommender(firebase_service=mock_firebase)
    
    # Test storing suggestion
    suggestion = recommender.get_habit_suggestion(
        'test_user', 'happy', 120, ['productivity']
    )
    
    # Verify Firebase service was called
    mock_firebase.store_habit_suggestion.assert_called_once()
    assert 'suggestion_id' in suggestion

def test_json_output(recommender):
    """Test JSON output format."""
    json_output = recommender.to_json(
        'test_user', 'happy', 120, ['productivity']
    )
    
    # Verify JSON structure
    import json
    data = json.loads(json_output)
    assert 'mood' in data
    assert 'screen_time_minutes' in data
    assert 'preferences' in data
    assert 'suggested_habit' in data

def test_preference_validation(recommender):
    """Test that preferences are properly validated and processed."""
    # Test with valid preferences
    suggestion = recommender.get_habit_suggestion(
        'test_user', 'neutral', 120, 
        ['Physical Activity', 'Mindfulness'], 
        store_in_firebase=False
    )
    assert 'suggested_habit' in suggestion
    
    # Test with empty preferences
    suggestion = recommender.get_habit_suggestion(
        'test_user', 'neutral', 120, [], 
        store_in_firebase=False
    )
    assert 'suggested_habit' in suggestion
    assert suggestion['suggested_habit'] in recommender.habits['general']


if __name__ == '__main__':
    unittest.main()