#!/usr/bin/python2.7
'''
First version created on 2012-06-25
@author: Everett Wetchler (evee746)
'''

import csv
import datetime
import sys
import time

from BeautifulSoup import BeautifulSoup
from absl import flags as gflags
from selenium import webdriver

CHROME_DRIVER_PATH = 'chromedriver_win32\chromedriver.exe'
MATCH_URL = 'http://www.okcupid.com/match'


def extract_usernames(html):
    '''Parse the match search result page for usernames.'''
    soup = BeautifulSoup(html)
    usernames = soup.findAll(name='span', attrs={'class': 'username-text'})
    usernames = [u.a['href'] for u in usernames]
    plaintext_usernames = []
    for u in usernames:
        try:
            plaintext_usernames.append(str(u))
        except UnicodeError, e:
            print 'Skipping funky username', u
    print 'Found %d viable usernames' % len(plaintext_usernames)
    # print plaintext_usernamess
    return plaintext_usernames


#####################################################################
# Main
#####################################################################


def main(argv):

    outfile = 'usernames_%s.csv' % (
        datetime.date.today().strftime('%Y%m%d'))
    print 'Saving to:', outfile
    f = open(outfile, 'a')
    writer = csv.writer(f, lineterminator='\n')
    all_usernames = []

    # look into itertools.repeat for this instead
    browser = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH)
    for run in range(100):
        print 'Sleeping...',
        time.sleep(10)  # Avoid throttling by OKC servers
        print 'querying...',
        browser.get(MATCH_URL)
        print 'done.'#, r.url

        usernames = extract_usernames(browser.page_source)#.text)
        # Write incrementally in case the program crashes
        for u in usernames:
            writer.writerow([u])
        f.flush()
        all_usernames.extend(usernames)

    f.close()
    print 'Found %d total users' % len(all_usernames)


if __name__ == '__main__':
    main(sys.argv)