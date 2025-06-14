from firebase_admin import credentials, firestore, initialize_app
from datetime import datetime
from typing import Dict, Optional

class FirebaseService:
    def __init__(self, credentials_path: str = "serviceAccountKey.json"):
        """Initialize Firebase connection.
        
        Args:
            credentials_path: Path to Firebase service account key file
        """
        try:
            cred = credentials.Certificate(credentials_path)
            initialize_app(cred)
            self.db = firestore.client()
        except Exception as e:
            raise Exception(f"Failed to initialize Firebase: {str(e)}")

    def store_habit_suggestion(self, user_id: str, suggestion_data: Dict) -> str:
        """Store a habit suggestion in Firestore.
        
        Args:
            user_id: Unique identifier for the user
            suggestion_data: Dictionary containing suggestion details
            
        Returns:
            Document ID of the stored suggestion
        """
        try:
            # Add timestamp and status
            suggestion_data.update({
                'created_at': datetime.utcnow(),
                'status': 'pending',
                'completed_at': None
            })
            
            # Store in user's suggestions collection
            doc_ref = self.db.collection('users').document(user_id)\
                .collection('suggestions').document()
            
            doc_ref.set(suggestion_data)
            return doc_ref.id
            
        except Exception as e:
            raise Exception(f"Failed to store suggestion: {str(e)}")

    def update_suggestion_status(self, user_id: str, suggestion_id: str, 
                               status: str, completed: bool = False) -> None:
        """Update the status of a habit suggestion.
        
        Args:
            user_id: Unique identifier for the user
            suggestion_id: ID of the suggestion document
            status: New status ('pending', 'completed', 'skipped')
            completed: Whether the habit was completed
        """
        try:
            doc_ref = self.db.collection('users').document(user_id)\
                .collection('suggestions').document(suggestion_id)
            
            update_data = {
                'status': status,
                'completed_at': datetime.utcnow() if completed else None
            }
            
            doc_ref.update(update_data)
            
        except Exception as e:
            raise Exception(f"Failed to update suggestion status: {str(e)}")

    def get_user_suggestions(self, user_id: str, 
                           limit: int = 10) -> list:
        """Retrieve recent habit suggestions for a user.
        
        Args:
            user_id: Unique identifier for the user
            limit: Maximum number of suggestions to retrieve
            
        Returns:
            List of suggestion documents
        """
        try:
            suggestions_ref = self.db.collection('users').document(user_id)\
                .collection('suggestions')\
                .order_by('created_at', direction=firestore.Query.DESCENDING)\
                .limit(limit)
            
            return [doc.to_dict() for doc in suggestions_ref.stream()]
            
        except Exception as e:
            raise Exception(f"Failed to retrieve suggestions: {str(e)}")

    def get_todays_suggestion(self, user_id: str) -> Optional[Dict]:
        """Get today's habit suggestion for a user.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Today's suggestion document or None if not found
        """
        try:
            today = datetime.utcnow().date()
            
            suggestions_ref = self.db.collection('users').document(user_id)\
                .collection('suggestions')\
                .where('created_at', '>=', datetime.combine(today, datetime.min.time()))\
                .where('created_at', '<=', datetime.combine(today, datetime.max.time()))\
                .limit(1)
            
            docs = list(suggestions_ref.stream())
            return docs[0].to_dict() if docs else None
            
        except Exception as e:
            raise Exception(f"Failed to retrieve today's suggestion: {str(e)}") 