import regex
import pandas as pd

# maybe these should be pulled from a csv
basicskws = {'orientation': ['straight', 'gay', 'bisexual', 'asexual',
                             'demisexual', 'heteroflexible', 'homoflexible',
                             'lesbian', 'pansexual', 'queer', 'questioning',
                             'sapiosexual'],
             'gender': ['woman', 'man', 'agender', 'androgynous',
                        'bigender', 'cis man', 'cis woman',
                        'genderfluid', 'genderqueer',
                        'gender nonconforming', 'hijra', 'intersex',
                        'binary', 'other', 'pangender', 'transfeminine',
                        'transgender', 'transmasculine', 'transsexual',
                        'trans man', 'trans woman'],
             'status': ['single', 'seeing', 'married', 'open'],
             'monogamous': ['monogamous', u'non\u2011monogamous'],
             'build': ['rather', 'thin', 'overweight', 'average', 'fit',
                       'jacked', 'extra', 'full', 'curvy', 'used'],
             }

backgroundkws = {'ethnicity': ['asian', 'black', 'hispanic / latin', 'indian',
                               'middle eastern', 'native american',
                               'pacific islander', 'white', 'other ethnicity',
                               'multi-ethnic'],
                 'ed_prefix': ['attended', 'working on', 'dropped out of'],
                 'education': ['high school', 'two-year college',
                               'university', 'space camp', 'post grad'],
                 'religion_pre': [u'it\u2019s important', u'not important',
                                  'laughing about it'],
                 'religion': ['agnostic', 'atheist', 'christian', 'jewish',
                              'catholic', 'muslim', 'hindu', 'buddhist',
                              'sikh', 'other religion'],
                 }

misckws = {'kids_present': [u'doesn\u2019t have kids', 'has kids'],
           'kids_future': ['but might want them', 'but wants them',
                           u'doesn\u2019t want them'],
           'dogs': ['dogs'],
           'cats': ['cats'],
           'sign': ['aquarius', 'pisces', 'aries', 'taurus',
                    'gemini', 'cancer', 'leo', 'virgo', 'libra',
                    'scorpio', 'sagittarius', 'capricorn'],
           'diet': ['omnivore', 'vegetarian', 'vegan', 'kosher', 'halal']
           }

lookingkws = {'lf_gender': ['women', 'men', 'people'],
              'lf_status': ['single'],
              'lf_rel_type': ['short', 'long', 'hookup', 'friends'],
              'lf_monogamous': ['monogamous'],
              }


def parse_basics(text):
    print(text.encode('utf-8'))
    df = pd.DataFrame()

    feetinches = regex.findall('\d+', text)
    if not any(feetinches):
        df['height'] = None
    else:
        df['height'] = [(int(feetinches[0]) * 12) + int(feetinches[1])]

    # Return as lists
    listvals = ['orientation', 'gender']
    for category in listvals:
        values = []
        for kw in basicskws[category]:
            match = regex.findall(r'\b(%s)\b' % kw, text)
            if any(match):
                values.append(match[0])
        if not any(values):
            df[category] = None
        else:
            df[category] = [values]

    # Single values
    for category in list(filter(lambda key: key not in listvals,
                                basicskws.keys())):
        values = [kw for kw in basicskws[category] if kw in text]
        if not any(values):
            df[category] = None
        else:
            df[category] = values

    print(df)
    return df


