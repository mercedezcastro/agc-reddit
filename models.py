import time
from datetime import datetime

import numpy as np
import requests


class Subreddit:
    def __init__(self, subreddit: str):
        self._subreddit = subreddit

    def get_submission_results_until(self, end_timestamp: datetime, verbose=True):
        """Obtain submission results from a given subreddit until the end_timestamp

        Parameters
        ----------
        end_timestamp : datetime
            Timestamp to stop at

        Returns
        -------
        results : list of Submissions
        """
        results = []

        # Results are limited to 25 records per query
        API_BASE_ENDPOINT = "https://api.pushshift.io/reddit/submission/search"

        epoch = datetime.utcfromtimestamp(0)

        # Timestamp starts from the current time
        timestamp: int = int((datetime.utcnow() - epoch).total_seconds())
        end_timestamp: int = int((end_timestamp - epoch).total_seconds())

        while timestamp > end_timestamp:
            query = (
                f"{API_BASE_ENDPOINT}/?before={timestamp}&subreddit={self._subreddit}"
            )

            if verbose:
                print(
                    f"Retrieving up to 25 posts before: {datetime.fromtimestamp(timestamp)}"
                )

            try:
                # Throttle requests in the case of HTTP 429: Too Many Requests
                backoff_time = 5

                while (r := requests.get(query)) and r.status_code != 200:
                    # Too Many Requests
                    if r.status_code == 429:
                        time.sleep(backoff_time)

                        # Exponential Backoff
                        # https://en.wikipedia.org/wiki/Exponential_backoff
                        backoff_time *= 1.5 + np.random.uniform(0, 5)

            # If an unknown exception occurs, terminate and return the results we have obtained thus far
            except Exception as e:
                print(e)
                return results

            paginated_results: list = r.json()["data"]

            if len(paginated_results) == 0:
                if verbose:
                    print(
                        f"Could not retrieve anymore posts beyond: {datetime.fromtimestamp(timestamp)}"
                    )
                break

            results.extend(paginated_results)
            # Oldest timestamp is our new start point
            timestamp = int(paginated_results[-1]["created_utc"])

        return results
