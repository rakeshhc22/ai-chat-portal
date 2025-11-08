"""
Analysis Service for AI Chat Portal
Handles sentiment analysis, topic extraction, and insights generation
"""

import logging
from typing import Dict, List, Any, Optional
import json

logger = logging.getLogger(__name__)

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning('transformers library not installed. Analysis features disabled.')


class SentimentAnalyzer:
    """
    Sentiment analysis using HuggingFace transformers
    """
    
    def __init__(self, model_name: str = 'distilbert-base-uncased-finetuned-sst-2-english'):
        """Initialize sentiment analyzer"""
        self.model_name = model_name
        self.pipeline = None
        
        if TRANSFORMERS_AVAILABLE:
            try:
                self.pipeline = pipeline(
                    'sentiment-analysis',
                    model=model_name
                )
                logger.info(f'Loaded sentiment model: {model_name}')
            except Exception as e:
                logger.error(f'Failed to load sentiment model: {str(e)}')
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text
        
        Returns:
            {
                'label': 'POSITIVE|NEGATIVE',
                'score': 0.0-1.0,
                'sentiment': 'positive|neutral|negative'
            }
        """
        if not TRANSFORMERS_AVAILABLE or not self.pipeline:
            return {
                'label': 'NEUTRAL',
                'score': 0.0,
                'sentiment': 'neutral',
                'available': False
            }
        
        try:
            result = self.pipeline(text[:512])[0]  # Limit to 512 chars
            
            label = result['label'].lower()
            score = result['score']
            
            # Convert to sentiment scale (-1 to 1)
            if label == 'positive':
                sentiment_score = score
                sentiment_label = 'positive'
            elif label == 'negative':
                sentiment_score = -score
                sentiment_label = 'negative'
            else:
                sentiment_score = 0.0
                sentiment_label = 'neutral'
            
            return {
                'label': result['label'],
                'score': score,
                'sentiment_score': sentiment_score,
                'sentiment': sentiment_label,
                'available': True
            }
        
        except Exception as e:
            logger.error(f'Sentiment analysis error: {str(e)}')
            return {
                'label': 'ERROR',
                'score': 0.0,
                'sentiment': 'neutral',
                'available': False
            }
    
    def batch_analyze(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze multiple texts"""
        return [self.analyze(text) for text in texts]


class TopicExtractor:
    """
    Topic extraction and categorization
    """
    
    def __init__(self):
        """Initialize topic extractor"""
        self.topics = {
            'technical': ['code', 'programming', 'development', 'debugging', 'error', 'bug', 'api', 'database'],
            'general': ['hello', 'hi', 'how', 'what', 'why', 'when', 'where'],
            'business': ['project', 'deadline', 'meeting', 'budget', 'plan', 'strategy', 'goal'],
            'science': ['research', 'study', 'experiment', 'data', 'analysis', 'result', 'theory'],
        }
    
    def extract_topics(self, text: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Extract topics from text
        
        Returns:
            {
                'primary_topic': 'technical',
                'secondary_topics': ['general', 'business'],
                'keywords': ['code', 'api', 'project'],
                'category': 'Technical'
            }
        """
        text_lower = text.lower()
        topic_scores = {}
        
        # Calculate topic scores
        for category, keywords in self.topics.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                topic_scores[category] = score
        
        if not topic_scores:
            return {
                'primary_topic': 'general',
                'secondary_topics': [],
                'keywords': [],
                'category': 'General',
                'confidence': 0.3
            }
        
        # Sort by score
        sorted_topics = sorted(
            topic_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        primary = sorted_topics[0][0]
        secondary = [t[0] for t in sorted_topics[1:top_k]] if len(sorted_topics) > 1 else []
        
        # Extract keywords
        keywords = []
        for topic in self.topics[primary]:
            if topic in text_lower:
                keywords.append(topic)
        
        return {
            'primary_topic': primary,
            'secondary_topics': secondary,
            'keywords': keywords,
            'category': primary.capitalize(),
            'confidence': min(sorted_topics[0][1] / 10, 1.0)
        }


class InsightGenerator:
    """
    Generate insights from conversation data
    """
    
    @staticmethod
    def generate_summary(messages: List[Dict[str, str]], max_sentences: int = 3) -> str:
        """
        Generate summary from messages
        Simple extractive summarization
        """
        if not messages:
            return "No messages to summarize"
        
        # Get longest messages (likely most important)
        sorted_messages = sorted(
            messages,
            key=lambda x: len(x.get('content', '')),
            reverse=True
        )
        
        summary_messages = sorted_messages[:max_sentences]
        summary = ' '.join([m.get('content', '') for m in summary_messages])
        
        return summary[:500]  # Limit to 500 chars
    
    @staticmethod
    def extract_entities(text: str) -> Dict[str, List[str]]:
        """
        Extract named entities (simple implementation)
        """
        entities = {
            'people': [],
            'organizations': [],
            'locations': [],
            'products': [],
        }
        
        # Simple pattern matching (can be enhanced with NER)
        words = text.split()
        for i, word in enumerate(words):
            if word[0].isupper():  # Capitalized words likely entities
                if i + 1 < len(words) and words[i + 1][0].isupper():
                    entities['people'].append(f"{word} {words[i + 1]}")
        
        return entities
    
    @staticmethod
    def generate_insights(
        messages: List[Dict[str, str]],
        sentiments: List[float]
    ) -> Dict[str, Any]:
        """
        Generate insights from conversation
        """
        insights = {
            'total_messages': len(messages),
            'average_sentiment': sum(sentiments) / len(sentiments) if sentiments else 0,
            'sentiment_trend': 'positive' if (sum(sentiments) / len(sentiments) if sentiments else 0) > 0.5 else 'negative',
            'key_insights': [
                f"Conversation has {len(messages)} messages",
                f"Average sentiment: {'positive' if (sum(sentiments) / len(sentiments) if sentiments else 0) > 0.5 else 'negative'}",
                f"Most active message count: {max(len(m.get('content', '')) for m in messages) if messages else 0} characters"
            ]
        }
        
        return insights


class AnalysisService:
    """Unified analysis service"""
    
    def __init__(self):
        """Initialize all analyzers"""
        self.sentiment_analyzer = SentimentAnalyzer()
        self.topic_extractor = TopicExtractor()
        self.insight_generator = InsightGenerator()
    
    def analyze_message(self, text: str) -> Dict[str, Any]:
        """
        Comprehensive analysis of a message
        """
        sentiment = self.sentiment_analyzer.analyze(text)
        topics = self.topic_extractor.extract_topics(text)
        entities = self.insight_generator.extract_entities(text)
        
        return {
            'sentiment': sentiment,
            'topics': topics,
            'entities': entities,
        }
    
    def analyze_conversation(
        self,
        messages: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Analyze entire conversation
        """
        sentiments = []
        text_for_topics = []
        
        for message in messages:
            content = message.get('content', '')
            if content:
                sentiment = self.sentiment_analyzer.analyze(content)
                sentiments.append(sentiment.get('sentiment_score', 0))
                text_for_topics.append(content)
        
        combined_text = ' '.join(text_for_topics)
        topics = self.topic_extractor.extract_topics(combined_text)
        summary = self.insight_generator.generate_summary(messages)
        insights = self.insight_generator.generate_insights(messages, sentiments)
        
        return {
            'summary': summary,
            'topics': topics,
            'insights': insights,
            'average_sentiment': sum(sentiments) / len(sentiments) if sentiments else 0
        }


# Initialize global analysis service
analysis_service = AnalysisService()
