"""
Export Service for AI Chat Portal
Handles exporting conversations in multiple formats
Supports: PDF, JSON, Markdown, CSV
"""

import logging
from typing import Dict, List, Any, Optional
import json
from datetime import datetime
import io

logger = logging.getLogger(__name__)

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
    from reportlab.lib import colors
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logger.warning('reportlab not installed. PDF export disabled.')


class ExportService:
    """
    Service for exporting conversations in various formats
    """
    
    def __init__(self):
        """Initialize export service"""
        self.pdf_available = PDF_AVAILABLE
    
    def export_to_json(
        self,
        conversation: Dict[str, Any],
        messages: List[Dict[str, Any]]
    ) -> str:
        """
        Export conversation to JSON format
        
        Args:
            conversation: Conversation data
            messages: List of messages
        
        Returns:
            JSON string
        """
        try:
            export_data = {
                'conversation': {
                    'id': conversation.get('id'),
                    'title': conversation.get('title'),
                    'summary': conversation.get('summary'),
                    'topic': conversation.get('topic'),
                    'created_at': conversation.get('created_at'),
                    'updated_at': conversation.get('updated_at'),
                    'message_count': len(messages),
                    'average_sentiment': conversation.get('average_sentiment'),
                },
                'messages': messages,
                'export_date': datetime.now().isoformat(),
                'export_format': 'json'
            }
            
            return json.dumps(export_data, indent=2, default=str)
        
        except Exception as e:
            logger.error(f'JSON export error: {str(e)}')
            return '{}'
    
    def export_to_markdown(
        self,
        conversation: Dict[str, Any],
        messages: List[Dict[str, Any]]
    ) -> str:
        """
        Export conversation to Markdown format
        
        Args:
            conversation: Conversation data
            messages: List of messages
        
        Returns:
            Markdown string
        """
        try:
            md_content = f"""# {conversation.get('title', 'Conversation')}

## Conversation Details
- **ID:** {conversation.get('id')}
- **Created:** {conversation.get('created_at')}
- **Updated:** {conversation.get('updated_at')}
- **Topic:** {conversation.get('topic', 'General')}
- **Average Sentiment:** {conversation.get('average_sentiment', 0):.2f}

## Summary
{conversation.get('summary', 'No summary available')}

---

## Messages

"""
            
            for message in messages:
                sender = message.get('sender', 'unknown').upper()
                content = message.get('content', '')
                timestamp = message.get('created_at', '')
                sentiment = message.get('sentiment_label', 'neutral')
                
                md_content += f"""### {sender}
- **Time:** {timestamp}
- **Sentiment:** {sentiment}

{content}

---

"""
            
            md_content += f"\n*Exported on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
            
            return md_content
        
        except Exception as e:
            logger.error(f'Markdown export error: {str(e)}')
            return '# Export Error'
    
    def export_to_csv(
        self,
        conversation: Dict[str, Any],
        messages: List[Dict[str, Any]]
    ) -> str:
        """
        Export conversation to CSV format
        
        Args:
            conversation: Conversation data
            messages: List of messages
        
        Returns:
            CSV string
        """
        try:
            csv_content = 'Timestamp,Sender,Sentiment,Content\n'
            
            for message in messages:
                timestamp = message.get('created_at', '').replace(',', ';')
                sender = message.get('sender', 'unknown')
                sentiment = message.get('sentiment_label', 'neutral')
                content = message.get('content', '').replace('\n', ' ').replace(',', ';')
                
                csv_content += f'"{timestamp}","{sender}","{sentiment}","{content}"\n'
            
            return csv_content
        
        except Exception as e:
            logger.error(f'CSV export error: {str(e)}')
            return ''
    
    def export_to_pdf(
        self,
        conversation: Dict[str, Any],
        messages: List[Dict[str, Any]]
    ) -> Optional[bytes]:
        """
        Export conversation to PDF format
        
        Args:
            conversation: Conversation data
            messages: List of messages
        
        Returns:
            PDF bytes or None if unavailable
        """
        if not self.pdf_available:
            logger.warning('PDF export not available (reportlab not installed)')
            return None
        
        try:
            # Create PDF buffer
            pdf_buffer = io.BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
            story = []
            
            # Get styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1f2937'),
                spaceAfter=12,
                fontName='Helvetica-Bold'
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#374151'),
                spaceAfter=6,
                fontName='Helvetica-Bold'
            )
            
            # Add title
            story.append(Paragraph(
                conversation.get('title', 'Conversation'),
                title_style
            ))
            
            # Add conversation details
            story.append(Paragraph('Conversation Details', heading_style))
            details_data = [
                ['Field', 'Value'],
                ['ID', str(conversation.get('id', 'N/A'))],
                ['Created', str(conversation.get('created_at', 'N/A'))],
                ['Topic', conversation.get('topic', 'General')],
                ['Average Sentiment', f"{conversation.get('average_sentiment', 0):.2f}"],
            ]
            
            details_table = Table(details_data, colWidths=[2*inch, 4*inch])
            details_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e5e7eb')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            
            story.append(details_table)
            story.append(Spacer(1, 12))
            
            # Add messages
            story.append(Paragraph('Messages', heading_style))
            
            for message in messages:
                sender = message.get('sender', 'unknown').upper()
                content = message.get('content', '')
                timestamp = message.get('created_at', '')
                
                story.append(Paragraph(f'<b>{sender}</b> ({timestamp})', styles['Normal']))
                story.append(Paragraph(content, styles['Normal']))
                story.append(Spacer(1, 6))
            
            # Add footer
            story.append(Spacer(1, 12))
            story.append(Paragraph(
                f'Exported on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey)
            ))
            
            # Build PDF
            doc.build(story)
            pdf_buffer.seek(0)
            
            return pdf_buffer.getvalue()
        
        except Exception as e:
            logger.error(f'PDF export error: {str(e)}')
            return None
    
    def export(
        self,
        format_type: str,
        conversation: Dict[str, Any],
        messages: List[Dict[str, Any]]
    ) -> Any:
        """
        Export conversation in specified format
        
        Args:
            format_type: 'json', 'markdown', 'csv', or 'pdf'
            conversation: Conversation data
            messages: List of messages
        
        Returns:
            Exported data (string or bytes depending on format)
        """
        format_type = format_type.lower()
        
        if format_type == 'json':
            return self.export_to_json(conversation, messages)
        elif format_type == 'markdown':
            return self.export_to_markdown(conversation, messages)
        elif format_type == 'csv':
            return self.export_to_csv(conversation, messages)
        elif format_type == 'pdf':
            return self.export_to_pdf(conversation, messages)
        else:
            logger.warning(f'Unknown export format: {format_type}')
            return self.export_to_json(conversation, messages)
    
    def get_filename(self, conversation_title: str, format_type: str) -> str:
        """
        Generate export filename
        
        Args:
            conversation_title: Conversation title
            format_type: Export format
        
        Returns:
            Filename string
        """
        safe_title = ''.join(c for c in conversation_title if c.isalnum() or c in (' ', '-', '_'))[:50]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f'{safe_title}_{timestamp}.{format_type}'


# Initialize global export service
export_service = ExportService()
