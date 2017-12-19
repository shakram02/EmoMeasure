import re
import string
import sys
from collections import Counter, OrderedDict

from nltk.corpus import stopwords
from nltk.stem.lancaster import LancasterStemmer


def partitionize(raw_lines):
    result = []
    for line in raw_lines:
        split_line = line.split("\t")
        split_line = split_line[1:]  # Remove tweet id
        tweet = split_line[0]
        feeling = split_line[1]
        intensity = split_line[2]
        result.append([tweet, feeling, intensity])
    return result


def strip_emojis(text_lines):
    emoji_pattern = re.compile('['
                               u'\U00010000-\U0010ffff'
                               u'\U0001F600-\U0001F64F'  # emoticons
                               u'\U0001F300-\U0001F5FF'  # symbols & pictographs
                               u'\U0001F680-\U0001F6FF'  # transport & map symbols
                               u'\U0001F1E0-\U0001F1FF'  # flags (iOS)
                               ']+', flags=re.UNICODE)

    return [emoji_pattern.sub(r'', l) for l in text_lines]


def strip_mentions(text_lines):
    mention_pattern = re.compile("@\w+")
    # $ % & '()*+,-./:;<=>?@[\]^_`{|}~
    return [mention_pattern.sub('', l) for l in text_lines]


def strip_punctuation(text_lines):
    translator = str.maketrans('', '', string.punctuation)
    return [l.translate(translator) for l in text_lines]


def strip_redundant_chars_words(text_lines):
    stop_words = set(stopwords.words('english'))
    result = []
    st = LancasterStemmer()

    for i, line in enumerate(text_lines):
        split_line = line.split()
        resultwords = [st.stem(word) for word in split_line if word not in stop_words]

        result.append(' '.join(resultwords))

    return result


def strip(tweet_lines):
    mention_stripped = strip_mentions(tweet_lines)
    del tweet_lines

    emoji_stripped = strip_emojis(mention_stripped)
    del mention_stripped

    punctuation_stripped = strip_punctuation(emoji_stripped)
    del emoji_stripped

    stopwords_stipped = strip_redundant_chars_words(punctuation_stripped)
    del punctuation_stripped

    return stopwords_stipped


def read_raw(file_name):
    # load data
    fd = open(file_name, encoding='UTF-8')

    text = fd.read()
    return text  # Remove first line


def print_stats(stripped_text):
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

    print(count)
    print("Total count of items:", len(counter))
    # print(len(counter.most_common(1)))
    # pp.pprint(OrderedDict(counter.most_common(1)))


def preprocess(file_name):
    text = read_raw(file_name)
    # read emojis and remove it
    text = text.lower()
    text_lines = text.split("\n")
    text_lines = list(filter(None, text_lines))  # Remove empty entries

    result = partitionize(text_lines[1:])
    del text_lines

    stripped_text = strip([data_line[0] for data_line in result])

    for i, data_line in enumerate(result):
        result[i][0] = stripped_text[i]

    import pprint as pp
    pp.pprint(result)


def main():
    check_debug = getattr(sys, 'gettrace', None)
    if check_debug():
        # In debug mode
        # file_name = input("Filename:")
        file_name = "../dataset/english_dev/2018-EI-reg-En-anger-dev.txt"
    else:
        file_name = sys.argv[1]

    preprocess(file_name)


if __name__ == "__main__":
    main()
