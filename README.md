# Reddit Downloader

Reddit Downloader is a Python script that allows you to download media files (photos, audio, and videos) from a specified subreddit on Reddit. You can filter the files by type, format, and word patterns in the post titles. The script supports multithreading to download files faster, and it uses the `praw` and `requests` libraries to interact with the Reddit API and download files, respectively.

## Getting Started

1. Clone or download this repository to your computer.
2. Install the required packages listed in the `requirements.txt` file. You can use the following command in your terminal or command prompt:
   ```
   pip install -r requirements.txt
   ```
3. Obtain the credentials for your Reddit app and update the script accordingly. You can follow the instructions in the comments of the script or visit the [Reddit API documentation](https://www.reddit.com/dev/api/) for more information.
4. Run the script in your terminal or command prompt:
   ```
   python reddit_downloader.py
   ```
5. Follow the prompts to enter the subreddit name, file type filter, file format filter, sorting mechanism, and word patterns.

The downloaded files will be saved in a new directory with the same name as the subreddit in the current working directory.

## Limitations

- The script can download up to 50 files at a time. You can change this limit by modifying the `MAX_NUM_FILES` variable in the script.
- The script can use up to 100 threads to download files concurrently. You can change this limit by modifying the `MAX_NUM_THREADS` variable in the script.
- The script may not download some files if they are not accessible or their URLs are invalid.
- The script may not download some files if they do not match the specified filters or if they have already been downloaded before.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.
