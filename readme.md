# webcorpus

![pypi badge](https://badge.fury.io/py/webcorpus.svg)

Generate large-scale NLP corpora from web crawls. This project has been used to generate [IndicCorp](https://indicnlp.ai4bharat.org/corpora/), a large-scale corpora for Indic languages.


### Installation

Make sure you have java installed on your system. Next, go to the project root directory and install it using pip:

```bash
sudo pip3 install .
```

### Usage

##### Running Crawls

* First, create a log directory where all the logs will be dumped. Next, start the scrapyd server from project directory and deploy the spiders:

  ```bash
  # current directory is webcorpus
  mkdir logs
  sudo scrapyd
  scrapyd-deploy
  ```

* Start a crawl

  ```bash
  # all paths must be absolute paths
  curl http://localhost/schedule.json -d project=webcorpus -d spider=recursive-spider -d html_path=<html_path> -d source_name=<source_name> -d home_url=<home_url> -d lang=<iso code> -d log_path=<path_to_webcorpus>/logs
  
  ```

* Monitor crawls: You can monitor the jobs at the dashboard available at `http://<ip address>`. If using GCP, make sure to enable HTTP traffic on your VM.


##### Processing corpus


  ```bash
  # all paths must be absolute paths
  python3 scripts/process.py --operation <operation code> --lang <lang code> --input <input path> --output <output path>
  ```

* Processing operations supported: `extract_arts`, `extract_sents`, `extract_genres`


### Features

* supports crawling and processing of 17 Indian languages
* designed to run in distributed fashion




### Similar Projects

* [news-please](https://github.com/fhamborg/news-please)
* [newspaper3k](https://github.com/codelucas/newspaper)
* [lazynlp](https://github.com/chiphuyen/lazynlp)



