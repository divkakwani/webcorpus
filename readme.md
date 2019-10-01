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
  python3 main.py fetch-news --lang <langcode>
  ```

* Process a raw dataset:

  ```bash
  python3 main.py process-news --corpuspath <path> --lang <langcode>
  ```

* Print the meta-data of a raw/processed dataset:

  ```bash
  python3 main.py metadata --corpuspath <path>
  ```


#### Datasets

| Language | # News Articles | # Lines | # Tokens  | # Unique Tokens | Link |
| -------- | --------------- | ------- | --------- | --------------- | ---- |
| Kannada  | 93K          | 1.1M | 13.5M | 0.8M         |      |

