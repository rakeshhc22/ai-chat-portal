"""
AI Service Module - Handles communication with LM Studio API
Provides AI responses for chat conversations
"""

import requests
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class LMStudioService:
    """
    Service class to communicate with LM Studio API
    Handles sending messages to local LLM and receiving responses
    """
    
    def __init__(self, api_url: str = "http://192.168.229.1:1234"):
        """
        Initialize LM Studio Service
        
        Args:
            api_url (str): Base URL for LM Studio API server
        """
        self.api_url = api_url
        self.endpoint = f"{api_url}/v1/chat/completions"
        self.request_timeout = 120  # Timeout in seconds
        
        logger.info(f"✅ LMStudioService initialized")
        logger.info(f"   Endpoint: {self.endpoint}")
        logger.info(f"   Timeout: {self.request_timeout}s")
    
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """
        Send chat messages to LM Studio and get AI response
        
        Args:
            messages (List[Dict]): List of message dicts with 'role' and 'content' keys
                                  Example: [{'role': 'user', 'content': 'Hello'}]
            temperature (float): Model temperature (0.0-1.0). Higher = more creative
        
        Returns:
            str: AI response text, or error message if request fails
        """
        try:
            # Log request details
            logger.info(f"📤 Sending {len(messages)} messages to LM Studio")
            
            # Build request payload
            payload = {
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 200,
                "top_p": 0.9,
                "stream": False
            }
            
            logger.debug(f"Payload: {payload}")
            
            # Send POST request to LM Studio
            logger.info(f"🔗 Making request to {self.endpoint}")
            
            response = requests.post(
                self.endpoint,
                json=payload,
                timeout=self.request_timeout
            )
            
            # Check response status
            logger.info(f"📊 Response status code: {response.status_code}")
            
            # Handle error responses
            if response.status_code == 400:
                error_msg = f"Bad Request: {response.text}"
                logger.error(f"❌ {error_msg}")
                return "Error: Invalid request to AI service. Please try again."
            
            if response.status_code >= 500:
                error_msg = f"Server Error: {response.text}"
                logger.error(f"❌ {error_msg}")
                return "Error: AI service is experiencing issues. Please try again."
            
            # Raise exception for other HTTP errors
            response.raise_for_status()
            
            # Parse JSON response
            result = response.json()
            logger.debug(f"Response: {result}")
            
            # Extract AI response from choices
            if 'choices' in result and len(result['choices']) > 0:
                choice = result['choices'][0]
                
                if 'message' in choice and 'content' in choice['message']:
                    ai_text = choice['message']['content'].strip()
                    
                    if ai_text:
                        logger.info(f"✅ AI response: {ai_text[:80]}...")
                        return ai_text
            
            # Fallback if response format is unexpected
            logger.warning(f"⚠️ Unexpected response format: {result}")
            return "Sorry, I couldn't generate a response. Please try again."
        
        except requests.exceptions.Timeout:
            logger.error(f"⏱️ Request timeout after {self.request_timeout}s")
            return f"⏱️ AI service is slow. Please wait and try again (timeout after {self.request_timeout}s)"
        
        except requests.exceptions.ConnectionError as e:
            logger.error(f"❌ Connection error: {str(e)}")
            logger.error(f"   Cannot reach LM Studio at {self.api_url}")
            return f"❌ Cannot connect to AI service. Is LM Studio running at {self.api_url}?"
        
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Request error: {str(e)}")
            return f"Error: Request failed - {str(e)}"
        
        except ValueError as e:
            logger.error(f"❌ JSON decode error: {str(e)}")
            return "Error: Invalid response format from AI service"
        
        except Exception as e:
            logger.error(f"❌ Unexpected error: {str(e)}", exc_info=True)
            return f"Error: {str(e)}"
