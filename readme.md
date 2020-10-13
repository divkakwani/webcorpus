# webcorpus

![pypi badge](https://badge.fury.io/py/webcorpus.svg)

A tool to generate large textual corpora by crawling the web.

### Installation

```bash
git clone https://github.com/divkakwani/webcorpus
cd webcorpus
sudo pip3 install .
```

### Usage

###### Running Crawls

* Start scrapyd server from project directory and deploy the spiders:

  ```bash
  # current directory is webcorpus
  sudo scrapyd
  scrapy-deploy
  ```

* Start a crawl

  ```bash
  # all paths must be absolute paths
  curl http://localhost/schedule.json -d project=webcorpus -d spider=recursive-spider -d html_path=<html_path> -d source_name=<source_name> -d home_url=<home_url> -d lang=<iso code> -d log_path=<path_to_webcorpus>/logs
  
  ```

###### Processing corpus






### Features

* supports crawling and processing of 17 Indian languages
* designed to run in distributed fashion



### Crawled Datasets

Checkout the [docs](https://github.com/divkakwani/webcorpus/tree/master/docs) directory to download the crawled datasets and other resources derived from the datasets.



### Similar Projects

* [news-please](https://github.com/fhamborg/news-please)
* [newspaper3k](https://github.com/codelucas/newspaper)
* [lazynlp](https://github.com/chiphuyen/lazynlp)



