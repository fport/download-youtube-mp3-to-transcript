#!/usr/bin/env python3
import os
import sys
import time
import argparse
import yt_dlp
from pydub import AudioSegment
import openai
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Download YouTube video as MP3 and transcribe it.')
    parser.add_argument('url', help='YouTube video URL')
    parser.add_argument('--output-dir', default='downloads', help='Output directory for downloaded files')
    parser.add_argument('--api-key', help='OpenAI API key')
    parser.add_argument('--skip-transcription', action='store_true', help='Skip transcription step')
    return parser.parse_args()

def download_youtube_audio(url, output_dir):
    """Download YouTube video as MP3."""
    try:
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Downloading audio from: {url}")
        
        # Configure yt-dlp options with additional parameters to bypass restrictions
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': False,
            'no_warnings': False,
            # Add options to bypass bot protection
            'nocheckcertificate': True,
            'geo_bypass': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                    'skip': ['hls', 'dash', 'translated_subs']
                }
            },
            # Add random user agent
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'referer': 'https://www.youtube.com/'
        }
        
        # Download the audio
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info.get('title', 'video')
            
        # Find the actual downloaded file in the output directory
        # This is more reliable than constructing the filename ourselves
        downloaded_files = [f for f in os.listdir(output_dir) if f.endswith('.mp3')]
        if not downloaded_files:
            raise FileNotFoundError(f"No MP3 files found in {output_dir} after download")
        
        # If multiple files exist, try to find the most recently created one
        if len(downloaded_files) > 1:
            downloaded_files.sort(key=lambda x: os.path.getmtime(os.path.join(output_dir, x)), reverse=True)
        
        mp3_file = os.path.join(output_dir, downloaded_files[0])
        
        logger.info(f"Download complete: {mp3_file}")
        return mp3_file
    
    except Exception as e:
        logger.error(f"Error downloading YouTube audio: {str(e)}")
        raise

def transcribe_audio(audio_file, api_key):
    """Transcribe audio file using OpenAI's Whisper model."""
    try:
        logger.info(f"Transcribing audio file: {audio_file}")
        
        # Set OpenAI API key
        openai.api_key = api_key
        
        # Get file size
        file_size = os.path.getsize(audio_file) / (1024 * 1024)  # in MB
        logger.info(f"File size: {file_size:.2f} MB")
        
        # Open the audio file
        with open(audio_file, "rb") as file:
            # Use the Whisper model to transcribe
            logger.info("Starting transcription with Whisper model...")
            client = openai.OpenAI(api_key=api_key)
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=file,
                response_format="text"
            )
        
        # Save transcription to file
        base_name = os.path.splitext(audio_file)[0]
        transcript_file = f"{base_name}_transcript.txt"
        
        with open(transcript_file, "w", encoding="utf-8") as f:
            f.write(response)
        
        logger.info(f"Transcription saved to: {transcript_file}")
        return transcript_file
    
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        raise

def main():
    """Main function."""
    args = parse_arguments()
    
    # Check if OpenAI API key is provided
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key and not args.skip_transcription:
        logger.error("OpenAI API key is required for transcription. "
                    "Provide it with --api-key or set OPENAI_API_KEY environment variable.")
        sys.exit(1)
    
    try:
        # Download YouTube audio
        mp3_file = download_youtube_audio(args.url, args.output_dir)
        
        # Transcribe audio if not skipped
        if not args.skip_transcription:
            transcript_file = transcribe_audio(mp3_file, api_key)
            logger.info(f"Process completed successfully. Transcript saved to: {transcript_file}")
        else:
            logger.info(f"Process completed successfully. Audio saved to: {mp3_file}")
    
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 