# MUTT
Metrics Unit TesTing (MUTT) for machine translation and other similarity metrics.

###Dependencies:
  - python (2.7.6)
    - nltk (3.1)
    - pattern.en (2.6)

### Run
To just evaluate metrics (~30 mins):
```
$ python src/mutt.py
```

For a full run (~150 mins):
```
$ rm src/tmp/*
$ python src/mutt.py
```
