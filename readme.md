<img src="docs/logo.svg"/>

![pypi badge](https://badge.fury.io/py/webcorpus.svg)  ![GPL License](https://img.shields.io/pypi/l/webcorpus) 

webcorpus is an end-to-end tool used to crawl and generate datasets from the crawled data. It can be used to generate monolingual corpora and has various processors to create labelled datasets automatically. webcorpus is particulary suited for low-resource languages which need automated methods for creating large-scale datasets.

This project has been used to generate [IndicCorp](https://indicnlp.ai4bharat.org/corpora/), a large-scale corpora for Indic languages, and some datasets for [IndicGLUE](https://indicnlp.ai4bharat.org/indic-glue/).


### Installation

Make sure you have java installed on your system. Next, install it using pip:

```bash
sudo pip3 install webcorpus
```

### Usage

To build the dataset, we first need to crawl the web and then process the crawls to create the final dataset.

##### Step 1: Crawling Sources

To start crawling websites, you first need to start the webcorpus crawling server:

````bash
sudo webcorpus start
````

Once the server has started, you can start crawls using the following command.

```bash
webcorpus crawl --path <path> --name <name> --url <url> --log <path> [--host <ip address>]
```

You can see the status of the crawls anytime by executing:

```bash
webcorpus log [--host <ip address>]
```

The last two steps can also been remotely, which can be useful in distributed mode where you are running multiple webcorpus servers.

##### Step 2: Processing Corpus


  ```bash
webcorpus process --operation <operation code> --lang <lang code> --input <input path> --output <output path>
  ```

Currently, the following processing operations are supported: `extract_arts`, `extract_sents`, `extract_genres`, `archive`.

