import os
import sys
import re

def main():
    # Read data from replies.csv
    replies_file = "../resources/repliesV2.csv"
    replies_labeled_file = "../resources/replies_labeled.csv"
    replies_positive_file= "../resources/corpus/positives.txt"
    replies_negative_file= "../resources/corpus/negatives.txt"

    replies = load_data(replies_file)
    with open(replies_labeled_file, "w") as f, open(replies_positive_file, "w") as f_p, open(replies_negative_file, "w") as f_n:
        f.write("reply;s3ObjectId;label\n")
        needs_manual_replies = []
        # Auto classify to get count before manual classify
        for reply in replies:
            label = auto_classify(reply['reply_text'])
            if label == 'p':
                reply["label"] = "positive"
                f_p.write(
                    f"{reply['reply_text']}\n")
            elif label == 'j':
                reply["label"] = "junk"
            else:
                reply["label"] = "negative"
                f_n.write(f"{reply['reply_text']}\n")
                # needs_manual_replies.append(reply)
                # continue
            f.write(
                f"{reply['reply_text']};{reply['s3ObjectId']};{reply['label']}\n")


        # Manually classify
        # print(
        # f"Classify the following {len(needs_manual_replies)} replies with a 'p' (positive), 'n' (negative), 'j' (junk) label:\n")
        # index = 1
        # total = len(needs_manual_replies)
        # for reply in needs_manual_replies:

        #     label = manual_classify(reply['reply_text'], index, total)
        #     if label == 'p':
        #         reply["label"] = "positive"
        #         f_p.write(
        #             f"{reply['reply_text']}\n")
        #     elif label == 'n':
        #         reply["label"] = "negative"
        #         f_n.write(
        #             f"{reply['reply_text']}\n")
        #     else:
        #         reply["label"] = "junk"
        #     f.write(f"{reply['reply_text']};{reply['s3ObjectId']};{reply['label']}\n")
        #     index += 1

        

def manual_classify(reply_text, index, total):
    label = input(f"{index} out of {total}\n'{reply_text}': ")
    while label not in ('p', 'n', 'j'):
        label = input(
            f"Please only use 'p', 'n', or 'j'\n'{reply_text}': ")
    return label


def auto_classify(reply_text):
    # add is negative if we see patterns to match
    if is_junk(reply_text):
        return 'j' 
    if is_positive(reply_text):
        return 'p'
    return "needs manual classification"
    

def is_junk(reply_text):
    junk_variations = {
        '',
        'no match with xpath selection',
        '[attachment]'
    }
    if reply_text.strip() in junk_variations:
        return True
    return False

def is_positive(reply_text):
    refill_regex = 'refill'
    fillers_positives = {
        "refill"
        "please",
        "thanks",
        "thank",
        "you",
        "yes",
        "yea",
        "yeah",
        "hello",
        "hi",
        "hey",
        "send",
        "i",
        "would",
        "like",
        "we"
    }

    fillers_negatives = {
        "no",
        "not",
        "don't"
    }

    # result = re.search(refill_regex, reply_text, re.IGNORECASE)
    # if result != None:
    reply_text = reply_text.replace("!", "")
    reply_text = reply_text.replace(".", "")
    reply_text = reply_text.replace(",", "")

    reply_words = reply_text.split()
    words_count = len(reply_words)
    fillers_positives_count = 1
    for word in reply_words:
        if word.lower() in fillers_negatives:
            return False
        if word.lower() in fillers_positives:
            fillers_positives_count += 1
    if words_count - fillers_positives_count < 3:
        return True

    refill_variations = {
        'refill',
        'reffil',
        'refil',
        'please refill',
        'please refill',
        'yes',
        'yes please',
        'send',
        'refill please'
    }
    if reply_text.lower() in refill_variations:
        return True
    return False


def load_data(file):
    replies = []
    with open(file) as f:
        for line in f.read().splitlines():
            reply_text = line.split(";")[0]
            s3ObjectId = line.split(";")[1]
            replies.append({"reply_text": reply_text,
                           "s3ObjectId": s3ObjectId})
    return replies


main()
