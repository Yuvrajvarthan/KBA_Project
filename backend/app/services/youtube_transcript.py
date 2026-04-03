from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled, 
    NoTranscriptFound, 
    VideoUnavailable,
    NoTranscriptAvailable
)
import re
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class YouTubeTranscriptService:
    """Service for extracting YouTube video transcripts"""
    
    @staticmethod
    def extract_video_id(url: str) -> str:
        """Extract video ID from YouTube URL"""
        # Regular expressions for different YouTube URL formats
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)',
            r'youtu\.be\/([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return ""
    
    @staticmethod
    async def get_transcript(url: str) -> Dict[str, Any]:
        """Get transcript from YouTube video"""
        try:
            # Extract video ID
            video_id = YouTubeTranscriptService.extract_video_id(url)
            if not video_id:
                return {
                    "success": False,
                    "error": "Invalid YouTube URL or could not extract video ID",
                    "text": "",
                    "metadata": {}
                }
            
            # Get available transcripts
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            except Exception as e:
                logger.error(f"Error listing transcripts for {video_id}: {e}")
                return {
                    "success": False,
                    "error": f"Could not access video transcripts: {str(e)}",
                    "text": "",
                    "metadata": {}
                }
            
            # Try to get English transcript first, then any available
            transcript = None
            languages_to_try = ['en', 'en-US', 'en-GB']
            
            # Try preferred languages
            for lang in languages_to_try:
                try:
                    transcript = transcript_list.find_transcript([lang])
                    break
                except NoTranscriptFound:
                    continue
            
            # If no preferred language found, get any manually created transcript
            if not transcript:
                try:
                    transcript = transcript_list.find_manually_created_transcript()
                except NoTranscriptFound:
                    pass
            
            # If still no transcript, get any generated transcript
            if not transcript:
                try:
                    transcript = transcript_list.find_generated_transcript()
                except NoTranscriptFound:
                    pass
            
            # If still no transcript, get the first available
            if not transcript:
                try:
                    transcript = list(transcript_list)[0]
                except (IndexError, Exception):
                    pass
            
            if not transcript:
                return {
                    "success": False,
                    "error": "No transcript available for this video",
                    "text": "",
                    "metadata": {}
                }
            
            # Fetch the transcript data
            transcript_data = transcript.fetch()
            
            # Combine transcript segments into readable text
            text_segments = []
            for segment in transcript_data:
                # Clean up the text
                clean_text = segment['text'].strip()
                if clean_text:
                    text_segments.append(clean_text)
            
            full_text = ' '.join(text_segments)
            
            # Get metadata
            metadata = {
                "video_id": video_id,
                "url": url,
                "language": transcript.language,
                "language_code": transcript.language_code,
                "is_generated": transcript.is_generated,
                "is_manually_created": transcript.is_manually_created,
                "translation_languages": [lang['language'] for lang in transcript.translation_languages],
                "duration": sum(segment['duration'] for segment in transcript_data),
                "segment_count": len(transcript_data)
            }
            
            return {
                "success": True,
                "text": full_text,
                "metadata": metadata,
                "segments": transcript_data
            }
            
        except VideoUnavailable:
            logger.error(f"Video {url} is unavailable")
            return {
                "success": False,
                "error": "Video is unavailable or private",
                "text": "",
                "metadata": {}
            }
        except TranscriptsDisabled:
            logger.error(f"Transcripts are disabled for video {url}")
            return {
                "success": False,
                "error": "Transcripts are disabled for this video",
                "text": "",
                "metadata": {}
            }
        except NoTranscriptAvailable:
            logger.error(f"No transcript available for video {url}")
            return {
                "success": False,
                "error": "No transcript available for this video",
                "text": "",
                "metadata": {}
            }
        except Exception as e:
            logger.error(f"Error getting transcript from {url}: {e}")
            return {
                "success": False,
                "error": f"Error extracting transcript: {str(e)}",
                "text": "",
                "metadata": {}
            }
