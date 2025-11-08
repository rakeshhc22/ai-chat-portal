"""
Django REST Framework Serializers for AI Chat Portal
Converts Django models to/from JSON for API endpoints
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Conversation, Message, Sentiment, Topic


# ==================== USER SERIALIZER ====================

class UserSerializer(serializers.ModelSerializer):
    """Serialize User model for display in conversations"""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


# ==================== MESSAGE SERIALIZERS ====================

class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model - Used for displaying messages"""

    sender_display = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id',
            'conversation',
            'sender',
            'sender_display',
            'content',
            'status',
            'sentiment_score',
            'sentiment_label',
            'is_liked',
            'is_disliked',
            'is_pinned',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'sentiment_score']

    def get_sender_display(self, obj):
        """Get human-readable sender display"""
        sender_map = {
            'user': 'You',
            'ai': 'AI Assistant',
            'system': 'System'
        }
        return sender_map.get(obj.sender, obj.sender)


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new messages"""

    class Meta:
        model = Message
        fields = ['conversation', 'sender', 'content']
        extra_kwargs = {
            'conversation': {'required': True},
            'sender': {'required': True},
            'content': {'required': True, 'min_length': 1}
        }


class MessageUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating message reactions/feedback"""

    class Meta:
        model = Message
        fields = ['is_liked', 'is_disliked', 'is_pinned']


# ==================== SENTIMENT SERIALIZER ====================

class SentimentSerializer(serializers.ModelSerializer):
    """Serializer for Sentiment Analysis"""

    class Meta:
        model = Sentiment
        fields = [
            'id',
            'message',
            'conversation',
            'label',
            'confidence',
            'analyzed_at'
        ]
        read_only_fields = ['id', 'analyzed_at']


# ==================== TOPIC SERIALIZER ====================

class TopicSerializer(serializers.ModelSerializer):
    """Serializer for Topic Analysis"""

    class Meta:
        model = Topic
        fields = [
            'id',
            'conversation',
            'primary_topic',
            'category',
            'keywords',
            'confidence_score',
            'analyzed_at'
        ]
        read_only_fields = ['id', 'analyzed_at']


# ==================== CONVERSATION SERIALIZERS ====================

class ConversationListSerializer(serializers.ModelSerializer):
    """
    Serializer for Conversation list
    Used for displaying conversations in dashboard/list view
    """

    message_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id',
            'title',
            'summary',
            'status',
            'topic',
            'message_count',
            'average_sentiment',
            'is_pinned',
            'is_archived',
            'created_at',
            'updated_at',
            'last_message_at'
        ]
        read_only_fields = [
            'id',
            'message_count',
            'average_sentiment',
            'created_at',
            'updated_at',
            'last_message_at'
        ]

    def get_message_count(self, obj):
        """Get total message count"""
        return obj.messages.count()


class ConversationDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Conversation detail view
    Includes all messages and related data
    """

    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id',
            'title',
            'summary',
            'status',
            'topic',
            'tags',
            'message_count',
            'average_sentiment',
            'is_pinned',
            'is_archived',
            'messages',
            'created_at',
            'updated_at',
            'last_message_at'
        ]
        read_only_fields = [
            'id',
            'average_sentiment',
            'created_at',
            'updated_at',
            'last_message_at',
            'messages'
        ]

    def get_message_count(self, obj):
        """Get total message count"""
        return obj.messages.count()


class ConversationCreateSerializer(serializers.ModelSerializer):
    """
    ✅ FIXED: Serializer for creating new conversations
    - Made all fields optional to accept minimal data
    - Added 'id' to response
    """

    class Meta:
        model = Conversation
        fields = ['id', 'title', 'summary', 'topic', 'tags', 'status']
        read_only_fields = ['id']
        extra_kwargs = {
            'title': {
                'required': False,
                'allow_blank': True,
                'default': 'Untitled Conversation'
            },
            'summary': {'required': False, 'allow_blank': True},
            'topic': {'required': False, 'allow_blank': True},
            'tags': {'required': False, 'allow_null': True},
            'status': {'required': False, 'default': 'active'}
        }

    def create(self, validated_data):
        """Create conversation with sensible defaults"""
        # ✅ Set default title if not provided
        if not validated_data.get('title') or validated_data.get('title') == '':
            validated_data['title'] = 'Untitled Conversation'
        
        # ✅ Set default status
        if not validated_data.get('status'):
            validated_data['status'] = 'active'
        
        # Create and return conversation
        conversation = Conversation.objects.create(**validated_data)
        return conversation


class ConversationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating conversations"""

    class Meta:
        model = Conversation
        fields = [
            'title',
            'summary',
            'status',
            'topic',
            'tags',
            'is_pinned',
            'is_archived'
        ]
        extra_kwargs = {
            'title': {'required': False},
            'summary': {'required': False},
            'status': {'required': False},
            'topic': {'required': False},
            'tags': {'required': False}
        }
