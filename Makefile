
build:
	sudo apt install python-numpy libicu-dev python3-icu
	sudo $(which pip3) install boilerpipe3
	git submodule update --init --recursive
	pipenv install --system
