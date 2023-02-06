## Description
A program that builds a modified naive bayes classifier to calculate the probability that a given user "reply" is intended to confirm "refill".

## How to run AI reply text analyzer in CLI
Since the corpus for the ai/analysis model has already been built (resources/corpus/positive.txt and negative.txt), you can just run the ai tool in the CLI. --> after downloading the libraries in requirements.txt (or just pip install "nltk"), cd into src and run "python (or python3) refill_ai.py":
*   asks for in input string from user in terminal
*   outputs an estimated probability that the user wants a refill, with no added details
* submit "quit" as the string to end the program