def parse_background(text):
    print(text.encode('utf-8'))
    df = pd.DataFrame()

    # Return as lists
    listvals = ['ethnicity']
    for category in listvals:
        values = []
        for kw in backgroundkws[category]:
            if kw in text:
                values.append(kw)
                text = regex.sub(kw, '', text)
        if not any(values):
            df[category] = None
        else:
            df[category] = [values]

    # Single values
    for category in list(filter(lambda key: key not in listvals,
                                backgroundkws.keys())):
        value = [kw for kw in backgroundkws[category] if kw in text]
        if not any(value):
            df[category] = None
        else:
            df[category] = value
            text = regex.sub(r'%s' % value[0], '', text)

    secondary = regex.findall(r'(?<=some\s)(\w+)', text)
    if not any(secondary):
        df['lang_secondary'] = None
    else:
        df['lang_secondary'] = [[lang for lang in secondary]]

    text = regex.sub(r'some\s\w+|speaks|and|but|it\u2019s', '', text)

    primary = regex.findall(r'\w+', text)
    if not any(primary):
        df['lang_primary'] = None
    else:
        df['lang_primary'] = [[lang for lang in primary]]

    print(df)
    return df


def parse_misc(text):
    print(text.encode('utf-8'))
    df = pd.DataFrame()

    # OKC alters the word order and words themselves depending on
    # user answers, making it difficult to generate regexes dynamically
    # This method isn't as pretty as I would like, but it gets the job done.
    categories = ['smokes', 'drinks', 'drugs']
    # sometimes uses 'do drugs', sometimes 'does drugs'
    terms = ['smokes', 'drinks', 'doe?s? drugs']
    matches = [regex.findall(r'\w+(?= %s)|(?<=%s )\w+' % (terms[0], terms[0]), text),
               regex.findall(r'\w+(?= %s)|(?<=%s )\w+' %
                             (terms[1], terms[1]), text),
               regex.findall(
                   r'[\w(?:\u2019)]+(?= %s)|(?<=%s )[\w(?:\u2019)]+' % (terms[2], terms[2]), text),
               ]

    # standardize and assign values
    for category, match in zip(categories, matches):
        if not any(match):
            df[category] = None
        elif (match[0] == 'regularly') | (match[0] == 'often'):
            df[category] = ['yes']
        elif (match[0] == 'never') | (match[0] == u'doesn\u2019t'):
            df[category] = ['no']
        else:
            df[category] = match

    # Get the rest of the values using simple keyword search
    for category, kws in misckws.items():
        values = [kw for kw in kws if kw in text]
        if not any(values):
            df[category] = None
        else:
            df[category] = values

    print(df)
    return df


def parse_lookingfor(text):
    print(text.encode('utf-8'))
    df = pd.DataFrame()

    # Numerical data
    # Possible for user to select 'Anywhere' instead of a number range
    dist = regex.findall(r'within (\d+) (\w+)', text)
    if any(dist):
        if dist[0][1] == 'km':
            df['lf_dist'] = [int(int(dist[0][0]) * 0.621371)]
        else:
            df['lf_dist'] = [int(dist[0][0])]
    elif any(regex.findall(r'anywhere', text)):
        df['lf_dist'] = [-1]
    else:
        df['lf_dist'] = None

    # Possible for users to select a single 'lookingfor' age
    lf_age_lower = regex.findall(r'\d+(?=\u2011)', text)
    if any(lf_age_lower):
        df['lf_age_lower'] = [int(lf_age_lower[0])]
        df['lf_age_upper'] = [int(regex.findall(r'(?<=\u2011)\d+', text)[0])]
    else:
        lf_age = [int(regex.findall(r'(?<=age )\d+', text)[0])]
        df['lf_age_lower'] = lf_age
        df['lf_age_upper'] = lf_age

    # Can result in a list of strings
    df['lf_rel_type'] = [[kw for kw in lookingkws['lf_rel_type'] if kw in text]]

    # Single entries. lf_gender needs a custom loop with a break so that 'men'
    # doesn't match twice with 'women' and 'men'
    for kw in lookingkws['lf_gender']:
        if kw in text:
            df['lf_gender'] = [kw]
            break
    df['lf_status'] = [kw if kw in text else None for kw in lookingkws['lf_status']]
    df['lf_monogamous'] = [
        kw if kw in text else None for kw in lookingkws['lf_monogamous']]

    print(df)
    return df
