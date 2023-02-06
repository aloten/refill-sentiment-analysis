import nltk
import os
import sys


def main():
    # Read data from files
    corpus_path = "../resources/corpus"
    positives, negatives = load_data(corpus_path)

    # Create a set of all words
    words = set()
    for document in positives:
        words.update(document)
    for document in negatives:
        words.update(document)
    words.remove("refill")

    # generate frequency map
    frequency_map = generate_frequency_map(words, positives, negatives)

    # get string to classify
    # s = "please cancel"
    while True:
        s = input("s: ")
        if s == "quit":
            return
        if catch_refill_variation(s):
            result = "100% probability of wanting a refill"
            print(result)
        else:
            # sum the probability that each word is in positives
            p_positive = get_probability_value_sum(s, frequency_map, "positive")
            # sum the probability that each word is in negatives
            p_negative = get_probability_value_sum(s, frequency_map, "negative")
            adjusted_p_positive = p_positive / (p_positive + p_negative) * 100
            result = f"{adjusted_p_positive:.3f}% probability of wanting a refill"
            print(result)


def catch_refill_variation(s):
    if s.strip() in {
        'refill',
        'reffil',
        'refil',
        'please refill',
        'please refill',
        'yes',
        'yes please',
        'send',
        'refill please'
    }:
        return True


def get_probability_value_sum(s, frequency_map, type):
    document_words = extract_words(s)
    p_sum = 0
    for word in document_words:
        p = get_probability_value(word, frequency_map, type)
        p_sum += p
    return p_sum


def calculate_negative_modifier(token):
    if token in {
        "cancel",
        "no",
        "not",
            "don't"}:
        return 1000
    return 1


def get_probability_value(token, frequency_map, type):
    count_token = 1
    try:
        count_token = frequency_map[token][f"{type}_frequency"] + 1
    finally:
        count_total = frequency_map[f"total_{type}_tokens"]
        p = count_token / count_total
        if (type == 'negative'):
            p_adjusted = p * calculate_negative_modifier(token)
            return p_adjusted
        return p


def generate_frequency_map(words, positives, negatives):
    frequency_map = {}
    total_positive_tokens = 0
    total_negative_tokens = 0
    for word in words:
        positive_frequency = 0
        for document in positives:
            for token in document:
                if word == token:
                    positive_frequency += 1
                total_positive_tokens += 1
        negative_frequency = 0
        for document in negatives:
            for token in document:
                if word == token:
                    negative_frequency += 1
                total_negative_tokens += 1
        frequency_map[word] = {
            "positive_frequency": positive_frequency,
            "negative_frequency": negative_frequency
        }
    frequency_map["total_positive_tokens"] = total_positive_tokens
    frequency_map["total_negative_tokens"] = total_negative_tokens
    return frequency_map


def load_data(directory):
    result = []
    for filename in ["positives.txt", "negatives.txt"]:
        with open(os.path.join(directory, filename)) as f:
            result.append([
                extract_words(line)
                for line in f.read().splitlines()
            ])
    return result


def extract_words(document):
    return set(
        word.lower() for word in nltk.word_tokenize(document)
        if any(c.isalpha() for c in word)
    )


if __name__ == "__main__":
    main()
