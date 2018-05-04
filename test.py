from BeautifulSoup import BeautifulSoup
import regex
import pandas as pd

import OKCutil

print('Loading locally saved profile in \'htmltest.html\' ... \n')

html = open('htmltest.html').read()

soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)

basics_soup = soup.find(name = 'div', attrs = {'class': 'userinfo2015-basics'})
sidebar_soup = soup.find(name='div', attrs={'class':'profile2015-content-sidebar'})
essays_soup = soup.findAll(name='div', attrs={'class':'profile-essay'})
if not (basics_soup and sidebar_soup and essays_soup):
    print 'Profile likely deleted. Missing expected html structure.'
    profile = pd.DataFrame()
    input('Kill the program when you\'re done')

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

print('done')