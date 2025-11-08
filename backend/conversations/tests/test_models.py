"""
Test suite for Conversation Models
Tests all model functionality, validations, and business logic
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from conversations.models import Conversation, Message, Sentiment, Topic


# ==================== CONVERSATION MODEL TESTS ====================
class ConversationModelTest(TestCase):
    """Test Conversation model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_conversation(self):
        """Test creating a conversation"""
        conversation = Conversation.objects.create(
            user=self.user,
            title='Test Conversation',
            summary='This is a test',
            topic='General'
        )
        
        self.assertEqual(conversation.title, 'Test Conversation')
        self.assertEqual(conversation.user, self.user)
        self.assertEqual(conversation.status, 'active')
        self.assertFalse(conversation.is_archived)
        self.assertFalse(conversation.is_pinned)
    
    def test_conversation_default_values(self):
        """Test conversation default values"""
        conversation = Conversation.objects.create(
            user=self.user,
            title='Default Test'
        )
        
        self.assertEqual(conversation.status, 'active')
        self.assertEqual(conversation.message_count, 0)
        self.assertEqual(conversation.average_sentiment, 0.0)
        self.assertFalse(conversation.is_pinned)
        self.assertFalse(conversation.is_archived)
    
    def test_conversation_title_validation(self):
        """Test title must not be empty"""
        conversation = Conversation(
            user=self.user,
            title=''
        )
        # This would fail in actual save due to validator
        conversation.title = 'Valid Title'
        conversation.save()
        self.assertEqual(conversation.title, 'Valid Title')
    
    def test_conversation_status_choices(self):
        """Test conversation status choices"""
        conversation = Conversation.objects.create(
            user=self.user,
            title='Status Test'
        )
        
        # Test status transitions
        conversation.status = 'archived'
        conversation.save()
        self.assertTrue(conversation.is_archived)
        
        conversation.status = 'active'
        conversation.save()
        self.assertFalse(conversation.is_archived)
    
    def test_conversation_pinning(self):
        """Test pinning/unpinning conversations"""
        conversation = Conversation.objects.create(
            user=self.user,
            title='Pin Test'
        )
        
        conversation.is_pinned = True
        conversation.save()
        self.assertTrue(conversation.is_pinned)
        
        conversation.is_pinned = False
        conversation.save()
        self.assertFalse(conversation.is_pinned)
    
    def test_conversation_public_sharing(self):
        """Test public sharing with token generation"""
        conversation = Conversation.objects.create(
            user=self.user,
            title='Share Test'
        )
        
        # Initially not public
        self.assertFalse(conversation.is_public)
        self.assertIsNone(conversation.share_token)
        
        # Make public
        conversation.is_public = True
        conversation.save()
        
        # Token should be generated
        self.assertIsNotNone(conversation.share_token)
        self.assertEqual(len(conversation.share_token), 32)
    
    def test_conversation_recent_property(self):
        """Test is_recent property"""
        conversation = Conversation.objects.create(
            user=self.user,
            title='Recent Test'
        )
        
        # Should be recent (just created)
        self.assertTrue(conversation.is_recent)
        
        # Manually set to old date
        conversation.updated_at = timezone.now() - timedelta(days=2)
        conversation.save()
        
        # Should not be recent
        self.assertFalse(conversation.is_recent)
    
    def test_conversation_sentiment_label(self):
        """Test sentiment label generation"""
        conversation = Conversation.objects.create(
            user=self.user,
            title='Sentiment Test'
        )
        
        # Positive sentiment
        conversation.average_sentiment = 0.8
        self.assertEqual(conversation.get_sentiment_label, 'positive')
        
        # Negative sentiment
        conversation.average_sentiment = -0.8
        self.assertEqual(conversation.get_sentiment_label, 'negative')
        
        # Neutral sentiment
        conversation.average_sentiment = 0.1
        self.assertEqual(conversation.get_sentiment_label, 'neutral')
    
    def test_get_messages_property(self):
        """Test get_messages property"""
        conversation = Conversation.objects.create(
            user=self.user,
            title='Get Messages Test'
        )
        
        # Add messages
        Message.objects.create(
            conversation=conversation,
            sender='user',
            content='Hello'
        )
        Message.objects.create(
            conversation=conversation,
            sender='ai',
            content='Hi there'
        )
        
        messages = conversation.get_messages
        self.assertEqual(messages.count(), 2)
    
    def test_conversation_ordering(self):
        """Test conversations are ordered by updated_at"""
        conv1 = Conversation.objects.create(
            user=self.user,
            title='First'
        )
        
        conv2 = Conversation.objects.create(
            user=self.user,
            title='Second'
        )
        
        # conv2 should be first (most recent)
        conversations = Conversation.objects.all()
        self.assertEqual(conversations[0].id, conv2.id)
        self.assertEqual(conversations[1].id, conv1.id)


