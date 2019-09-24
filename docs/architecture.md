## Architecture



The basic flow for preparing the dataset is:

* Compile a list of news sources
* Scrape the news sources and store the raw dataset
* Process the raw dataset

In the following sections, each of the step is discussed in detail.



#### News Sources Compilation

A news source has the following attributes:

* Name
* Language
* Sitemap URL
* Home Page URL

Newspapers URLs are scraped from `w3newspapers.com` by `crawlers/w3newspaper`.  After scraping, they are stored in the file `data/news_sources.json`. This file can be manually edited to, for example, set irregular sitemap URLs.



#### Scraping News Sources

For each newspaper, we create a `Spider`, which is seeded with a URL obtained from the `news_sources.json` file. The URL is the site-map URL, and if it doesn't work, we use the home-page URL of the newspaper.

The spider crawls all the web-pages of a newspaper site and extracts the contained article using `boilerpipe`. After extraction, each article is checked against the following set of rules, called the articleness test, to make sure that it is a proper news article, and not any other page on the website:

**articleness test**

- The length is greater than 100

All the verified articles are compiled and stored in the `data/raw` directory



#### Processing Dataset

The processing of dataset is done by `NewsCorpusProcessor` defined in `corpus.py`. It reads a raw corpus and extracts every article it contains. The articles are split into sentences and the sentences are, in turn, filtered and transformed. Finally, all the sentences are combined into a single file to obtain the final dataset. 

The final dataset is stored in one file inside the `data/processed` directory.





