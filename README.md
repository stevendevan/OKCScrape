# OKCScrape
Scrape OKC profiles into pandas DataFrames for exploration

# Info for recruiters
- Look at [profileparser.py](https://github.com/stevendevan/OKCScrape/blob/master/profileparser.py) for regex work and data extraction
- Look at my [Ipython notebook](https://github.com/stevendevan/OKCScrape/blob/master/OKCScrape_exploration.ipynb) to see how I explore data

I was considering trying to predict word counts for each user based on the other data in their profiles, but decided to leave off at EDA and focus on kaggle competitions and other projects. I may come back to do some modeling on this data at some point.

# Using OKCScrape
As I mention in the code comments, this project is adapted from a [~4-year old project](https://github.com/wetchler/okcupid), back when OKC profiles had tabulated data. Most of the data is now contained in sentences generated from user information, and is much more difficult to extract data from.
## Dependencies
I originally used Python 2.7 for this project, but it could easily be adapted to 3.x
I'm not using a virtual environment, so I'll list the python dependencies here.
- [absl-py](https://pypi.org/project/absl-py/) (the [absl-py github](https://github.com/abseil/abseil-py) has more information)
- [BeautifulSoup](https://pypi.org/project/BeautifulSoup/#description) (This is the old, Python 2.7 version)
- [pandas](https://pypi.org/project/pandas/)
- [regex](https://pypi.org/project/regex/)
- [selenium](https://pypi.org/project/selenium/)

Notes: 

- I'm using regex instead of the built in re module because there was some missing functionality in re
- I don't know that much about absl-py. The original project used gflags, which has now apparently been deprecated in favor of absl-py. You might know of a better way to implement this functionality.
## Other stuff
You'll need the chromedriver executable. This is what selenium will be using to fetch webpages, as opposed to your normal browser. You could probably use another headless browser instead, but this is what I'm using.

[Downloads page for the chromedriver executable](http://chromedriver.chromium.org/downloads)
