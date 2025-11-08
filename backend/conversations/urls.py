"""
URL Configuration for Conversations App
Routes all API endpoints to their respective viewsets
"""

from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter, SimpleRouter
from .views import (
    ConversationViewSet,
    MessageViewSet,
    SentimentViewSet,
    TopicViewSet
)

# ✅ Use SimpleRouter instead of DefaultRouter to avoid conflicts
router = SimpleRouter(trailing_slash=True)

# Register viewsets with proper basename
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'sentiments', SentimentViewSet, basename='sentiment')
router.register(r'topics', TopicViewSet, basename='topic')

urlpatterns = [
    path('', include(router.urls)),
]
