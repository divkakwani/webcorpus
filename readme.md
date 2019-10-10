## Corpora

Corpora is a language-agnostic corpus crawler and processor specifically designed for Indian languages.


#### Setup

Clone the repository and run the following command:
```bash
pip3 install .
```



#### Usage

* Re-compile the list of news sources:

  ```
  corpora fetch-sources
  ```

* Scrape news sources and build raw dataset:

  ```bash
  corpora fetch-news --lang <langcode> [--srange a,b]
  ```

* Process a raw dataset:

  ```bash
  corpora process-news --corpuspath <path> --lang <langcode>
  ```



#### Performance

* Crawls around 0.5 GB of raw data / day for 10 sources.
* To achieve better efficiency, run multiple instances of crawlers on different machines, each operating on a different set of sources.
* Need around 5GB of raw data for 100M tokens



#### Datasets

| Language | # News Articles | # Lines | # Tokens  | # Unique Tokens | Link |
| -------- | --------------- | ------- | --------- | --------------- | ---- |
| Assamese |  |  |  |          |      |
| Bengali |  |  |  |          |      |
| Gujarati | | 6.6M | 112M | 1.8M | |
| Hindi | | |  | | |
| Kannada | 713K | 12M | 137M | 2.6M | |
| Malayalam | | 9.5M | 103M | 5.1M | |
| Marathi | | 9.2M | 130M | 2.2M | |
| Oriya | | |  | | |
| Punjabi | | |  | | |
| Tamil | | 12M | 143M | 3.5M | |
| Telugu |  | 14M | 190M | 4.2M | |
