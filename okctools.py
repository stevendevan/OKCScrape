# shebang?

#

import pandas as pd
import pickle as pkl


def load_profiles_df(filename='profiles.pickle'):
    df = pd.DataFrame()
    profiles = open(filename, 'rb')

    print('Loading file ...')
    try:
        while True:
            temp = pkl.load(profiles)
            df = df.append(temp, ignore_index=True)
    except EOFError:
        print('Finished loading file.')
    finally:
        profiles.close()

    return df
