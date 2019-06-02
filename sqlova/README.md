This wraps up https://github.com/naver/sqlova/ for making predictions,
just to get a sense of when it works and when it fails.

Steps:

```
  make
  # Get a csv file, e.g. bridges.csv
  curl -F "csv=@bridges.csv" -F "q=how long is throgs neck" localhost:5050
```

If model crashes without appearing to give output, check docker memory limit is high enough.
(Docker->Preferences->Advanced or equivalent).  3GB works!
