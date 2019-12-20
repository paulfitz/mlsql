This wraps up https://github.com/microsoft/IRNet for making predictions.
Don't judge IRNet based on this, I haven't got a BERT-based model for it,
haven't even set up a way to test multi-table queries, and have broken
things in various ways.  Watch this space though.

Steps:

```
  # Make sure sqlova container isn't running since this will use same port.
  # Make sure docker has access to >= 5GB of memory, and that you're not
  # short on disk space.

  make && make run

  curl -F "csv=@bridges.csv" -F "q=how long is throgs neck" localhost:5050

  # You'll have to be very patient!  It takes a long time to load the model.
  # The first time you run this it will be especially long, since various
  # downloads and unpackings need to happen.  It wasn't practical to stick
  # all that in the docker container, at least not just yet.
```
