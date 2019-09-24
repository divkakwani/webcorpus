## Data Processing



#### Principles

* The empirical distribution of the sentences should be as close to the true distribution as possible
* Each word (i.e. delimited by space) should be part of the vocabulary of the desired language
* For increasing efficiency, map similar lexemes into one token, when we are not interested in learning different vectors from these lexemes



#### Specific Rules

* Remove special standalone characters from the corpus
* Remove sentences that contain one or more words not in the desired language
* Treat punctuation marks as words. Insert spaces around them
* Replace every number by `#` token
* Remove "stop sentences"
