#!/usr/bin/env python3
import os
import sys
import time
import argparse
import random
import logging
from pathlib import Path
from youtube_mp3_transcriber import download_youtube_audio, transcribe_audio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Batch download YouTube videos as MP3 and transcribe them with rate limiting.')
    parser.add_argument('--input-file', required=True, help='File containing YouTube URLs (one per line)')
    parser.add_argument('--output-dir', default='downloads', help='Output directory for downloaded files')
    parser.add_argument('--api-key', help='OpenAI API key')
    parser.add_argument('--min-delay', type=int, default=30, help='Minimum delay between downloads in seconds')
    parser.add_argument('--max-delay', type=int, default=120, help='Maximum delay between downloads in seconds')
    parser.add_argument('--skip-transcription', action='store_true', help='Skip transcription step')
    return parser.parse_args()

def read_urls(input_file):
    """Read URLs from input file."""
    try:
        with open(input_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        return urls
    except Exception as e:
        logger.error(f"Error reading input file: {str(e)}")
        sys.exit(1)

def main():
    """Main function."""
    args = parse_arguments()
    
    # Check if OpenAI API key is provided
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key and not args.skip_transcription:
        logger.error("OpenAI API key is required for transcription. "
                    "Provide it with --api-key or set OPENAI_API_KEY environment variable.")
        sys.exit(1)
    
    # Read URLs from input file
    urls = read_urls(args.input_file)
    logger.info(f"Found {len(urls)} URLs to process")
    
    # Process each URL with rate limiting
    for i, url in enumerate(urls):
        try:
            logger.info(f"Processing URL {i+1}/{len(urls)}: {url}")
            
            # Download YouTube audio
            mp3_file = download_youtube_audio(url, args.output_dir)
            
            # Transcribe audio if not skipped
            if not args.skip_transcription:
                transcript_file = transcribe_audio(mp3_file, api_key)
                logger.info(f"Transcription saved to: {transcript_file}")
            
            # Apply rate limiting if not the last URL
            if i < len(urls) - 1:
                delay = random.randint(args.min_delay, args.max_delay)
                logger.info(f"Waiting {delay} seconds before next download...")
                time.sleep(delay)
        
        except Exception as e:
            logger.error(f"Error processing URL {url}: {str(e)}")
            logger.info("Continuing with next URL...")
            # Still apply delay before next attempt
            if i < len(urls) - 1:
                delay = random.randint(args.min_delay, args.max_delay)
                logger.info(f"Waiting {delay} seconds before next download...")
                time.sleep(delay)
    
    logger.info("Batch processing completed")

if __name__ == "__main__":
    main() 