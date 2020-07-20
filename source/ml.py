import pandas as pd
import random as rd
import numpy as np
from itertools import combinations
from math import ceil, floor


def random_setify(df, train_pct, valid_pct):
    """
    Take a classifier and split into training, validation and testing sets randomly.
    @param df dataframe of extracted attributes;
    @param train_pct percentage of samples in training set;
    @param valid_pct percentage of samples in validation set;
    @return tuple with the three sets.
    """

    # check if arguments are valid
    if train_pct + valid_pct > 1:
        raise ValueError('Train percentage and Validation percentage can\'t be above 1')

    # determine size of the sets
    train_len = ceil(df.shape[0] * train_pct)
    valid_len = floor(df.shape[0] * valid_pct)
    test_len = df.shape[0] - train_len - valid_len

    # DataFrames of the sets
    train_df = pd.DataFrame(columns=df.columns) if train_len > 0 else None
    valid_df = pd.DataFrame(columns=df.columns) if valid_len > 0 else None
    test_df = pd.DataFrame(columns=df.columns) if test_len > 0 else None

    # split the entries according to state
    state_columns = [i for i in df.columns if 'state' in i]
    states = [i.split('_')[-1] for i in state_columns]
    index = {s: [] for s in states}
    for i in df.index:
        for column, state in zip(state_columns, states):
            if df.at[i, column] == 1:
                index[state].append(i)
                break

    # initialize result
    train_index = []
    valid_index = []

    # get training indexes randomly
    for _ in range(train_len//len(states)):
        for j in states:
            train_index.append(rd.choice(index[j]))
            index[j].remove(train_index[-1])

    # get validation indexes randomly
    for _ in range(valid_len//len(states)):
        for j in states:
            valid_index.append(rd.choice(index[j]))
            index[j].remove(valid_index[-1])

    # testing gets remaining indexes
    test_index = [i for i in index[j] for j in index.keys()]

    # populate the sets with selected indexes
    if train_df is not None:
        for i in train_index:
            train_df = train_df.append(df.loc[i])
    if valid_df is not None:
        for i in valid_index:
            valid_df = valid_df.append(df.loc[i])
    if test_df is not None:
        for i in test_index:
            test_df = test_df.append(df.loc[i])

    return train_df, valid_df, test_df


def generate_1x1_classifiers(df, states):
    """
    """

    classifiers = {}

    # each classifier decides between two states
    for comb in combinations(states, 2):

        # get for each combination
        states = [f'state_{j}' for j in comb]

        # leave only inputs of desired states
        classifier = [
            df.query(f'{s}==1').drop(
                [j for j in df.columns if 'state' in j], axis=1
            ) for s in states
        ]

        # first state is labeled as 1 and second as -1
        classifier[0]['state'] = (classifier[0].shape[0])*[1]
        classifier[1]['state'] = (classifier[1].shape[0])*[-1]

        # join states
        classifier = classifier[0].append(classifier[1])

        # append result
        classifiers[f'{comb[0]}_{comb[1]}'] = classifier

    return classifiers