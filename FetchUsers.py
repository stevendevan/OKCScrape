#!/usr/bin/python2.7
"""
@author: Steven Devan, 05.2018
Adapted from old project by the person mentioned below

ORIGINAL DESCRIPTION
One by one, fetch profile pages for OKCupid users. The input to this script
is a file with a list of usernames of profiles to pull,
Original version created on Jun 25, 2012
Everett Wetchler (evee746)
"""

import csv
import datetime
import random
import sys
import time
import pickle as pkl

from BeautifulSoup import BeautifulSoup, UnicodeDammit
from absl import flags as gflags # workaround since gflags is deprecated
from selenium import webdriver
import pandas as pd
import regex

import OKCutil

CHROME_DRIVER_PATH = 'D:\_proj\python projects\chromedriver_win32\chromedriver.exe'
cookies = [
           {'name':'authlink','value':<YOUR COOKIE VALUE>,'domain':'.okcupid.com'},
           {'name':'nano',
                   'value':<YOUR COOKIE VALUE>,
                   'domain':'.okcupid.com'},
           {'name':'override_session','value':<YOUR COOKIE VALUE>,'domain':'.okcupid.com'},
           {'name':'secure_check','value':<YOUR COOKIE VALUE>,'domain':'.okcupid.com'},
           {'name':'secure_login','value':<YOUR COOKIE VALUE>,'domain':'.okcupid.com'},
           {'name':'session',
                   'value':<YOUR COOKIE VALUE>,
                   'domain':'.okcupid.com'},
          ]


FLAGS = gflags.FLAGS
gflags.DEFINE_string('outfile', 'profiles.csv', 'Filename for output')
gflags.DEFINE_boolean('pull_essays', True,
                      'If True, pulls free responses sections. If False, '
                      'just basic profile details.')
gflags.DEFINE_string('usernames_file','usernames_20180310_unique.csv',
                     'File with usernames to fetch')
gflags.DEFINE_string('completed_usernames_file','completed_usernames.csv',
                     'File with usernames we have already fetched')


SLEEP_BETWEEN_QUERIES = 10
BASE_URL = "http://www.okcupid.com"


def pull_profile_and_essays(browser, username):
    """Given a username, fetches the profile page and parses it."""
    url = BASE_URL + username
    print "Fetching profile HTML for", username + "... ",
    
    html = None
    browser.get(url)

    html = browser.page_source
    if not html:
        print "Giving up."
        return pd.DataFrame()
    print "Parsing..."
    profile = parse_profile_html(html)
    profile['username'] = regex.findall(r'/profile/(.+)\?cf', username)
    return profile


def parse_profile_html(html):
    """Parses a user profile page into the data fields and essays.
    It turns out parsing HTML, with all its escaped characters, and handling
    wacky unicode characters, and writing them all out to a CSV file (later),
    is a pain in the ass because everything that is not ASCII goes out of its
    way to make your life hard.
    During this function, we handle unescaping of html special
    characters. Later, before writing to csv, we force everything to ASCII,
    ignoring characters that don't play well.
    """
    html = html.lower()
    soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)

    basics_soup = soup.find(name = 'div', attrs = {'class': 'userinfo2015-basics'})
    sidebar_soup = soup.find(name='div', attrs={'class':'profile2015-content-sidebar'})
    essays_soup = soup.findAll(name='div', attrs={'class':'profile-essay'})
    if not (basics_soup and sidebar_soup and essays_soup):
        print 'Profile likely deleted. Missing expected html structure.'
        return pd.DataFrame()
    
    basicsTable = sidebar_soup.find(name='table',attrs={'class':'details2015-section basics'})
    if basicsTable is not None:
        basics = OKCutil.ParseBasics(basicsTable.findAll('td')[1].text)
    else:
        basics = pd.DataFrame()
    
    backgroundTable = sidebar_soup.find(name='table',attrs={'class':'details2015-section background'})
    if backgroundTable is not None:
        background = OKCutil.ParseBackground(backgroundTable.findAll('td')[1].text)
    else:
        background = pd.DataFrame()
    
    miscTable = sidebar_soup.find(name='table',attrs={'class':'details2015-section misc'})
    if miscTable is not None:
        misc = OKCutil.ParseMisc(miscTable.findAll('td')[1].text)
    else:
        misc = pd.DataFrame()
    
    lookingforObj = sidebar_soup.find(name='div',attrs={'class':'lookingfor2015-sentence'})
    if lookingforObj is not None:
        lookingfor = OKCutil.ParseLookingfor(lookingforObj.text)
    else:
        lookingfor = pd.DataFrame()
    
    name     = basics_soup.find(name='div',attrs={'class':'userinfo2015-basics-username'}).text
    age      = basics_soup.find(name='span',attrs={'class':'userinfo2015-basics-asl-age'}).text
    location = basics_soup.find(name='span',attrs={'class':'userinfo2015-basics-asl-location'}).text
    city, region = regex.findall(r'(.*?), (.*)',location)[0]
    
    userinfo = pd.DataFrame([{'name':name,
                              'age':age,
                              'city':city,
                              'region':region,
                             }],
                           )
    print(userinfo)

    # the 'essays' column is a list of dicts
    essays_list = []
    if essays_soup is not None:
        for item in essays_soup:
            essays_list.append({'title':item.h2.text.encode('ascii', 'ignore'),
                                'content':item.p.text.encode('ascii', 'ignore')
                               })
        essays = pd.DataFrame([[essays_list]], columns=['essays'])
    else:
        essays = pd.DataFrame()
    
    profile = pd.concat([basics, background, misc, userinfo, essays], axis=1)
    
    return profile


