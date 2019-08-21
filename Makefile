
build:
	sudo apt install python-numpy libicu-dev python3-icu
	pipenv install
	python3 -m spacy download en
