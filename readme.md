## webcorpus



A tool to generate large textual corpora by crawling the web.



#### Usage


* Pull the latest source lists from various aggregators:
  ```bash
  webcorpus getsources --lang <language code> --srcdir <path>
  ```

* Crawls articles from sources building a raw corpus:

  ```bash
  webcorpus fetch --lang <language code> --srcdir <path> [--part <int>] --jobdir-root <path>  --output <path> 
  ```

* Generate processed dataset from a corpus:

  ```bash
  webcorpus gen-rawsent --lang <language code> --corpus <path> --output <path>
  webcorpus gen-annotatedsent --lang <language code> --corpus <path> --output <path>
  webcorpus gen-classification --lang <language code> --corpus <path> --output <path> \
                              --minclasses <int> --maxsamples <int>
  ```

* Get statistics of a corpus:

  ```bash
  webcorpus stat --corpus <path>
  ```



#### Features

* supports crawling and processing of 17 Indian languages
* supports resuming crawls after failures



#### Crawled Datasets

Checkout [this page](https://divkakwani.github.io/indian-corpora/) to download the crawled datasets




