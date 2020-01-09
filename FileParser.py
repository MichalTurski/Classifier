

def sample_generator(file):
    for line in file:
        if line[0] != '>':
            yield line.upper()
