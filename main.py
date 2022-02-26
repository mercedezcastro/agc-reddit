from datetime import datetime
from pathlib import Path

import click
import pandas as pd
from dateutil.relativedelta import relativedelta

from models import Subreddit


@click.command()
@click.argument("subreddit")
@click.argument("save_filepath")
@click.option(
    "--keywords/--no-keywords",
    default=True,
    help="Filter Subreddit titles by keywords listed in keywords.txt. Generates a separate CSV from SAVE_FILENAME with keywords prefix.",
)
def cli(subreddit: str, save_filepath: str, keywords: bool):
    save_filepath: Path = Path(save_filepath)
    save_folder = save_filepath.parents[0]
    save_filename = save_filepath.stem

    if keywords:
        with open("keywords.txt", "r") as f:
            keywords: list[str] = [line.rstrip() for line in f.readlines()]

    today = datetime.utcnow()
    last_year = today - relativedelta(years=1)
    submissions = Subreddit(subreddit).get_submission_results_until(last_year)

    if len(keywords) > 0:

        def contains_keyword(submission: dict):
            title = str(submission["title"]).lower()
            return any([keyword in title for keyword in keywords])

        keyword_submissions = list(filter(contains_keyword, submissions))

    def submission_to_record(s: dict):
        title = s["title"]
        created_date = str(datetime.fromtimestamp(s["created_utc"]).date())
        url = f"https://www.reddit.com/{s['permalink']}"
        return (title, created_date, url)

    submissions = [submission_to_record(s) for s in submissions]
    keyword_submissions = [submission_to_record(s) for s in keyword_submissions]

    columns = ["title", "created_date", "url"]
    submissions_df = pd.DataFrame(submissions, columns=columns)
    keyword_submissions_df = pd.DataFrame(keyword_submissions, columns=columns)

    submissions_df.to_csv(save_folder.joinpath(f"{save_filename}.csv"), index=False)
    keyword_submissions_df.to_csv(
        save_folder.joinpath(f"keywords_{save_filename}.csv"), index=False
    )


if __name__ == "__main__":
    cli()
