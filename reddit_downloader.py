import sys
import praw
import requests
import time
import os
import threading
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

authenticated = False
MAX_NUM_FILES = 50 #Change this to change the number of files to download
MAX_NUM_THREADS = 100 #Change this to change the number to increase or decrease download speed


reddit = praw.Reddit(client_id="YOUR_CLIENT_ID",
                        client_secret="YOUR_CLIENT_SECRET",
                        redirect_uri="YOUR_REDIRECT_URI",
                        user_agent="YOUR_USER_AGENT", #This is a short description of your app.
                        refresh_token="YOUR_REFRESH_TOKEN") #Time based api token. Run token_refresh.py to generate a new refresh token.

#To get these credentials you need to create a Reddit app.
#Visit https://www.reddit.com/prefs/apps/ to create an app or view your existing apps.

try:
    reddit.user.me()
    authenticated = True
    user = reddit.user.me()
    print(f'Authenticated as {user.name}')
except Exception as e:
    print('Failed to authenticate user')
    print("Invalid refresh token. Run token_refresh.py to generate a new refresh token.")
    print("Run the script after updating the config.ini file.")
    print("Received error: " + str(e))
    
if authenticated == True:
    pass
else:
    sys.exit(1)

subreddit_name = input('Enter targeted subreddit (e.g. memes, music, or gaming): ').lower()
while subreddit_name == '':
    print('Subreddit name cannot be empty.')
    subreddit_name = input('Enter targeted subreddit (e.g. memes, music, or gaming): ').lower()
subreddit = reddit.subreddit(subreddit_name)

file_type_filter = input('Enter file type to filter by (photo, audio, video): ').lower()
if file_type_filter == '':
    file_type_filter = None
file_format_filter = input('Enter file format to filter by (e.g. .mp3, .jpg): ').lower()
if file_format_filter == '':
    file_format_filter = None
    
sorting_mechanism = input('Enter sorting mechanism (e.g. relevance, hot, top, new, or comments): ').lower()
if sorting_mechanism == '':
    sorting_mechanism = 'new'
    
word_patterns = input('Enter patterns of words to filter by (separated by commas): ').lower().split(',')
word_patterns = [pattern.strip() for pattern in word_patterns]

dir_path = os.path.join(os.getcwd(), subreddit_name)
if not os.path.exists(dir_path):
    os.makedirs(dir_path) 
    
if sorting_mechanism == 'new':
    post_limit = subreddit.new(limit=MAX_NUM_FILES)
else:
    post_limit = getattr(subreddit, sorting_mechanism)(limit=MAX_NUM_FILES)
    
count = 0
lock = threading.Lock()
threads = []
session = requests.Session()
retry_strategy = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

downloaded_posts = set()

def download_file(post, filename):
    try:
        with session.get(post.url, timeout=30) as response:
            response.raise_for_status()
            with open(filename, 'wb') as f:
                f.write(response.content)
            print('Downloaded', filename)
            with lock:
                global count
                count += 1
        downloaded_posts.add(post)
    except requests.exceptions.HTTPError as e:
        print(f'Error downloading file from {post.url}: {e}')
    except requests.exceptions.Timeout as e:
        print(f'Timeout downloading file from {post.url}: {e}')
    time.sleep(0.5)

while count < MAX_NUM_FILES:
    for post in post_limit:
        if post in downloaded_posts:
            continue
        post_title = post.title.lower()
        if all(pattern in post_title for pattern in word_patterns):
            file_extension = os.path.splitext(post.url)[-1][1:].lower()
            if file_extension and (
                file_type_filter is None or file_type_filter == 'none' or
                (file_type_filter in {'p', 'photo', 'photos', 'picture', 'pictures'} and file_extension in {'jpg', 'jpeg', 'png', 'gif'}) or
                (file_type_filter in {'a', 'audio', 'audios', 'sound', 'sounds', 's'} and file_extension in {'mp3', 'wav', 'flac'}) or
                (file_type_filter in {'v', 'video', 'videos', 'movie', 'movies', 'm'} and file_extension in {'mp4', 'mov', 'avi', 'gifv'})
            ):
                if file_format_filter == 'none' or file_format_filter is None or post.url.endswith(file_format_filter):
                    filename = os.path.join(dir_path, post.id + '.' + file_extension)
                    if os.path.exists(filename):
                        print('File already exists:', filename)
                        downloaded_posts.add(post)
                        continue
                    thread = threading.Thread(target=download_file, args=(post, filename))
                    threads.append(thread)
                    thread.start()
                    if len(threads) >= MAX_NUM_THREADS:
                        for thread in threads:
                            thread.join()
                        threads = []

for thread in threads:
    thread.join()
