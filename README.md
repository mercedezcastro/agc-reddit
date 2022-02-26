# Reddit Scraper for AGC

Simple Reddit Scraper to obtain submissions from a subreddit.

## Installation

This project has been tested with python version `3.10.2`

### Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Running

The default way to run this project is to run

```bash
python main.py SUBREDDIT SAVE_FILEPATH
```

### Keywords

The default behavior is to output two CSVs, one with all the results from up to one day ago (configurable by `--query-until` option) and the other is a subset of results where the title matched a keyword in `keywords.txt`

You can configure the list of keywords to check from as a newline separated list in `keywords.txt`.


### Help

You can find more info from

```bash
python main.py --help
```
