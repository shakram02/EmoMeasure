import re
import string
import sys
from collections import Counter, OrderedDict

from nltk.corpus import stopwords
from nltk.stem.lancaster import LancasterStemmer

from emoMeasure.utils.file_utils import get_directory_name, get_file_name, make_directory, create_file_path, \
    get_file_names


class TweetEntry(object):
    def __init__(self, tweet_id, text, feel, intensity):
        self.tweet_id: str = tweet_id
        self.text: str = text
        self.feel: str = feel
        self.intensity: str = intensity

    def __str__(self):
        return "{}\t{}\t{}".format(self.text, self.feel, self.intensity)


def partitionize(raw_lines):
    result = []
    for line in raw_lines:
        split_line = line.split("\t")
        split_line = split_line[1:]  # Remove tweet id
        tweet = split_line[0]
        feeling = split_line[1]
        intensity = split_line[2].split(":")[0]  # Take the number of sadness amount only
        result.append([tweet, feeling, intensity])
    return result


def strip_mentions(text_lines):
    mention_pattern = re.compile("@\w+")
    # $ % & '()*+,-./:;<=>?@[\]^_`{|}~
    return [mention_pattern.sub('', l) for l in text_lines]


def strip_punctuation(text_lines):
    translator = str.maketrans('', '', string.punctuation)
    return [l.translate(translator) for l in text_lines]


def strip_redundant_chars_words(text_lines):
    """
    Removes stop words then stems the remaining words
    """

    stop_words = set(stopwords.words('english'))
    result = []
    st = LancasterStemmer()

    for i, line in enumerate(text_lines):
        split_line = line.split()
        resultwords = [st.stem(word.strip()) for word in split_line if word not in stop_words]
        result.append(' '.join(resultwords))

    return result


def strip_extra_space(text_lines):
    space_remover = re.compile("\s{2,}")
    return [space_remover.sub(" ", x.strip()) for x in text_lines]


def strip(tweet_lines):
    """
    Removes unwanted charactes from tweets on multiple stages
    """
    mention_stripped = strip_mentions(tweet_lines)
    del tweet_lines

    stopwords_stripped = strip_redundant_chars_words(mention_stripped)
    del mention_stripped

    puncutation_stripped = strip_punctuation(stopwords_stripped)
    del stopwords_stripped

    space_stripped = strip_extra_space(puncutation_stripped)
    del puncutation_stripped

    return space_stripped


def read_raw_lower_cased(file_name):
    """
    Loads all text as a single string from data.
    """

    # load data
    fd = open(file_name, encoding='UTF-8')

    text = fd.read()
    text = text.replace("\\n", " ")
    return text.lower()


def print_stats(stripped_text, file=sys.stdout):
    """
    Creates some statistics about the provided text like word count
    """
    # filter out stop words
    words = []
    for line in stripped_text:
        words += line.split(" ")

    counter = Counter(words)
    import pprint as pp

    count = 0
    for en in counter:
        if counter[en] != 1:
            continue
        count += 1

    # print(count)
    # print("Total count of items:", len(counter))
    # print(len(counter.most_common(1)))
    pp.pprint(OrderedDict(counter.most_common()), stream=file)


def preprocess(file_name):
    text = read_raw_lower_cased(file_name)

    text_lines = text.split("\n")
    text_lines = list(filter(None, text_lines))  # Remove empty entries

    result = partitionize(text_lines[1:])  # Remove first line

    # Cleanup
    del text
    del text_lines

    stripped_text = strip([data_line[0] for data_line in result])

    # Insert the stripped twees to their place
    for i, data_line in enumerate(result):
        result[i][0] = stripped_text[i]

    return result


def main():
    check_debug = getattr(sys, 'gettrace', None)
    if check_debug():
        # In debug mode
        # file_name = input("Filename:")
        file_names = get_file_names("../../dataset/english_train/", extension="txt")
    else:
        file_names = sys.argv[1:]

    for file_name in file_names:
        processed_input = preprocess(file_name)

        dir_name = get_directory_name(file_name)
        dataset_name = get_file_name(file_name)
        out_folder = make_directory("stats_" + dataset_name, dir_name)

        out_path = create_file_path(dataset_name + "_out", out_folder)
        tweet_out_path = create_file_path(dataset_name + "_tweet_out", out_folder)

        out_file = open(out_path, mode='w')
        tweet_file = open(tweet_out_path, mode='w')

        # TODO write file content
        for entry in processed_input:
            # Write only factor and the tweet
            intensity = entry[2]
            text = entry[0]
            tweet_file.write(" ".join(["__label__" + intensity, text]) + "\n")
            out_file.write(text + "\n")

        tweet_file.close()
        print_stats([x[0] for x in processed_input], out_file)
        out_file.close()


if __name__ == "__main__":
    main()
