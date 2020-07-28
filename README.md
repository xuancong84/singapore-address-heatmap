Singapore Map/Address Library
=============================

This is an improved and augmented version from https://github.com/xkjyeah/singapore-postal-codes
It also contains a dump of all Singapore postal codes retrieved from Onemap.sg on 10 Jun 2020.

The repo has 4 main functional components:
1. The download script and the crawled address database. The original downloaded data is in *singpostcode.json.gz*, after processing/normalization, it is stored in *database.json.gz* and *database.csv.gz*
2. The database searcher: *dbsearch.py* uses *database.json.gz* with everything in JSON format; *dfsearch.py* uses *database.csv.gz* with everything in Pandas DataFrame format.
3. The count-map highlighter: given [geo-coordinates, count] pairs with corresponding color hint, it can draw circles on the map, with areas proportional to the counts at that location.
4. The heat-map highlighter: given a table with columns [datetime,address,count] or [datetime,latitude,longitude,count], it shows a timestamped heatmap, with color intensity proportional to the counts at that location.

Note: Use of the data is governed by the [Open Data Licence](https://www.onemap.sg/legal/opendatalicence.html)

- This data dump contains information from Onemap.sg postal code search accessed on 10 Jun 2020, or later if the date is specified in the commit message.
- This data dump contains information from MyTransport.sg static data, accessed 1 Dec 2017.
- For postal codes, the 2017 database contains 141726 entries, and the 2020 database contains 141848 entries. Interestingly, the 2020 database is about 25% smaller because it keeps fewer floating point digits.
