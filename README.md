# r2r-sentiment-analysis
## Description
The goal of this project is to analyze customer email replies to our automatic reply-to-refill email to inform a future SMS refill project and begin building a sentiment analysis AI tool to increase the number of replies that can be handled automatically --> reducing the cases created for CS.

## Results
Replies breakdown:
* 65% clean "refill"
* 25% "refill" was intended, but customer did not follow instructions, or email data was messy, so a Salseforce case was created (this is where our program will add value)
* 5% empty reply (seems to be at least partly due to confusion between clicking a button and sending text reply)
* 5% did not want refill, but replied as were confused by instructions, OR wanted a refill, but had a question or additional request

## How to run AI reply text analyzer in CLI
Since the corpus for the ai/analysis model has already been built (resources/corpus/positive.txt and negative.txt), you can just run the ai tool in the CLI. --> after downloading the libraries in requirements.txt (or just pip install "nltk"), cd into src and run "python (or python3) refill_ai.py":
*   asks for in input string from user in terminal
*   outputs an estimated probability that the user wants a refill, with no added details
* submit "quit" as the string to end the program

## Steps to build dataset
1.  unzip "s3_objects.zip" into a folder S3_objects with all the objects inside (or download s3 objects from AWS bucket (prod reply to refill))
2. run npm install
3. cd into "src" from root dir
4. run "node cleanData.js" to roughly filter emails to text replies (more accurate than prod, but still not perfect)
5. run label.py --> which should output positives.txt and negatives.txt in resources/corpus, files that are ready to be consumed by refill_ai.py and sentiment.py for ai analysis.