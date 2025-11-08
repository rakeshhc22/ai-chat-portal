"""
Django Admin Configuration for AI Chat Portal
Registers models and customizes admin interface for easy data management
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Conversation, Message, Sentiment, Topic


# ==================== CONVERSATION ADMIN ====================
@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """
    Admin interface for Conversation model
    Displays conversation list with filtering and search capabilities
    """
    
    list_display = (
        'title',
        'user',
        'get_status_badge',
        'message_count',
        'get_sentiment_emoji',
        'is_pinned',
        'created_at'
    )
    list_filter = ('status', 'is_pinned', 'created_at', 'average_sentiment')
    search_fields = ('title', 'summary', 'user__username')
    readonly_fields = ('created_at', 'updated_at', 'message_count', 'average_sentiment')
    
    fieldsets = (
        ('Conversation Info', {
            'fields': ('user', 'title', 'summary', 'topic', 'tags')
        }),
        ('Status', {
            'fields': ('status', 'is_pinned', 'is_archived')
        }),
        ('Statistics', {
            'fields': ('message_count', 'average_sentiment'),
            'classes': ('collapse',)
        }),
        ('Sharing', {
            'fields': ('is_public', 'share_token'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_message_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_status_badge(self, obj):
        """Display status with color badge"""
        colors = {
            'active': '#28a745',
            'archived': '#ffc107',
            'deleted': '#dc3545',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    get_status_badge.short_description = 'Status'
    
    def get_sentiment_emoji(self, obj):
        """Display sentiment with emoji"""
        sentiment_icons = {
            'positive': '😊',
            'neutral': '😐',
            'negative': '😞',
        }
        label = obj.get_sentiment_label
        return f"{sentiment_icons.get(label, '❓')} {label.capitalize()}"
    get_sentiment_emoji.short_description = 'Sentiment'


# ==================== MESSAGE ADMIN ====================
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Admin interface for Message model
    Displays individual messages with sentiment and delivery status
    """
    
    list_display = (
        'id',
        'get_sender_badge',
        'get_content_preview',
        'get_sentiment_badge',
        'get_status_icon',
        'created_at'
    )
    list_filter = ('sender', 'sentiment_label', 'status', 'created_at', 'is_liked')
    search_fields = ('content', 'conversation__title')
    readonly_fields = ('created_at', 'updated_at', 'sentiment_score')
    
    fieldsets = (
        ('Message Content', {
            'fields': ('conversation', 'sender', 'content')
        }),
        ('Status', {
            'fields': ('status', 'error_message')
        }),
        ('AI Information', {
            'fields': ('model_used', 'response_time_ms', 'token_count'),
            'classes': ('collapse',)
        }),
        ('Sentiment Analysis', {
            'fields': ('sentiment_score', 'sentiment_label'),
            'classes': ('collapse',)
        }),
        ('User Interaction', {
            'fields': ('is_liked', 'is_disliked', 'reaction'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('is_pinned', 'citations', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_sender_badge(self, obj):
        """Display sender with color badge"""
        colors = {
            'user': '#007bff',
            'ai': '#6f42c1',
            'system': '#6c757d',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.sender, '#6c757d'),
            obj.get_sender_display()
        )
    get_sender_badge.short_description = 'Sender'
    
    def get_content_preview(self, obj):
        """Display content preview (first 50 chars)"""
        preview = obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
        return preview
    get_content_preview.short_description = 'Content'
    
    def get_sentiment_badge(self, obj):
        """Display sentiment with badge"""
        if not obj.sentiment_label:
            return '—'
        colors = {
            'positive': '#28a745',
            'neutral': '#ffc107',
            'negative': '#dc3545',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.sentiment_label, '#6c757d'),
            obj.get_sentiment_label_display() if hasattr(obj, 'get_sentiment_label_display') else obj.sentiment_label.capitalize()
        )
    get_sentiment_badge.short_description = 'Sentiment'
    
    def get_status_icon(self, obj):
        """Display status with icon"""
        icons = {
            'sent': '✓',
            'delivered': '✓✓',
            'failed': '✗',
            'pending': '⏱',
        }
        return icons.get(obj.status, '?')
    get_status_icon.short_description = 'Status'


# ==================== SENTIMENT ADMIN ====================
@admin.register(Sentiment)
class SentimentAdmin(admin.ModelAdmin):
    """
    Admin interface for Sentiment Analysis
    Displays sentiment analysis results with confidence scores
    """
    
    list_display = (
        'id',
        'get_sentiment_label_badge',
        'get_confidence_bar',
        'analyzed_at'
    )
    list_filter = ('label', 'analyzed_at', 'confidence')
    search_fields = ('message__content',)
    readonly_fields = ('analyzed_at', 'get_emotions_display')
    
    fieldsets = (
        ('Analysis Result', {
            'fields': ('message', 'conversation', 'label', 'confidence')
        }),
        ('Scores', {
            'fields': ('positive_score', 'neutral_score', 'negative_score'),
            'classes': ('collapse',)
        }),
        ('Details', {
            'fields': ('get_emotions_display', 'key_phrases'),
            'classes': ('collapse',)
        }),
        ('Model Information', {
            'fields': ('model_used', 'analysis_version'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('analyzed_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_sentiment_label_badge(self, obj):
        """Display sentiment with badge"""
        colors = {
            'positive': '#28a745',
            'neutral': '#ffc107',
            'negative': '#dc3545',
            'mixed': '#6f42c1',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.label, '#6c757d'),
            obj.get_label_display()
        )
    get_sentiment_label_badge.short_description = 'Label'
    
    def get_confidence_bar(self, obj):
        """Display confidence as progress bar"""
        percentage = int(obj.confidence * 100)
        color = '#28a745' if obj.confidence > 0.7 else '#ffc107' if obj.confidence > 0.5 else '#dc3545'
        return format_html(
            '<div style="background-color: #f0f0f0; border-radius: 3px; width: 200px; height: 20px;">'
            '<div style="background-color: {}; height: 100%; width: {}%; border-radius: 3px; text-align: center; line-height: 20px; color: white; font-weight: bold;">'
            '{}%'
            '</div></div>',
            color,
            percentage,
            percentage
        )
    get_confidence_bar.short_description = 'Confidence'
    
    def get_emotions_display(self, obj):
        """Display emotions in readable format"""
        if not obj.emotions:
            return 'No emotions detected'
        emotions_html = '<br>'.join([f"<strong>{k}:</strong> {v:.2f}" for k, v in obj.emotions.items()])
        return format_html(emotions_html)
    get_emotions_display.short_description = 'Emotions'


# ==================== TOPIC ADMIN ====================
@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    """
    Admin interface for Topic Analysis
    Displays topic extraction and categorization results
    """
    
    list_display = (
        'primary_topic',
        'category',
        'get_complexity_indicator',
        'get_confidence_indicator',
        'analyzed_at'
    )
    list_filter = ('category', 'analyzed_at', 'complexity_score', 'technical_score')
    search_fields = ('primary_topic', 'conversation__title')
    readonly_fields = ('analyzed_at', 'updated_at')
    
    fieldsets = (
        ('Topic Classification', {
            'fields': ('conversation', 'primary_topic', 'secondary_topics', 'category', 'subcategory')
        }),
        ('Analysis Scores', {
            'fields': ('confidence_score', 'complexity_score', 'technical_score'),
            'classes': ('collapse',)
        }),
        ('Extracted Information', {
            'fields': ('keywords', 'entities'),
            'classes': ('collapse',)
        }),
        ('Model Information', {
            'fields': ('model_used',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('analyzed_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_complexity_indicator(self, obj):
        """Display complexity level"""
        if obj.complexity_score > 0.7:
            return format_html('<span style="color: #dc3545;">⬆ Complex</span>')
        elif obj.complexity_score > 0.4:
            return format_html('<span style="color: #ffc107;">➡ Medium</span>')
        return format_html('<span style="color: #28a745;">⬇ Simple</span>')
    get_complexity_indicator.short_description = 'Complexity'
    
    def get_confidence_indicator(self, obj):
        """Display confidence level"""
        percentage = int(obj.confidence_score * 100)
        color = '#28a745' if obj.confidence_score > 0.7 else '#ffc107' if obj.confidence_score > 0.5 else '#dc3545'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}%</span>',
            color,
            percentage
        )
    get_confidence_indicator.short_description = 'Confidence'


# ==================== ADMIN SITE CONFIGURATION ====================
admin.site.site_header = "AI Chat Portal Administration"
admin.site.site_title = "AI Chat Admin"
admin.site.index_title = "Welcome to AI Chat Portal Admin Panel"