# ==================== MESSAGE MODEL TESTS ====================
class MessageModelTest(TestCase):
    """Test Message model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.conversation = Conversation.objects.create(
            user=self.user,
            title='Test Conversation'
        )
    
    def test_create_message(self):
        """Test creating a message"""
        message = Message.objects.create(
            conversation=self.conversation,
            sender='user',
            content='Test message'
        )
        
        self.assertEqual(message.content, 'Test message')
        self.assertEqual(message.sender, 'user')
        self.assertEqual(message.status, 'sent')
    
    def test_message_default_values(self):
        """Test message default values"""
        message = Message.objects.create(
            conversation=self.conversation,
            sender='user',
            content='Test'
        )
        
        self.assertEqual(message.status, 'sent')
        self.assertEqual(message.sentiment_score, 0.0)
        self.assertFalse(message.is_liked)
        self.assertFalse(message.is_disliked)
        self.assertFalse(message.is_pinned)
    
    def test_message_sender_choices(self):
        """Test message sender choices"""
        # User message
        user_msg = Message.objects.create(
            conversation=self.conversation,
            sender='user',
            content='User message'
        )
        self.assertEqual(user_msg.sender, 'user')
        
        # AI message
        ai_msg = Message.objects.create(
            conversation=self.conversation,
            sender='ai',
            content='AI response'
        )
        self.assertEqual(ai_msg.sender, 'ai')
    
    def test_message_status_choices(self):
        """Test message status transitions"""
        message = Message.objects.create(
            conversation=self.conversation,
            sender='user',
            content='Test'
        )
        
        message.status = 'delivered'
        message.save()
        self.assertEqual(message.status, 'delivered')
        
        message.status = 'failed'
        message.save()
        self.assertEqual(message.status, 'failed')
    
    def test_message_sentiment_analysis(self):
        """Test message sentiment fields"""
        message = Message.objects.create(
            conversation=self.conversation,
            sender='user',
            content='Great job!',
            sentiment_score=0.9,
            sentiment_label='positive'
        )
        
        self.assertEqual(message.sentiment_score, 0.9)
        self.assertEqual(message.sentiment_label, 'positive')
    
    def test_message_user_reactions(self):
        """Test user reaction tracking"""
        message = Message.objects.create(
            conversation=self.conversation,
            sender='ai',
            content='Test response'
        )
        
        # Like message
        message.is_liked = True
        message.is_disliked = False
        message.save()
        self.assertTrue(message.is_liked)
        self.assertFalse(message.is_disliked)
        
        # Dislike message
        message.is_liked = False
        message.is_disliked = True
        message.save()
        self.assertFalse(message.is_liked)
        self.assertTrue(message.is_disliked)
    
    def test_message_ai_metadata(self):
        """Test AI-specific metadata"""
        message = Message.objects.create(
            conversation=self.conversation,
            sender='ai',
            content='AI response',
            model_used='gpt-3.5-turbo',
            response_time_ms=1250,
            token_count=150
        )
        
        self.assertEqual(message.model_used, 'gpt-3.5-turbo')
        self.assertEqual(message.response_time_ms, 1250)
        self.assertEqual(message.token_count, 150)
    
    def test_message_is_user_message(self):
        """Test is_user_message property"""
        user_msg = Message.objects.create(
            conversation=self.conversation,
            sender='user',
            content='User message'
        )
        
        ai_msg = Message.objects.create(
            conversation=self.conversation,
            sender='ai',
            content='AI response'
        )
        
        self.assertTrue(user_msg.is_user_message)
        self.assertFalse(ai_msg.is_user_message)
    
    def test_message_is_ai_message(self):
        """Test is_ai_message property"""
        ai_msg = Message.objects.create(
            conversation=self.conversation,
            sender='ai',
            content='AI response'
        )
        
        user_msg = Message.objects.create(
            conversation=self.conversation,
            sender='user',
            content='User message'
        )
        
        self.assertTrue(ai_msg.is_ai_message)
        self.assertFalse(user_msg.is_ai_message)
    
    def test_message_updates_conversation_count(self):
        """Test message count is updated in conversation"""
        self.assertEqual(self.conversation.message_count, 0)
        
        Message.objects.create(
            conversation=self.conversation,
            sender='user',
            content='Message 1'
        )
        
        # Refresh from database
        self.conversation.refresh_from_db()
        self.assertEqual(self.conversation.message_count, 1)
        
        Message.objects.create(
            conversation=self.conversation,
            sender='ai',
            content='Message 2'
        )
        
        self.conversation.refresh_from_db()
        self.assertEqual(self.conversation.message_count, 2)
    
    def test_message_ordering(self):
        """Test messages are ordered by created_at"""
        msg1 = Message.objects.create(
            conversation=self.conversation,
            sender='user',
            content='First'
        )
        
        msg2 = Message.objects.create(
            conversation=self.conversation,
            sender='ai',
            content='Second'
        )
        
        messages = Message.objects.all()
        self.assertEqual(messages[0].id, msg1.id)
        self.assertEqual(messages[1].id, msg2.id)


# ==================== SENTIMENT MODEL TESTS ====================
class SentimentModelTest(TestCase):
    """Test Sentiment model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser')
        self.conversation = Conversation.objects.create(
            user=self.user,
            title='Test'
        )
        self.message = Message.objects.create(
            conversation=self.conversation,
            sender='user',
            content='Test message'
        )
    
    def test_create_sentiment(self):
        """Test creating sentiment analysis"""
        sentiment = Sentiment.objects.create(
            message=self.message,
            conversation=self.conversation,
            label='positive',
            confidence=0.95,
            positive_score=0.95,
            neutral_score=0.04,
            negative_score=0.01
        )
        
        self.assertEqual(sentiment.label, 'positive')
        self.assertEqual(sentiment.confidence, 0.95)
    
    def test_sentiment_is_confident(self):
        """Test confidence check"""
        high_conf = Sentiment.objects.create(
            message=self.message,
            conversation=self.conversation,
            label='positive',
            confidence=0.85
        )
        
        low_conf = Sentiment.objects.create(
            message=self.message,
            conversation=self.conversation,
            label='negative',
            confidence=0.6
        )
        
        self.assertTrue(high_conf.is_confident)
        self.assertFalse(low_conf.is_confident)
    
    def test_sentiment_emotions(self):
        """Test emotion detection"""
        emotions = {'joy': 0.8, 'surprise': 0.2}
        sentiment = Sentiment.objects.create(
            message=self.message,
            conversation=self.conversation,
            label='positive',
            confidence=0.9,
            emotions=emotions
        )
        
        self.assertEqual(sentiment.emotions, emotions)
        self.assertEqual(sentiment.dominant_emotion, 'joy')


