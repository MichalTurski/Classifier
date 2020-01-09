

def train_sample_generator(file):
    for line in file:
        if line[0] != '>':
            yield line.upper()


def fasta_sample_generator(file):
    pass
