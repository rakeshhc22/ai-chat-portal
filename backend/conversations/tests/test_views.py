"""
Test suite for API Views
Tests all API endpoints and viewset functionality
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase
from rest_framework import status

from conversations.models import Conversation, Message, Sentiment, Topic


# ==================== CONVERSATION VIEWSET TESTS ====================
class ConversationViewSetTest(APITestCase):
    """Test Conversation API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.conversation = Conversation.objects.create(
            user=self.user,
            title='Test Conversation',
            summary='Test summary'
        )
    
    def test_list_conversations(self):
        """Test listing conversations"""
        response = self.client.get('/api/conversations/conversations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_conversation(self):
        """Test creating a conversation"""
        data = {
            'title': 'New Conversation',
            'topic': 'AI'
        }
        response = self.client.post('/api/conversations/conversations/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Conversation.objects.count(), 2)
    
    def test_retrieve_conversation(self):
        """Test retrieving conversation detail"""
        response = self.client.get(
            f'/api/conversations/conversations/{self.conversation.id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Conversation')
    
    def test_update_conversation(self):
        """Test updating conversation"""
        data = {'title': 'Updated Title'}
        response = self.client.patch(
            f'/api/conversations/conversations/{self.conversation.id}/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.conversation.refresh_from_db()
        self.assertEqual(self.conversation.title, 'Updated Title')
    
    def test_delete_conversation(self):
        """Test deleting conversation"""
        response = self.client.delete(
            f'/api/conversations/conversations/{self.conversation.id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Conversation.objects.count(), 0)
    
    def test_conversation_messages_action(self):
        """Test getting conversation messages"""
        Message.objects.create(
            conversation=self.conversation,
            sender='user',
            content='Hello'
        )
        
        response = self.client.get(
            f'/api/conversations/conversations/{self.conversation.id}/messages/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_archive_conversation(self):
        """Test archiving conversation"""
        response = self.client.post(
            f'/api/conversations/conversations/{self.conversation.id}/archive/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.conversation.refresh_from_db()
        self.assertEqual(self.conversation.status, 'archived')
    
    def test_restore_conversation(self):
        """Test restoring archived conversation"""
        self.conversation.status = 'archived'
        self.conversation.save()
        
        response = self.client.post(
            f'/api/conversations/conversations/{self.conversation.id}/restore/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.conversation.refresh_from_db()
        self.assertEqual(self.conversation.status, 'active')
    
    def test_pin_conversation(self):
        """Test pinning conversation"""
        response = self.client.post(
            f'/api/conversations/conversations/{self.conversation.id}/pin/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.conversation.refresh_from_db()
        self.assertTrue(self.conversation.is_pinned)
    
    def test_unpin_conversation(self):
        """Test unpinning conversation"""
        self.conversation.is_pinned = True
        self.conversation.save()
        
        response = self.client.post(
            f'/api/conversations/conversations/{self.conversation.id}/unpin/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.conversation.refresh_from_db()
        self.assertFalse(self.conversation.is_pinned)
    
    def test_statistics_action(self):
        """Test getting conversation statistics"""
        response = self.client.get('/api/conversations/conversations/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total', response.data)
        self.assertIn('active', response.data)
    
    def test_filter_by_status(self):
        """Test filtering conversations by status"""
        Conversation.objects.create(
            user=self.user,
            title='Archived Conv',
            status='archived'
        )
        
        response = self.client.get('/api/conversations/conversations/?status=active')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_search_conversations(self):
        """Test searching conversations"""
        response = self.client.get('/api/conversations/conversations/?search=Test')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_user_isolation(self):
        """Test user can only see own conversations"""
        other_user = User.objects.create_user(username='otheruser')
        Conversation.objects.create(
            user=other_user,
            title='Other User Conv'
        )
        
        response = self.client.get('/api/conversations/conversations/')
        self.assertEqual(len(response.data['results']), 1)


# ==================== MESSAGE VIEWSET TESTS ====================
class MessageViewSetTest(APITestCase):
    """Test Message API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.conversation = Conversation.objects.create(
            user=self.user,
            title='Test'
        )
        
        self.message = Message.objects.create(
            conversation=self.conversation,
            sender='user',
            content='Test message'
        )
    
    def test_list_messages(self):
        """Test listing messages"""
        response = self.client.get('/api/conversations/messages/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_message(self):
        """Test creating message"""
        data = {
            'conversation': self.conversation.id,
            'sender': 'user',
            'content': 'New message'
        }
        response = self.client.post('/api/conversations/messages/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_like_message(self):
        """Test liking message"""
        response = self.client.post(
            f'/api/conversations/messages/{self.message.id}/like/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.message.refresh_from_db()
        self.assertTrue(self.message.is_liked)
    
    def test_dislike_message(self):
        """Test disliking message"""
        response = self.client.post(
            f'/api/conversations/messages/{self.message.id}/dislike/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.message.refresh_from_db()
        self.assertTrue(self.message.is_disliked)
    
    def test_pin_message(self):
        """Test pinning message"""
        response = self.client.post(
            f'/api/conversations/messages/{self.message.id}/pin/'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.message.refresh_from_db()
        self.assertTrue(self.message.is_pinned)


# ==================== ANALYTICS VIEW TESTS ====================
class AnalyticsViewTest(APITestCase):
    """Test Analytics endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.conversation = Conversation.objects.create(
            user=self.user,
            title='Test'
        )
    
    def test_analytics_dashboard(self):
        """Test dashboard analytics"""
        response = self.client.get('/api/conversations/analytics/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_conversations', response.data)
    
    def test_sentiment_trends(self):
        """Test sentiment trends"""
        response = self.client.get('/api/conversations/analytics/sentiment_trends/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_topic_distribution(self):
        """Test topic distribution"""
        response = self.client.get('/api/conversations/analytics/topic_distribution/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


# ==================== AUTHENTICATION TESTS ====================
class AuthenticationTest(APITestCase):
    """Test authentication requirements"""
    
    def test_unauthenticated_request_denied(self):
        """Test unauthenticated requests are denied"""
        response = self.client.get('/api/conversations/conversations/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_authenticated_request_allowed(self):
        """Test authenticated requests are allowed"""
        user = User.objects.create_user(username='testuser')
        self.client.force_authenticate(user=user)
        
        response = self.client.get('/api/conversations/conversations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


# ==================== PERMISSION TESTS ====================
class PermissionTest(APITestCase):
    """Test permission checks"""
    
    def setUp(self):
        """Set up test data"""
        self.user1 = User.objects.create_user(username='user1')
        self.user2 = User.objects.create_user(username='user2')
        
        self.conversation = Conversation.objects.create(
            user=self.user1,
            title='User1 Conv'
        )
    
    def test_user_cannot_access_other_user_conversation(self):
        """Test user cannot access other user's conversations"""
        self.client.force_authenticate(user=self.user2)
        
        response = self.client.get(
            f'/api/conversations/conversations/{self.conversation.id}/'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# ==================== INTEGRATION TESTS ====================
class IntegrationTest(APITestCase):
    """Integration tests for complete workflows"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_conversation_and_add_messages(self):
        """Test workflow: create conversation and add messages"""
        # Create conversation
        conv_data = {
            'title': 'Chat Workflow',
            'topic': 'Testing'
        }
        conv_response = self.client.post(
            '/api/conversations/conversations/',
            conv_data
        )
        self.assertEqual(conv_response.status_code, status.HTTP_201_CREATED)
        conv_id = conv_response.data['id']
        
        # Add user message
        msg_data = {
            'conversation': conv_id,
            'sender': 'user',
            'content': 'Hello'
        }
        msg_response = self.client.post('/api/conversations/messages/', msg_data)
        self.assertEqual(msg_response.status_code, status.HTTP_201_CREATED)
        
        # Add AI response
        ai_msg_data = {
            'conversation': conv_id,
            'sender': 'ai',
            'content': 'Hi there!'
        }
        ai_response = self.client.post('/api/conversations/messages/', ai_msg_data)
        self.assertEqual(ai_response.status_code, status.HTTP_201_CREATED)
        
        # Verify messages
        messages_response = self.client.get(
            f'/api/conversations/conversations/{conv_id}/messages/'
        )
        self.assertEqual(len(messages_response.data), 2)
