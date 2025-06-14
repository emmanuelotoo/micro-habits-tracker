# AI Developer Implementation Documentation

## Overview
This document explains the implementation of the habit suggestion system, including the AI model, Firebase integration, and Android screen time tracking.

## 1. Habit Suggestion AI Model (`habit_recommender.py`)

### Core Components

#### HabitRecommender Class
The main class that handles habit suggestions based on user data.

```python
class HabitRecommender:
    def __init__(self, firebase_service=None):
        self.firebase_service = firebase_service
        self.habits = {
            'physical_activity': [...],
            'mindfulness': [...],
            'productivity': [...],
            'relaxation': [...],
            'general': [...]
        }
```

### Key Features

1. **Mood-Based Suggestions**
   - Supports 6 moods: happy, stressed, tired, neutral, anxious, energetic
   - Each mood triggers specific habit categories
   - Example: 'stressed' mood prioritizes relaxation and mindfulness habits

2. **Screen Time Analysis**
   - High screen time (>180 minutes): Suggests physical activity
   - Low screen time (<60 minutes): Suggests productivity habits
   - Moderate screen time: Balanced suggestions

3. **Preference-Based Filtering**
   - Filters suggestions based on user preferences
   - Falls back to general habits if no preferences match

### Usage Example
```python
recommender = HabitRecommender(firebase_service)
suggestion = recommender.get_habit_suggestion(
    user_id='user123',
    mood='stressed',
    screen_time_minutes=120,
    preferences=['relaxation', 'mindfulness']
)
```

## 2. Firebase Integration (`firebase_service.py`)

### FirebaseService Class
Handles all Firestore operations for the habit suggestion system.

### Key Features

1. **Suggestion Storage**
   - Stores daily habit suggestions
   - Tracks suggestion status (pending, completed, skipped)
   - Maintains user preferences

2. **Data Structure**
```python
suggestion_data = {
    'user_id': str,
    'mood': str,
    'screen_time_minutes': int,
    'preferences': List[str],
    'suggested_habit': str,
    'timestamp': datetime,
    'status': str,
    'completed': bool
}
```

### Usage Example
```python
firebase_service = FirebaseService()
firebase_service.store_habit_suggestion(suggestion_data)
```

## 3. Android Screen Time Integration (`screen_time_service.dart`)

### ScreenTimeService Class
Flutter service for tracking and analyzing Android screen time.

### Key Features

1. **App Categorization**
   - Social Media: Facebook, Instagram, Twitter, etc.
   - Productivity: Gmail, Office, Google Docs
   - Entertainment: Netflix, Spotify, YouTube

2. **Usage Statistics**
   - Tracks daily screen time by category
   - Calculates total screen time
   - Monitors app-specific usage

3. **Permission Handling**
   - Manages Android usage stats permissions
   - Handles permission requests and validation

### Usage Example
```dart
final screenTimeService = ScreenTimeService();
final categoryTime = await screenTimeService.getScreenTimeByCategory();
```

## 4. Testing (`test_habit_recommender.py`)

Comprehensive test suite covering:
- Mood validation
- Screen time rules
- Firebase integration
- Preference handling
- JSON output format

## Integration Flow

1. **Data Collection**
   - Flutter app collects screen time data
   - User provides mood and preferences

2. **Suggestion Generation**
   - Data sent to Python backend
   - HabitRecommender processes data
   - Generates personalized suggestion

3. **Storage and Tracking**
   - Suggestion stored in Firebase
   - Status tracked over time
   - Completion status updated

## Setup Requirements

1. **Python Dependencies**
   ```
   firebase-admin
   pytest
   ```

2. **Flutter Dependencies**
   ```yaml
   usage_stats: ^1.2.0
   permission_handler: ^10.0.0
   http: ^0.13.0
   ```

3. **Firebase Setup**
   - Service account key required
   - Firestore database initialized
   - Appropriate security rules configured

## Best Practices

1. **Error Handling**
   - All services include comprehensive error handling
   - Graceful fallbacks for missing data
   - Clear error messages for debugging

2. **Data Validation**
   - Input validation for all parameters
   - Type checking and conversion
   - Default values for missing data

3. **Performance**
   - Efficient data processing
   - Minimal API calls
   - Cached where appropriate

## Future Improvements

1. **AI Model Enhancements**
   - Machine learning integration
   - Pattern recognition for better suggestions
   - User feedback incorporation

2. **Screen Time Analysis**
   - More detailed app categorization
   - Usage pattern analysis
   - Custom category support

3. **Integration Features**
   - Real-time updates
   - Push notifications
   - Analytics dashboard

## Support and Maintenance

For any issues or questions, please contact the AI development team. Regular updates and maintenance will be performed to ensure optimal performance and reliability. 