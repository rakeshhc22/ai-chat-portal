"""
Django REST Framework Views for AI Chat Portal API
Handles conversation management, messaging, and AI integration
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
import logging

from .models import Conversation, Message, Sentiment, Topic
from .serializers import (
    ConversationListSerializer,
    ConversationDetailSerializer,
    ConversationCreateSerializer,
    ConversationUpdateSerializer,
    MessageSerializer,
    MessageCreateSerializer,
    MessageUpdateSerializer,
    SentimentSerializer,
    TopicSerializer
)

logger = logging.getLogger(__name__)


# ==================== CONVERSATION VIEWSET ====================

class ConversationViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Conversations
    Supports: GET (list/retrieve), POST (create), PUT/PATCH (update), DELETE
    """
    
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'is_pinned', 'is_archived']
    search_fields = ['title', 'summary']
    ordering = ['-updated_at']
    
    def get_queryset(self):
        """Get all conversations"""
        return Conversation.objects.all()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return ConversationCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ConversationUpdateSerializer
        elif self.action == 'list':
            return ConversationListSerializer
        return ConversationDetailSerializer
    
    def create(self, request, *args, **kwargs):
        """Handle POST requests to create conversations"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f'Error creating conversation: {str(e)}')
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def perform_create(self, serializer):
        """Save conversation"""
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message to conversation and get AI response"""
        try:
            # Get conversation
            conversation = self.get_object()
            user_message_content = request.data.get('content', '').strip()
            
            if not user_message_content:
                return Response(
                    {'error': 'Message content cannot be empty'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # ✅ STEP 1: Save user message
            user_message = Message.objects.create(
                conversation=conversation,
                content=user_message_content,
                sender='user'
            )
            logger.info(f'✅ Created user message: {user_message.id}')
            
            # ✅ STEP 2: Try to get AI response
            ai_message = None
            try:
                from conversations.services.ai_service import LMStudioService
                
                # Initialize AI service
                ai_service = LMStudioService(api_url="http://192.168.229.1:1234")
                
                # Build context from previous messages (only last 3)
                previous_messages = conversation.messages.exclude(
                    id=user_message.id
                ).order_by('created_at')[:3]
                
                messages_context = []
                
                # Add previous messages to context
                for msg in previous_messages:
                    messages_context.append({
                        'role': 'user' if msg.sender == 'user' else 'assistant',
                        'content': msg.content
                    })
                
                # Add current user message
                messages_context.append({
                    'role': 'user',
                    'content': user_message_content
                })
                
                logger.info(f'📤 Sending {len(messages_context)} messages to AI')
                
                # Get AI response
                ai_response_text = ai_service.chat(messages_context)
                
                # Save AI message
                ai_message = Message.objects.create(
                    conversation=conversation,
                    content=ai_response_text,
                    sender='ai',
                    status='completed'
                )
                logger.info(f'✅ Created AI message: {ai_message.id}')
                
            except Exception as ai_error:
                logger.error(f'❌ AI Service error: {str(ai_error)}', exc_info=True)
                # Create error message
                ai_message = Message.objects.create(
                    conversation=conversation,
                    content=f"I'm having trouble responding right now. Error: {str(ai_error)}",
                    sender='ai',
                    status='error'
                )
            
            # ✅ STEP 3: Update conversation timestamp
            conversation.last_message_at = timezone.now()
            conversation.save()
            
            # ✅ STEP 4: Return response
            response_data = {
                'user_message': MessageSerializer(user_message).data,
                'conversation_id': conversation.id
            }
            
            if ai_message:
                response_data['ai_message'] = MessageSerializer(ai_message).data
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f'❌ Send message error: {str(e)}', exc_info=True)
            return Response(
                {'error': f'Error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def end_conversation(self, request, pk=None):
        """End conversation"""
        try:
            conversation = self.get_object()
            conversation.status = 'archived'
            conversation.is_archived = True
            conversation.save()
            return Response(ConversationDetailSerializer(conversation).data)
        except Exception as e:
            logger.error(f'Error ending conversation: {str(e)}')
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get conversation analytics"""
        try:
            conversation = self.get_object()
            return Response({
                'total_messages': conversation.messages.count(),
                'average_sentiment': float(conversation.average_sentiment or 0.0)
            })
        except Exception as e:
            logger.error(f'Error getting analytics: {str(e)}')
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ==================== MESSAGE VIEWSET ====================

class MessageViewSet(viewsets.ModelViewSet):
    """API ViewSet for Messages"""
    
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['conversation', 'sender']
    search_fields = ['content']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get all messages"""
        return Message.objects.all()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return MessageCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return MessageUpdateSerializer
        return MessageSerializer


# ==================== SENTIMENT VIEWSET ====================

class SentimentViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for Sentiment (read-only)"""
    
    serializer_class = SentimentSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['conversation']
    ordering = ['-analyzed_at']
    
    def get_queryset(self):
        """Get all sentiments"""
        return Sentiment.objects.all()


# ==================== TOPIC VIEWSET ====================

class TopicViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for Topic (read-only)"""
    
    serializer_class = TopicSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['primary_topic']
    ordering = ['-analyzed_at']
    
    def get_queryset(self):
        """Get all topics"""
        return Topic.objects.all()
