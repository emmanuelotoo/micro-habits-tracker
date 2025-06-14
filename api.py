from flask import Flask, request, jsonify
from habit_recommender import HabitRecommender

app = Flask(__name__)
recommender = HabitRecommender()

@app.route('/')
def home():
    """Home page with basic instructions."""
    return """
    <h1>Micro-Habits Tracker API</h1>
    <p>Use the /recommend endpoint with a POST request containing:</p>
    <pre>
    {
        "mood": "Stressed",
        "screen_time_minutes": 310,
        "preferences": ["Relaxation", "Mindfulness"]
    }
    </pre>
    """

@app.route('/recommend', methods=['POST'])
def recommend():
    """Generate a habit recommendation based on the provided user data."""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['mood', 'screen_time_minutes', 'preferences']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Extract data
        mood = data['mood']
        screen_time = data['screen_time_minutes']
        preferences = data['preferences']
        
        # Get recommendation
        suggestion = recommender.get_habit_suggestion(mood, screen_time, preferences)
        
        # Return result
        return jsonify({
            'mood': mood,
            'screen_time_minutes': screen_time,
            'preferences': preferences,
            'suggested_habit': suggestion
        })
    
    except ValueError as e:
        # Handle validation errors
        return jsonify({
            'error': str(e)
        }), 400
    
    except Exception as e:
        # Handle unexpected errors
        return jsonify({
            'error': f'An unexpected error occurred: {str(e)}'
        }), 500

@app.route('/moods', methods=['GET'])
def get_moods():
    """Return the list of valid moods."""
    return jsonify({
        'moods': recommender.valid_moods
    })

@app.route('/preferences', methods=['GET'])
def get_preferences():
    """Return the list of valid preferences."""
    return jsonify({
        'preferences': recommender.valid_preferences
    })

@app.route('/habits', methods=['GET'])
def get_habits():
    """Return all available habits grouped by category."""
    return jsonify({
        'habits': recommender.habits
    })

if __name__ == '__main__':
    app.run(debug=True)