import click
import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from statistics import mean

import FrequencyCounter
import FileParser

SAMPLE_TYPE_KEY = 'sample_type'
NOT_CONTAINS_N_KEY = 'contains_n'
PREDICTION_KEY = 'prediction'


def train_file_to_freqs(file, sample_type):
    counts_list = []
    for line in FileParser.train_sample_generator(file):
        counts = FrequencyCounter.count_freq(line)[0]
        counts[SAMPLE_TYPE_KEY] = sample_type
        counts_list.append(counts)
    df = pd.DataFrame(counts_list)
    return df


def create_train_df(neagtive_file, positive_file):
    df_neg = train_file_to_freqs(neagtive_file, False)
    df_pos = train_file_to_freqs(positive_file, True)
    return pd.concat([df_neg, df_pos], ignore_index=True)


def create_target_df(target_file):
    training_list = []
    for seq in FileParser.fasta_sample_generator(target_file):
        counts, non_n = FrequencyCounter.count_freq(seq)
        counts[NOT_CONTAINS_N_KEY] = non_n
        training_list.append(counts)
    training_df = pd.DataFrame(training_list)
    return training_df


@click.command()
@click.option('--negative_samples_file', '-n', type=click.File('r'), required=True)
@click.option('--positive_samples_file', '-p', type=click.File('r'), required=True)
@click.option('--target_file', '-t', type=click.File('r'), required=True)
@click.option('--out_file', '-o', type=click.File('w'), required=True)
def main(negative_samples_file, positive_samples_file, target_file, out_file):
    #  Model training:
    train_df = create_train_df(negative_samples_file, positive_samples_file)
    train_df, test_df = train_test_split(train_df, test_size=0.15, random_state=123)
    model = RandomForestClassifier()
    # model = XGBClassifier()
    model.fit(train_df.loc[:, train_df.columns != SAMPLE_TYPE_KEY], train_df.loc[:, SAMPLE_TYPE_KEY])

    #  Accuracy counting:
    y_pred = model.predict_proba(test_df.iloc[:, train_df.columns != SAMPLE_TYPE_KEY])
    predictions = [round(value[1]) for value in y_pred]
    accuracy = accuracy_score(test_df.loc[:, SAMPLE_TYPE_KEY].astype(int), predictions)
    print("Accuracy: %.2f%%" % (accuracy * 100.0))

    #  First run (only non-n elements):
    target_df = create_target_df(target_file)
    print(target_df)
    non_n_df = target_df[target_df[NOT_CONTAINS_N_KEY]].drop(columns=[NOT_CONTAINS_N_KEY])
    non_n_preds = model.predict_proba(non_n_df)
    print(non_n_df)
    avg_result = mean(non_n_preds[:, 1])
    print(f'Average probability = {avg_result}')

    #  Second run (replace n-containing elements with mean):
    target_preds = model.predict_proba(target_df.drop(columns=[NOT_CONTAINS_N_KEY]))
    target_df[PREDICTION_KEY] = target_preds[:, 1]
    print(target_preds[:, 1])
    mask = target_df[NOT_CONTAINS_N_KEY] == False
    target_df.loc[mask, PREDICTION_KEY] = avg_result

    #  Print to file:
    # print('track type=wiggle_0 name="chr2L_200_100_fly_nomodifications_4mers" description="Prediction of enhancers of Drosophila melanogaster based on 4mers with frame_length=200 and step_length=100." visibility=full autoScale=off vieLimits=0.0:1.0 color=50,150,255 yLineMark=11.76 yLineOnOff=on priority=10', file=out_file)
    # print('fixedStep chrom=chr21 start=1 step=1500 span=750', file=out_file)
    print('track type=wiggle_0 name="db=vista tissue=both histmods= kmers=4mers chrom=chr21.id" description="enhancers prediction"  visibility=full autoScale=off vieLimits=0.0:1.0 color=50,150,255 yLineMark=11.76 yLineOnOff=on priority=10', file=out_file)
    print('variableStep chrom=chr21 span=1500', file=out_file)
    i = 1
    for pred in target_df[PREDICTION_KEY]:
        print(f'{i} {pred:.6f}', file=out_file)
        i += 750


if __name__ == "__main__":
    main()