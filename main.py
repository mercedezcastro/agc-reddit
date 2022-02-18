import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import praw
from dotenv import load_dotenv
from tqdm import tqdm


if __name__ == "__main__":

    load_dotenv()

    subreddit: str = os.getenv("REDDIT_SUBREDDIT")
    db_filepath = f"{subreddit}.csv"

    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT"),
    )

    submissions = [
        submission for submission in tqdm(reddit.subreddit(subreddit).new(limit=1000))
    ]

    def submission_to_record(s):
        return (s.title, str(datetime.fromtimestamp(s.created_utc).date()), s.url)

    records = [submission_to_record(s) for s in submissions]
    df = pd.DataFrame(records, columns=["title", "date", "url"])

    df.to_csv(db_filepath, index=False)
