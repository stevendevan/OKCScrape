import pickle as pkl
import regex

import pandas as pd


def load_profiles_df(filename='profiles.pickle', version='py2'):
    """load_profiles_df(filename='profiles.pickle', py='py2')
    Load and concatenate all DataFrame rows contained in the pickle file into
    a single DataFrame. This must be done incrementally because the pickle was
    written to incrementally as a safeguard against exceptions during web
    scraping.
    """

    df = pd.DataFrame()
    file = open(filename, 'rb')

    print('Loading file ...')
    try:
        while True:
            if (version == 'py2'):
                temp = pkl.load(file)
            elif (version == 'py3'):
                temp = pkl.load(file, encoding='latin1')
            else:
                print('Invalid version')

            df = df.append(temp, ignore_index=True, sort=False)
    except EOFError:
        print('Finished loading file.')
    finally:
        file.close()

    return df


def count_words(listofdicts):
    words = 0
    for essay in listofdicts:
        words += len(regex.findall(r'\b\w+\b', essay['content']))
    return words
