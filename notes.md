## Architecture



1. Obtaining newspapers URLs
2. Downloading articles and building the raw dataset
3. Processing each article
4. Loading and processing the entire raw dataset



#### Obtaining Newspaper URLs

Newspapers URLs are gathered by scraping `w3newspapers.com`, which are then persisted in `news_sources.json`. The file `gather_urls.py` contains the required scraping & persisting code. 



#### Downloading Articles and Building the Raw Dataset

For each newspaper, we create a `Spider`, which is seeded with a URL obtained from the `news_sources.json` file. The URL is the site-map URL, and if it doesn't work, we use the home-page URL of the newspaper.

The spider crawls all the web-pages of a newspaper site and extracts the contained article using `boilerpipe`. After extraction, each article is checked against the following set of rules, called the articleness test, to make sure that it is a proper news article, and not any other page on the website:

**articleness test**

* The length is greater than 200
* contains a minimum of 3 sentences in the language associated with the newspaper
* There are a minimum of 3 sentences with length greater than 6 words.

All the verified articles are compiled and stored in the `data/raw` directory



#### Loading and Processing the Entire Raw Dataset

We use the following objects here:

* dataset objects - for loading and storing the raw and the processed dataset respectively
* sentence tokenizer: splits an article into sentences
* sentence processor: processes a sentence

The workflow is like this. We load articles from the raw dataset, and tokenize each sentence using the sentence tokenizer. Then, we process each sentence, and put them all together to form the processed article. All the processed articles are later persisted into the directory `data/processed`



**Sentence Processor**

* Normalize each sentence
* Remove useless symbols (punctuation marks, newline chars etc)

Remove "stop sentences"



#### Glossary

* Tokenization:  splitting text into meaningful units
* Normalization: the process of transforming text into a single canonical form that it might not have had before



#### Suggested Modifications

* Check if a page is article or not using URL logic
* Remove "stop sentences"
* Use the newspaper library with a custom content extractor
* Override get_category_urls in newspaper library
* Separate category pages and post pages