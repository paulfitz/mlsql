There's a lot of fun work going on to infer SQL queries from questions and tables.
Here I try to make recent models a bit more accessible and easy to use.

Requirements:
 * install `docker`
 * install `curl`
 * Make sure docker allows at least 3GB of RAM (see `Docker`>`Preferences`>`Advanced`
   or equivalent)

== sqlova ==

This wraps up a published pretrained model for Sqlova (https://github.com/naver/sqlova/).
The model is hobbled a bit by not having access to column types.

Fetch and start sqlova running as an api server on port 5050:

```
docker run --name sqlova -d -p "5050:5050" paulfitz/sqlova
```

Be patient, the image is about 4.2GB.  Once it is running, it'll take a few seconds
to load models and then you can start asking questions about CSV table.  For example:

```
curl -F "csv=@bridges.csv" -F "q=how long is throgs neck" localhost:5050
# should get: answer 1800, SELECT (length) FROM bridges WHERE bridge = ? ["throgs neck"]
```

This is using the sample `bridges.csv` included in this repo.

| bridge | designer | length |
|---|---|---|
| Brooklyn | J. A. Roebling | 1595 |
| Manhattan | G. Lindenthal | 1470 |
| Williamsburg | L. L. Buck | 1600 |
| Queensborough | Palmer & Hornbostel | 1182 |
| Triborough | O. H. Ammann | 1380,383 |
| Bronx Whitestone | O. H. Ammann | 2300 |
| Throgs Neck | O. H. Ammann | 1800 |
| George Washington | O. H. Ammann | 3500 |

Here are some questions and answers:

| question | answer | sql |
|---|---|---|
| how long is throgs neck | 1800 | SELECT (length) FROM bridges WHERE bridge = ? ['throgs neck'] |
| who designed the george washington | O. H. Ammann | |
| how many bridges are there | 8 | |
| how many bridges are designed by O. H. Ammann | 4 | |
| which bridge are longer than 2000 | Bronx Whitestone, George Washington | |
| how many bridges are longer than 2000 | 2 | |
| what is the shortest length | 1182 | |
