import logging
from googleapiclient.discovery import build
from quart import current_app
from youtube_transcript_api import YouTubeTranscriptApi

async def validate_youtube_video(video_id: str):
    try:
        api_key = current_app.config['YOUTUBE_API_KEY']
        youtube = build('youtube', 'v3', developerKey=api_key)
        request = youtube.videos().list(part='snippet,statistics', id=video_id)
        details = request.execute()
        title: str = details['items'][0]['snippet']['title']
        trans = YouTubeTranscriptApi.list_transcripts(video_id=video_id).find_transcript(language_codes=['en', 'en-GB'])
        if trans:
            return title
    except Exception as e:
        logging.error(e.__str__())