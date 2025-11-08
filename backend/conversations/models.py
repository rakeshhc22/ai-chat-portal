"""
Database Models for AI Chat Portal
Handles conversations, messages, sentiment analysis, and topic extraction
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.utils import timezone


# ==================== CONVERSATION MODEL ====================
class Conversation(models.Model):
    """
    Represents a conversation between user and AI
    Stores metadata like title, summary, timestamps, and statistics
    """
    
    # Status choices for conversation
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('deleted', 'Deleted'),
    ]
    
    # Primary Fields
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conversations',
        help_text="User who owns this conversation",
        null=True,  # ✅ ADD THIS
        blank=True   # ✅ ADD THIS
    )
    title = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(1)],
        help_text="Title of the conversation",
        default="Untitled Conversation"
    )
    summary = models.TextField(
        max_length=1000,
        blank=True,
        null=True,
        help_text="AI-generated summary of the conversation"
    )
    
    # Status & Metadata
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        help_text="Current status of conversation"
    )
    is_pinned = models.BooleanField(
        default=False,
        help_text="Whether conversation is pinned to top"
    )
    is_archived = models.BooleanField(
        default=False,
        help_text="Whether conversation is archived"
    )
    
    # Topic & Classification
    topic = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Main topic of conversation (e.g., 'AI', 'Programming')"
    )
    tags = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Comma-separated tags for categorization"
    )
    
    # Statistics
    message_count = models.IntegerField(
        default=0,
        help_text="Total number of messages in conversation"
    )
    average_sentiment = models.FloatField(
        default=0.0,
        help_text="Average sentiment score (-1 to 1)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When conversation was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When conversation was last updated"
    )
    last_message_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Timestamp of last message"
    )
    
    # Settings
    is_public = models.BooleanField(
        default=False,
        help_text="Whether conversation is public/shareable"
    )
    share_token = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        unique=True,
        help_text="Token for sharing conversation"
    )
    
    class Meta:
        ordering = ['-updated_at']  # Newest first
        indexes = [
            models.Index(fields=['user', '-updated_at']),
            models.Index(fields=['status']),
            models.Index(fields=['is_pinned']),
        ]
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"
    
    def __str__(self):
        return f"{self.title} (by {self.user.username})"
    
    def save(self, *args, **kwargs):
        """
        Update is_archived status based on status field
        Generate share token if public but token missing
        """
        if self.status == 'archived':
            self.is_archived = True
        
        if self.is_public and not self.share_token:
            import uuid
            self.share_token = str(uuid.uuid4())[:32]
        
        super().save(*args, **kwargs)
    
    @property
    def is_recent(self):
        """Check if conversation was updated in last 24 hours"""
        from datetime import timedelta
        return self.updated_at >= timezone.now() - timedelta(hours=24)
    
    @property
    def get_messages(self):
        """Get all messages in this conversation"""
        return self.messages.all()
    
    @property
    def get_sentiment_label(self):
        """Get human-readable sentiment label"""
        if self.average_sentiment > 0.3:
            return "positive"
        elif self.average_sentiment < -0.3:
            return "negative"
        return "neutral"


# ==================== MESSAGE MODEL ====================
class Message(models.Model):
    """
    Represents a single message in a conversation
    Can be from user or AI
    Stores content, sentiment, and metadata
    """
    
    # Sender type choices
    SENDER_CHOICES = [
        ('user', 'User'),
        ('ai', 'AI Assistant'),
        ('system', 'System'),
    ]
    
    # Status choices
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]
    
    # Primary Fields
    id = models.AutoField(primary_key=True)
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        help_text="Conversation this message belongs to"
    )
    sender = models.CharField(
        max_length=20,
        choices=SENDER_CHOICES,
        default='user',
        help_text="Who sent this message"
    )
    content = models.TextField(
        validators=[MinLengthValidator(1)],
        help_text="Message content"
    )
    
    # Message Metadata
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='sent',
        help_text="Delivery status of message"
    )
    error_message = models.TextField(
        blank=True,
        null=True,
        help_text="Error details if message failed"
    )
    
    # AI-specific Fields
    model_used = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="AI model used to generate response (for AI messages)"
    )
    response_time_ms = models.IntegerField(
        blank=True,
        null=True,
        help_text="Time taken to generate response (milliseconds)"
    )
    token_count = models.IntegerField(
        blank=True,
        null=True,
        help_text="Number of tokens used"
    )
    
    # Sentiment Analysis
    sentiment_score = models.FloatField(
        default=0.0,
        help_text="Sentiment score (-1.0 to 1.0)"
    )
    sentiment_label = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=[
            ('positive', 'Positive'),
            ('neutral', 'Neutral'),
            ('negative', 'Negative'),
        ],
        help_text="Sentiment classification"
    )
    
    # User Interaction
    is_liked = models.BooleanField(
        default=False,
        help_text="Whether user liked this message"
    )
    is_disliked = models.BooleanField(
        default=False,
        help_text="Whether user disliked this message"
    )
    reaction = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="User reaction emoji/feedback"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When message was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When message was last updated"
    )
    
    # Additional Metadata
    is_pinned = models.BooleanField(
        default=False,
        help_text="Whether message is pinned"
    )
    citations = models.JSONField(
        default=list,
        blank=True,
        help_text="Citations/sources for message"
    )
    
    class Meta:
        ordering = ['created_at']  # Oldest first
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['sender']),
            models.Index(fields=['sentiment_label']),
        ]
        verbose_name = "Message"
        verbose_name_plural = "Messages"
    
    def __str__(self):
        sender_name = self.get_sender_display()
        return f"[{sender_name}] {self.content[:50]}..."
    
    def save(self, *args, **kwargs):
        """
        Auto-update conversation's last_message_at timestamp
        Update message count
        """
        super().save(*args, **kwargs)
        
        # Update parent conversation
        conversation = self.conversation
        conversation.message_count = conversation.messages.count()
        conversation.last_message_at = timezone.now()
        conversation.save(update_fields=['message_count', 'last_message_at'])
    
    @property
    def is_user_message(self):
        """Check if message is from user"""
        return self.sender == 'user'
    
    @property
    def is_ai_message(self):
        """Check if message is from AI"""
        return self.sender == 'ai'
    
    @property
    def get_sentiment_icon(self):
        """Get emoji icon for sentiment"""
        if self.sentiment_label == 'positive':
            return '😊'
        elif self.sentiment_label == 'negative':
            return '😞'
        return '😐'


# ==================== SENTIMENT MODEL (OPTIONAL) ====================
class Sentiment(models.Model):
    """
    Stores sentiment analysis results for messages
    Optional model for detailed sentiment tracking and analytics
    Useful for generating sentiment trends over time
    """
    
    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
        ('mixed', 'Mixed'),
    ]
    
    # Primary Fields
    id = models.AutoField(primary_key=True)
    message = models.OneToOneField(
        Message,
        on_delete=models.CASCADE,
        related_name='sentiment_analysis',
        help_text="Message being analyzed"
    )
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='sentiment_analyses',
        help_text="Parent conversation for analytics"
    )
    
    # Sentiment Scores
    positive_score = models.FloatField(
        default=0.0,
        validators=[MinLengthValidator(0), MaxLengthValidator(1)],
        help_text="Probability of positive sentiment (0.0-1.0)"
    )
    neutral_score = models.FloatField(
        default=0.0,
        validators=[MinLengthValidator(0), MaxLengthValidator(1)],
        help_text="Probability of neutral sentiment (0.0-1.0)"
    )
    negative_score = models.FloatField(
        default=0.0,
        validators=[MinLengthValidator(0), MaxLengthValidator(1)],
        help_text="Probability of negative sentiment (0.0-1.0)"
    )
    
    # Classification
    label = models.CharField(
        max_length=20,
        choices=SENTIMENT_CHOICES,
        help_text="Overall sentiment classification"
    )
    confidence = models.FloatField(
        default=0.0,
        help_text="Confidence score of classification"
    )
    
    # Model Info
    model_used = models.CharField(
        max_length=100,
        default='bert-base-multilingual-uncased',
        help_text="Sentiment analysis model used"
    )
    analysis_version = models.CharField(
        max_length=20,
        default='1.0',
        help_text="Version of sentiment model"
    )
    
    # Detailed Analysis
    emotions = models.JSONField(
        default=dict,
        blank=True,
        help_text="Detected emotions (e.g., joy, anger, fear)"
    )
    key_phrases = models.JSONField(
        default=list,
        blank=True,
        help_text="Key sentiment-bearing phrases"
    )
    
    # Timestamps
    analyzed_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When sentiment analysis was performed"
    )
    
    class Meta:
        ordering = ['-analyzed_at']
        indexes = [
            models.Index(fields=['conversation', 'analyzed_at']),
            models.Index(fields=['label']),
        ]
        verbose_name = "Sentiment Analysis"
        verbose_name_plural = "Sentiment Analyses"
    
    def __str__(self):
        return f"[{self.label.upper()}] {self.message.content[:40]}... (Confidence: {self.confidence:.2f})"
    
    @property
    def is_confident(self):
        """Check if analysis is confident (>0.8)"""
        return self.confidence > 0.8
    
    @property
    def dominant_emotion(self):
        """Get the dominant emotion from emotions dict"""
        if not self.emotions:
            return None
        return max(self.emotions.items(), key=lambda x: x[1])[0]


# ==================== TOPIC MODEL (OPTIONAL) ====================
class Topic(models.Model):
    """
    Stores topic/category information for conversations
    Optional model for topic extraction and categorization
    Useful for conversation organization and analytics
    """
    
    # Primary Fields
    id = models.AutoField(primary_key=True)
    conversation = models.OneToOneField(
        Conversation,
        on_delete=models.CASCADE,
        related_name='topic_analysis',
        help_text="Conversation being analyzed"
    )
    
    # Topic Information
    primary_topic = models.CharField(
        max_length=100,
        help_text="Main topic of conversation"
    )
    secondary_topics = models.JSONField(
        default=list,
        blank=True,
        help_text="List of secondary topics"
    )
    
    # Classification
    category = models.CharField(
        max_length=100,
        help_text="Category classification (e.g., 'Technical', 'General')"
    )
    subcategory = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Subcategory if applicable"
    )
    
    # Keywords & Phrases
    keywords = models.JSONField(
        default=list,
        help_text="List of important keywords"
    )
    entities = models.JSONField(
        default=dict,
        blank=True,
        help_text="Named entities extracted (people, places, organizations)"
    )
    
    # Confidence & Metadata
    confidence_score = models.FloatField(
        default=0.0,
        help_text="Confidence of topic classification (0.0-1.0)"
    )
    model_used = models.CharField(
        max_length=100,
        default='zero-shot-classification',
        help_text="Model used for topic extraction"
    )
    
    # Complexity Metrics
    complexity_score = models.FloatField(
        default=0.0,
        help_text="Complexity of conversation (0.0-1.0)"
    )
    technical_score = models.FloatField(
        default=0.0,
        help_text="How technical the conversation is (0.0-1.0)"
    )
    
    # Timestamps
    analyzed_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When topic analysis was performed"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When topic was last updated"
    )
    
    class Meta:
        ordering = ['-analyzed_at']
        indexes = [
            models.Index(fields=['primary_topic']),
            models.Index(fields=['category']),
        ]
        verbose_name = "Topic Analysis"
        verbose_name_plural = "Topic Analyses"
    
    def __str__(self):
        return f"{self.primary_topic} (Confidence: {self.confidence_score:.2f})"
    
    @property
    def is_technical(self):
        """Check if conversation is technical (>0.6)"""
        return self.technical_score > 0.6
    
    @property
    def is_complex(self):
        """Check if conversation is complex (>0.7)"""
        return self.complexity_score > 0.7
    
    @property
    def all_topics(self):
        """Get all topics including primary and secondary"""
        topics = [self.primary_topic]
        if self.secondary_topics:
            topics.extend(self.secondary_topics)
        return topics


# ==================== SIGNAL HANDLERS (Auto-update) ====================
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Message)
def update_conversation_sentiment(sender, instance, created, **kwargs):
    """
    Signal handler to update conversation sentiment when message is created/updated
    """
    if created and instance.sender == 'user':
        conversation = instance.conversation
        messages = conversation.messages.filter(sender='user').exclude(sentiment_score=0.0)
        
        if messages.exists():
            avg_sentiment = messages.aggregate(
                avg_sentiment=models.Avg('sentiment_score')
            )['avg_sentiment']
            conversation.average_sentiment = avg_sentiment or 0.0
            conversation.save(update_fields=['average_sentiment'])