TIMING_MSG = """%(elapsed)ds elapsed, %(completed)d profiles fetched, \
%(skipped)d skipped, \
%(remaining)d left, %(secs_per_prof).1fs per profile, \
%(prof_per_hour).0f profiles per hour, \
%(est_hours_left).1f hours left"""


def compute_elapsed_seconds(elapsed):
    """Given a timedelta, returns a float of total seconds elapsed."""
    return (elapsed.days * 60 * 60 * 24 +
            elapsed.seconds + elapsed.microseconds / 1.0e6)


def read_usernames(filename):
    """Extracts usernames from the given file, returning a sorted list.
    The file should either be:
        1) A list of usernames, one per line
        2) A CSV file with a 'username' column (specified in its header line)
    """
    try:
        rows = [r[0] for r in csv.reader(open(filename))]
        return rows
    except IOError, e:
        # File doesn't exist
        return []


def prepare_flags(argv):
    """Set up flags. Returns true if the flag settings are acceptable."""
    try:
        argv = FLAGS(argv)  # parse flags
    except gflags.FlagsError, e:
        return False
    return FLAGS.usernames_file and FLAGS.outfile


def add_cookies(webdriver,cookie_dict):
    for cookie in cookie_dict:
        webdriver.add_cookie(cookie)


def main(argv):

    # TODO: I don't think this is used anymore
    if not prepare_flags(argv):
        print 'Usage: %s ARGS\\n%s' % (sys.argv[0], FLAGS)
        sys.exit(1)

    usernames_to_fetch = read_usernames(FLAGS.usernames_file)
    if not usernames_to_fetch:
        print 'Failed to load usernames from %s' % FLAGS.usernames_file
        sys.exit(1)
    print 'Read %d usernames to fetch' % len(usernames_to_fetch)

    completed = read_usernames(FLAGS.completed_usernames_file)
    if completed:
        usernames_to_fetch = sorted(set(usernames_to_fetch) - set(completed))
        print '%d usernames were already fetched, leaving %d to do' % (
            len(completed), len(usernames_to_fetch))

    start = datetime.datetime.now()
    last = start
    headers_written = bool(completed)  # Only write headers if file is empty
    skipped = 0
    profile_writer = csv.writer(open(FLAGS.outfile, 'ab'))
    completed_usernames_file = open(FLAGS.completed_usernames_file, 'ab')
    completed_usernames_writer = csv.writer(completed_usernames_file)
    N = len(usernames_to_fetch)
    # browser objects
    browser = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH)
    browser.get(BASE_URL) # need to navigate here before setting cookies
    add_cookies(browser,cookies) # I think cookies have to be added individually

    # Fetch profiles
    for i, username in enumerate(usernames_to_fetch):
        # ** Critical ** so OKC servers don't notice and throttle us
        if i > 0:
            print "Sleeping..."
            elapsed = datetime.datetime.now() - last
            elapsed_sec = elapsed.seconds * 1.0 + elapsed.microseconds / 1.0e6
            time.sleep(SLEEP_BETWEEN_QUERIES)
        # Go ahead
        last = datetime.datetime.now()
        profile = pull_profile_and_essays(browser, username)
        if profile.empty:
            skipped += 1
        else:
            with open('profiles.pickle', 'ab') as f:
                pkl.dump(profile, f)
#            
        completed_usernames_writer.writerow([username])
        completed_usernames_file.flush()
        if i % 10 == 0:
            elapsed = datetime.datetime.now() - start
            secs = compute_elapsed_seconds(elapsed)
            profiles_per_hour = (i+1.0)*3600/secs
            print '\n' + TIMING_MSG % {
                'elapsed': secs,
                'completed': i + 1,
                'skipped': skipped,
                'remaining': N - i - 1,
                'secs_per_prof': secs/(i+1.0),
                'prof_per_hour': profiles_per_hour,
                'est_hours_left': (N - i)/profiles_per_hour,
            }



if __name__ == '__main__':
        main(sys.argv)

