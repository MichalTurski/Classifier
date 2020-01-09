import click
import pandas as pd

import FrequencyCounter
import FileParser


SAMPLE_TYPE_KEY = 'sample_type'


def file_to_freqs(file, sample_type):
    counts_list = []
    for line in FileParser.sample_generator(file):
        counts = FrequencyCounter.count_freq(line)
        counts[SAMPLE_TYPE_KEY] = sample_type
        counts_list.append(counts)
    df = pd.DataFrame(counts_list)
    return df


def create_freqs_df(neagtive_file, positive_file):
    df_neg = file_to_freqs(neagtive_file, False)
    df_pos = file_to_freqs(positive_file, True)
    return pd.concat([df_neg, df_pos], ignore_index=True)


@click.command()
@click.option('--negative_samples_file', '-n', type=click.File('r'), required=True)
@click.option('--positive_samples_file', '-p', type=click.File('r'), required=True)
def main(negative_samples_file, positive_samples_file):
    df = create_freqs_df(negative_samples_file, positive_samples_file)
    print(df)


if __name__ == "__main__":
    main()