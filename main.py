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
@click.option("--query-until", nargs=3, type=int, help="Obtain submissions from up to YEAR(s) MONTH(s) DAY(s) ago from today's date. Example --query-until 1 5 7 obtains results from up to 1 year, 5 months, and 7 days ago.")
def cli(subreddit: str, save_filepath: str, query_until, keywords: bool):
    save_filepath: Path = Path(save_filepath)
    save_folder = save_filepath.parents[0]
    save_filename = save_filepath.stem

    if keywords:
        with open("keywords.txt", "r") as f:
            keywords: list[str] = [line.rstrip() for line in f.readlines()]


    today = datetime.utcnow()
    if query_until is not None:
        years, months, days = query_until
        end_timestamp = today - relativedelta(years=years, months=months, days=days)
    else:
        # Otherwise, obtain results from the last day
        end_timestamp = today - relativedelta(days=1)

    submissions = Subreddit(subreddit).get_submission_results_until(end_timestamp)

    if len(keywords) > 0:

        def contains_keyword(submission: dict, case_insensitive=True) -> list[dict]:
            """Verify if a submission contains a keyword in its title

            Parameters
            ----------
            submission: dict
                Reddit submission in JSON format
            case_insensitive : bool
                True if keywords should be check case insensitive

            Returns
            -------
            bool
                True if the submission's title contained at least one of the keywords
            """
            if case_insensitive:
                title = str(submission["title"]).lower()
            else:
                title = str(submission["title"])

            # Check for exact matches for keywords
            words = set(title.split(" "))
            return any([keyword in words for keyword in keywords])

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
