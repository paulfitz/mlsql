This wraps up https://github.com/naver/sqlova/ for making predictions,
just to get a sense of when it works and when it fails.

Steps:

```
  make
  make start
  # Get a csv file, eg:
  #    https://vincentarelbundock.github.io/Rdatasets/csv/Ecdat/USstateAbbreviations.csv
  #    (let's rename this to abbrev.csv)
  ./add_csv.sh play abbrev.csv
  ./add_question.sh play abbrev "what state has ansi digits of 11"
  ./predict.sh play
```

Result should be in results_play.jsonl.

If model crashes without appearing to give output, check docker memory limit is high enough.
(Docker->Preferences->Advanced or equivalent).  Say at least 3GB?
