#!/bin/bash

# Usage: ./crawler.sh --subreddits subreddit1 subreddit2 --limit 100 --depth 5

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "Python could not be found, please install Python 3."
    exit
fi

# Run the Python crawler script with parameters passed to this shell script
python3 reddit_crawler.py "$@"
