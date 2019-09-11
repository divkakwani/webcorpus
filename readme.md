## Indian Corpora



This repository contains newspaper datasets and scraping code for several Indian languages

For discussion, join us on [![Join the chat at https://gitter.im/indian-nlp/community](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/indian-nlp/community)



#### Setup

Make sure to pull all the submodules while cloning. After that, run the following command to install the dependencies:
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
  python3 main.py fetch-news
  ```

* Process a raw dataset:

  ```bash
  python3 main.py process-news --corpuspath <path> --lang <langcode>
  ```

* Print the meta-data of a raw/processed dataset:

  ```bash
  python3 main.py metadata --corpuspath <path>
  ```

* Sync a dataset

  ```bash
  python3 main.py sync --corpuspath <path> [--override]
  ```



#### Datasets

| Language | # News Articles | # Lines | # Tokens  | # Unique Tokens | Link |
| -------- | --------------- | ------- | --------- | --------------- | ---- |
| Kannada  | 93K          | 1.1M | 13.5M | 0.8M         |      |

