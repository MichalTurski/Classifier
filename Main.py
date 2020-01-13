import click
import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

import FrequencyCounter
import FileParser

SAMPLE_TYPE_KEY = 'sample_type'


def train_file_to_freqs(file, sample_type):
    counts_list = []
    for line in FileParser.train_sample_generator(file):
        counts = FrequencyCounter.count_freq(line)
        counts[SAMPLE_TYPE_KEY] = sample_type
        counts_list.append(counts)
    df = pd.DataFrame(counts_list)
    return df


def create_train_df(neagtive_file, positive_file):
    df_neg = train_file_to_freqs(neagtive_file, False)
    df_pos = train_file_to_freqs(positive_file, True)
    return pd.concat([df_neg, df_pos], ignore_index=True)


def create_target_df(target_file):
    counts_list = []
    for seq in FileParser.fasta_sample_generator(target_file):
        counts = FrequencyCounter.count_freq(seq)
        counts_list.append(counts)
    df = pd.DataFrame(counts_list)
    return df


@click.command()
@click.option('--negative_samples_file', '-n', type=click.File('r'), required=True)
@click.option('--positive_samples_file', '-p', type=click.File('r'), required=True)
@click.option('--target_file', '-t', type=click.File('r'), required=True)
def main(negative_samples_file, positive_samples_file, target_file):
    train_df = create_train_df(negative_samples_file, positive_samples_file)
    train_df, test_df = train_test_split(train_df, test_size=0.25, random_state=123)
    model = XGBClassifier()
    model.fit(train_df.loc[:, train_df.columns != SAMPLE_TYPE_KEY], train_df.loc[:, SAMPLE_TYPE_KEY])
    print(model)

    y_pred = model.predict(test_df.iloc[:, train_df.columns != SAMPLE_TYPE_KEY])
    predictions = [round(value) for value in y_pred]
    print(test_df.loc[:, SAMPLE_TYPE_KEY])
    accuracy = accuracy_score(test_df.loc[:, SAMPLE_TYPE_KEY].astype(int), predictions)
    print("Accuracy: %.2f%%" % (accuracy * 100.0))

    target_df = create_target_df(target_file)
    print(target_df)
    target_pred = model.predict(target_df)
    print(target_pred)


if __name__ == "__main__":
    main()