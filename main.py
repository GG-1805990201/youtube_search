from googleapiclient.discovery import build
from database import insert_video
from service import app
from isodate import parse_duration
import threading
import time


def print_youtube(search_query):
    # Use your own API key here
    api_key = 'AIzaSyB25R6SLFcGQM277ohunO7rEP6KIedYGgE'
    # api_key = 'AIzaSyCm0p7tV-T682Ij_e5Z7rOrkbqddd0ntCw'

    # Get the search query from user input
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Step 1: Initial search
    request = youtube.search().list(
        q=search_query,
        part='snippet',
        type='video',
        maxResults=10
    )
    response = request.execute()

    video_ids = [item['id']['videoId'] for item in response['items']]

    # Step 2: Fetch video details and filter out Shorts
    details_request = youtube.videos().list(
        part='contentDetails',
        id=','.join(video_ids)
    )
    details_response = details_request.execute()

    for item in details_response['items']:
        duration = parse_duration(item['contentDetails']['duration']).total_seconds()

        # Assuming you want to exclude videos shorter than 60 seconds
        if duration > 60:
            # Find the snippet from the initial response
            snippet = next((x['snippet'] for x in response['items'] if x['id']['videoId'] == item['id']), None)
            if snippet:
                title = snippet['title']
                description = snippet['description']
                publishTime = snippet['publishedAt']
                thumbnailsUrls = snippet['thumbnails']['default']['url']  # Adjust as needed

                # Print the extracted information
                print(f"Title: {title}")
                print(f"Description: {description}")
                print(f"Publish Time: {publishTime}")
                print(f"Thumbnail URL: {thumbnailsUrls}")
                print("-" * 40)

                # Insert into database as needed
                insert_video(title, description, publishTime, thumbnailsUrls)


def run_periodically(interval, func, *args):
    """Run a function in a separate thread at given intervals."""

    def func_wrapper():
        while True:
            func(*args)
            time.sleep(interval)

    thread = threading.Thread(target=func_wrapper)
    thread.daemon = True  # Daemonize thread
    thread.start()


if __name__ == '__main__':
    run_periodically(60, print_youtube, "Cricket")
    app.run(debug=True)
