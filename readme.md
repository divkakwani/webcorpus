## Indic Corpora



Indic Corpora is a tool to crawl and process corpora for Indian languages.



#### Setup

Clone the repository and run the following command:
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

