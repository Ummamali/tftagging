import nltk
from nltk.corpus import wordnet as wn
from collections import Counter


def find_representative_words(similar_words):
    # Initialize a frequency Counter to store counts of hypernyms
    hypernym_counts = Counter()

    # Iterate through each word
    for word in similar_words:
        # Get synsets (a set of synonyms) for the word
        synsets = wn.synsets(word)
        for synset in synsets:
            # Get hypernyms (more general terms) for the synset
            hypernyms = synset.hypernyms()
            # Increment count for each hypernym
            for hypernym in hypernyms:
                hypernym_name = hypernym.name().split(".")[
                    0
                ]  # Extract the hypernym name
                hypernym_counts[hypernym_name] += 1

    # Find the three most common hypernyms
    most_common_hypernyms = hypernym_counts.most_common(3)

    return most_common_hypernyms
