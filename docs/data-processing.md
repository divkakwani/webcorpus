## Data Processing



#### Principles

* The empirical distribution of the sentences should be as close to the true distribution as possible
* Each word (i.e. delimited by space) should be part of the vocabulary of the desired language. The vocabulary is defined as $V = \textrm{words} \cup \textrm{punc-marks} \cup \{\#\}$.
* For increasing efficiency, map similar lexemes into one token, when we are not interested in learning different vectors for these lexemes.l



#### Specific Rules

* Remove sentences that contain one or more words not in the desired language
* Remove short sentences because they are probably not proper sentences
* Treat punctuation marks as words. Insert spaces around them
* Lowercase all the letters (in case of English)
* Replace every number (both in the Latin and the native scripts) by `#` token
* Remove "stop sentences"





#### References

* 

