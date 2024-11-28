import logging
from googleapiclient.discovery import build
from quart import current_app
from youtube_transcript_api import YouTubeTranscriptApi
from isodate import parse_duration

async def validate_youtube_video(video_id: str):
    try:
        api_key = current_app.config['YOUTUBE_API_KEY']
        youtube = build('youtube', 'v3', developerKey=api_key)
        request = youtube.videos().list(part='snippet,contentDetails', id=video_id)
        details = request.execute()
        title: str = details['items'][0]['snippet']['title']
        duration = details['items'][0]['contentDetails']['duration']
        minutes = int(parse_duration(duration).total_seconds()) / 60
        if minutes > 360:
            raise Exception('Only 6 hours or shorter videos are supported. The provided video is more than 6 hours')
        trans = YouTubeTranscriptApi.list_transcripts(video_id=video_id).find_transcript(language_codes=['en', 'en-GB'])
        if trans:
            return title
    except Exception as e:
        logging.error(e.__str__())