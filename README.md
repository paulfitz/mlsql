Infer SQL queries from plain-text questions and table headers.

Requirements:
 * install `docker`
 * install `curl`
 * Make sure docker allows at least 3GB of RAM (see `Docker`>`Preferences`>`Advanced`
   or equivalent)

## sqlova

This wraps up a published pretrained model for Sqlova (https://github.com/naver/sqlova/).

Fetch and start sqlova running as an api server on port 5050:

```
docker run --name sqlova -d -p 5050:5050 paulfitz/sqlova
```

Be patient, the image is about 4.2GB.  Once it is running, it'll take a few seconds
to load models and then you can start asking questions about CSV tables.  For example:

```
curl -F "csv=@bridges.csv" -F "q=how long is throgs neck" localhost:5050
# {"answer":[1800],"params":["throgs neck"],"sql":"SELECT (length) FROM bridges WHERE bridge = ?"}
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

Here are some examples of the answers and sql inferred for plain-text questions about
this table:

| question | answer | sql |
|---|---|---|
| how long is throgs neck | 1800 | `SELECT (length) FROM bridges WHERE bridge = ? ['throgs neck']` |
| who designed the george washington | O. H. Ammann | `SELECT (designer) FROM bridges WHERE bridge = ? ['george washington']` |
| how many bridges are there | 8 | `SELECT count(bridge) FROM bridges` |
| how many bridges are designed by O. H. Ammann | 4 | `SELECT count(bridge) FROM bridges WHERE designer = ? ['O. H. Ammann']` |
| which bridge are longer than 2000 | Bronx Whitestone, George Washington | `SELECT (bridge) FROM bridges WHERE length > ? ['2000']` |
| how many bridges are longer than 2000 | 2 | `SELECT count(bridge) FROM bridges WHERE length > ? ['2000']` |
| what is the shortest length | 1182 | `SELECT min(length) FROM bridges` |

With the `players.csv` sample from WikiSQL:

| Player | No. | Nationality | Position | Years in Toronto | School/Club Team |
|---|---|---|---|---|---|
| Antonio Lang | 21 | United States | Guard-Forward | 1999-2000 | Duke |
| Voshon Lenard | 2 | United States | Guard | 2002-03 | Minnesota |
| Martin Lewis | 32, 44 | United States | Guard-Forward | 1996-97 | Butler CC (KS) |
| Brad Lohaus | 33 | United States | Forward-Center | 1996 | Iowa |
| Art Long | 42 | United States | Forward-Center | 2002-03 | Cincinnati |
| John Long | 25 | United States | Guard | 1996-97 | Detroit |
| Kyle Lowry | 3 | United States | Guard | 2012-present | Villanova |

| question | answer | sql |
|---|---|---|
| What number did the person playing for Duke wear? | 21 | `SELECT (No.) FROM players WHERE School/Club Team = ? ['duke']` |
| Who is the player that wears number 42? | Art Long  | `SELECT (Player) FROM players WHERE No. = ? ['42']` |
| What year did Brad Lohaus play? | 1996 | `SELECT (Years in Toronto) FROM players WHERE Player = ? ['brad lohaus']` |
| What country is Voshon Lenard from? | United States | `SELECT (Nationality) FROM players WHERE Player = ? ['voshon lenard']` |

Some questions about [iris.csv](https://en.wikipedia.org/wiki/Iris_flower_data_set):

| question | answer | sql |
|---|---|---|
| what is the average petal width for virginica | 2.026 | `SELECT avg(Petal.Width) FROM iris WHERE Species = ? ['virginica']` |
| what is the longest sepal for versicolor | 7.0 | `SELECT max(Sepal.Length) FROM iris WHERE Species = ? ['versicolor']` |
| how many setosa rows are there | 50 | `SELECT count(col0) FROM iris WHERE Species = ? ['setosa']` |

There are plenty of types of questions this model cannot answer (and that aren't covered
in the dataset it is trained on, or in the sql it is permitted to generate).  I hope to
track research in the area and substitute in models as they become available:

 * [WikiSQL leaderboard](https://github.com/salesforce/WikiSQL#leaderboard)
 * [Spider leaderboard](https://yale-lily.github.io/spider)
 * Code/models coming soon hopefully: [IRNet](https://github.com/zhanzecheng/IRNet) ([hint](https://github.com/zhanzecheng/IRNet/issues/6#issuecomment-521876138)), [Spider Schema GNN](https://github.com/benbogin/spider-schema-gnn)
 * Is there any code for [X-SQL](https://www.microsoft.com/en-us/research/publication/x-sql-reinforce-context-into-schema-representation/)?
 * [SyntaxSQL](https://github.com/taoyds/syntaxSQL)
 * [NL2SQL Challenge](https://tianchi.aliyun.com/competition/entrance/231716/information)
 * A term paper including a Sqlova reimplementation with tweaks: [Search Like a Human: Neural Machine Translation for Database Search](https://web.stanford.edu/class/cs224n/reports/custom/15709203.pdf)