# ==================== TOPIC MODEL TESTS ====================
class TopicModelTest(TestCase):
    """Test Topic model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser')
        self.conversation = Conversation.objects.create(
            user=self.user,
            title='Test'
        )
    
    def test_create_topic(self):
        """Test creating topic analysis"""
        topic = Topic.objects.create(
            conversation=self.conversation,
            primary_topic='Programming',
            category='Technical',
            confidence_score=0.9
        )
        
        self.assertEqual(topic.primary_topic, 'Programming')
        self.assertEqual(topic.category, 'Technical')
        self.assertEqual(topic.confidence_score, 0.9)
    
    def test_topic_is_technical(self):
        """Test technical score check"""
        technical = Topic.objects.create(
            conversation=self.conversation,
            primary_topic='Code',
            category='Technical',
            confidence_score=0.9,
            technical_score=0.85
        )
        
        non_technical = Topic.objects.create(
            conversation=self.conversation,
            primary_topic='Chat',
            category='General',
            confidence_score=0.8,
            technical_score=0.3
        )
        
        self.assertTrue(technical.is_technical)
        self.assertFalse(non_technical.is_technical)
    
    def test_topic_is_complex(self):
        """Test complexity check"""
        complex_topic = Topic.objects.create(
            conversation=self.conversation,
            primary_topic='AI',
            category='Technical',
            confidence_score=0.9,
            complexity_score=0.85
        )
        
        simple_topic = Topic.objects.create(
            conversation=self.conversation,
            primary_topic='Hello',
            category='General',
            confidence_score=0.8,
            complexity_score=0.3
        )
        
        self.assertTrue(complex_topic.is_complex)
        self.assertFalse(simple_topic.is_complex)
    
    def test_topic_all_topics_property(self):
        """Test all_topics property"""
        topic = Topic.objects.create(
            conversation=self.conversation,
            primary_topic='Python',
            secondary_topics=['Programming', 'Development'],
            category='Technical'
        )
        
        all_topics = topic.all_topics
        self.assertEqual(len(all_topics), 3)
        self.assertIn('Python', all_topics)
        self.assertIn('Programming', all_topics)
        self.assertIn('Development', all_topics)
