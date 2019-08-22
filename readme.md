## Indian Corpora



This repository contains newspaper datasets and scraping code for several Indian languages

For discussion, join us on [![Join the chat at https://gitter.im/indian-nlp/community](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/indian-nlp/community)

#### Setup

Run the following command to install the dependencies:
```bash
make build
```

#### Usage

* To re-compile the list of news sources, run:

  ```
  python3 main.py fetch-sources
  ```

* To scrape news sources and build raw dataset, run:

  ```bash
  python3 main.py fetch-news
  ```

* To process a raw dataset, run:

  ```bash
  python3 main.py process-news --corpuspath <path> --lang <langcode>
  ```

  

#### Datasets

* Hindi
* Kannada
* Oriya
