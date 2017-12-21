import itertools
import operator

import numpy as np
from fastText import train_supervised
from fastText.util import test

result_set = {}


class SteppedValues(object):
    def __init__(self, min_val, max_val, delta):
        self._min_val = min_val
        self._max_val = max_val
        self._delta = delta

    def generate(self):
        return np.arange(self._min_val, self._max_val, self._delta)


# Return top-k predictions and probabilities for each line in the given file.
def get_predictions(filename, model, k=1):
    predictions = []
    probabilities = []
    with open(filename) as f:
        for line in f:
            line = line.strip()
            labels, probs = model.predict(line, k)
            predictions.append(labels)
            probabilities.append(probs)
    return predictions, probabilities


# Parse and return list of labels
def get_labels_from_file(filename, prefix="__label__"):
    labels = []
    with open(filename) as f:
        for line in f:
            line_labels = []
            tokens = line.split()
            for token in tokens:
                if token.startswith(prefix):
                    line_labels.append(token)
            labels.append(line_labels)
    return labels


def gen_parameters(wordNgrams_vals, lr_vals):
    l = list(itertools.product(wordNgrams_vals.generate(), lr_vals.generate()))
    return sorted(l, key=lambda x: x[1])


def main():
    valid_data = "/mnt/Exec/code/python/EmoMeasure/dataset/english_dev/stats_2018-EI-oc-En-joy-dev/2018-EI-oc-En-joy-dev_tweet_out.txt"
    train_data = "/mnt/Exec/code/python/EmoMeasure/dataset/english_train/stats_EI-oc-En-joy-train/EI-oc-En-joy-train_tweet_out.txt"

    lr_vals = SteppedValues(0.5, 1, 0.1)
    wordNgrams_vals = SteppedValues(1, 9, 1)
    parameters = gen_parameters(wordNgrams_vals, lr_vals)

    for ngram, lr in parameters:
        # train_supervised uses the same arguments and defaults as the fastText cli
        print("Params ngrams:{} lr:{} ".format(ngram, lr))
        model = train_supervised(
            input=train_data, epoch=500, lr=lr, wordNgrams=ngram, verbose=2, minCount=1, thread=4
        )
        k = 1
        predictions, _ = get_predictions(valid_data, model, k=k)
        valid_labels = get_labels_from_file(valid_data)
        p, r = test(predictions, valid_labels, k=k)

        print("N:" + str(len(valid_labels)) + "\tP:{:.3f}".format(p))
        print("\n")
        result_set["{}-{}".format(lr, ngram)] = p
        # print("Saving model")
        # model.save_model(train_data + '.bin')

    print_stats()


def print_stats():
    import pprint

    sorted_result = sorted(result_set.items(), key=operator.itemgetter(1), reverse=True)
    pprint.pprint(sorted_result)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_stats()
