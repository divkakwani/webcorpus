## Indian Corpora



This repository contains newspaper datasets and scraping code for several Indian languages

For discussion, join us on [![Join the chat at https://gitter.im/indian-nlp/community](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/indian-nlp/community)



#### Setup

After cloning, run the following command to install all the dependencies:
```bash
make build
```



#### Usage

* Re-compile the list of news sources:

  ```
  python3 main.py fetch-sources
  ```

* Scrape news sources and build raw dataset:

  ```bash
  python3 main.py fetch-news --lang <langcode> [--srange a,b]
  ```

* Process a raw dataset:

  ```bash
  python3 main.py process-news --corpuspath <path> --lang <langcode>
  ```

* Print the meta-data of a raw/processed dataset:

  ```bash
  python3 main.py metadata --corpuspath <path>
  ```



#### Performance

* Crawls around 0.5 GB of raw data / day for 10 sources.
* To achieve better efficiency, run multiple instances of crawlers on different machines, each operating on a different set of sources.
* Need around 5GB of raw data for 100M tokens



#### Datasets

| Language | # News Articles | # Lines | # Tokens  | # Unique Tokens | Link |
| -------- | --------------- | ------- | --------- | --------------- | ---- |
| Kannada  | 450K |  | 77M |          |      |

