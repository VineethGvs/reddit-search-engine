import re
import praw
import json
import time
import logging
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps
import argparse

# Set up logging
logging.basicConfig(level=logging.INFO)

# Argument parser setup
parser = argparse.ArgumentParser(description="Reddit Crawler for specified subreddits")
parser.add_argument('--subreddits', nargs='+', help='List of subreddits to crawl')
parser.add_argument('--limit', type=int, help='Post limit for each subreddit')
parser.add_argument('--depth', type=int, help='Comment depth to crawl')
args = parser.parse_args()

# Reddit API initialization with your credentials
reddit = praw.Reddit(
    client_id='',     
    client_secret='',
    user_agent=''
)

# Other global variables
processed_ids = set()
id_lock = threading.Lock()
request_semaphore = threading.Semaphore(50)
wait_time = 100

def rate_limited(max_per_minute):
    """Decorator for rate limiting API calls"""
    min_interval = 60.0 / max_per_minute
    def decorate(func):
        @wraps(func)
        def rate_limited_function(*args, **kwargs):
            with request_semaphore:
                result = func(*args, **kwargs)
                time.sleep(min_interval)
                return result
        return rate_limited_function
    return decorate

def get_comments(comment, depth=0):
    """Fetch and parse comments recursively"""
    comments_list = []
    if depth > 0:
        if isinstance(comment, praw.models.MoreComments):
            comment = comment.comments()
        for reply in comment.replies:
            if isinstance(reply, praw.models.MoreComments):
                continue
            body = getattr(reply, 'body', 'No body available')
            comments_list.append({
                'id': reply.id,
                'body': body,
                'score': reply.score,
                'links': re.findall(r'https?://\S+', body)
            })
            if depth > 1:
                replies = get_comments(reply, depth - 1)
                if replies:
                    comments_list[-1]['replies'] = replies
    return comments_list

@rate_limited(wait_time)
def process_submission(submission_id, comment_depth, subreddit):
    """Process individual Reddit submissions"""
    try:
        submission = reddit.submission(id=submission_id)
    except Exception as e:
        logging.error(f"API call failed: {e}. Retrying...")
        time.sleep(1)  # Backoff before retrying
        return process_submission(submission_id, comment_depth, subreddit)  # Retry the function

    with id_lock:
        if submission.id in processed_ids:
            return None
        processed_ids.add(submission.id)

    post_details = {
        'selftext': submission.selftext,
        'title': submission.title,
        'id': submission.id,
        'score': submission.score,
        'url': submission.url,
        'permalink': submission.permalink,
        'comments': []
    }
    submission.comments.replace_more(limit=None)
    for comment in submission.comments:
        post_details['comments'].append(get_comments(comment, comment_depth))

    file_path = f'reddit_data_{subreddit}.json'
    with open(file_path, 'a') as file:
        json.dump(post_details, file, indent=4)

    logging.info(f"Fetched and processed post: {submission_id} from {subreddit}")
    return post_details

def crawl_subreddit(subreddit, post_limit, comment_depth):
    """Crawl subreddit for posts"""
    submission_ids = [submission.id for submission in reddit.subreddit(subreddit).hot(limit=post_limit)]
    reddit_data = {}
    for sub_id in submission_ids:
        post_details = process_submission(sub_id, comment_depth, subreddit)
        if post_details:
            reddit_data[sub_id] = post_details
            logging.info(f"Completed processing post: {sub_id} in {subreddit}")
    return reddit_data

def crawl_multiple_subreddits(subreddits, post_limit, comment_depth):
    """Crawl multiple subreddits"""
    all_data = {}
    for subreddit in subreddits:
        all_data[subreddit] = crawl_subreddit(subreddit, post_limit, comment_depth)
        logging.info(f"Completed crawling subreddit: {subreddit}")
    with open('reddit_data_multiple.json', 'w') as outfile:
        json.dump(all_data, outfile, indent=4)
    return all_data

# Main execution logic
if __name__ == "__main__":
    if not args.subreddits or not args.limit or not args.depth:
        print("Missing arguments, use --help for more information")
    else:
        result = crawl_multiple_subreddits(args.subreddits, args.limit, args.depth)
        print("finished crawling!!")
