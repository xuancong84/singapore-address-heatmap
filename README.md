Singapore Map/Address Library
=============================

This is an improved and augmented version from https://github.com/xkjyeah/singapore-postal-codes

It also contains a dump of all Singapore postal codes retrieved from Onemap.sg on 10 Jun 2020.
See *example.ipynb* for the demo/tutorial.

The repo has 4 main functional components:
1. The download script and address name processor. Run *download_postal_codes.py* to crawl Singapore address and store in *singpostcode.json.gz*. Run *process.sh* to process/normalize address names, it will output to *database.json.gz* and *database.csv.gz* .
2. The database searcher: **dbsearch.py** uses *database.json.gz* with everything in JSON format; **dfsearch.py** uses *database.csv.gz* with everything in Pandas DataFrame format.
<p float='left'>
  <img src="https://github.com/xuancong84/singapore-address-heatmap/raw/master/example/dfsearch.png" alt="" width="90%" />
</p>
3. The count-map highlighter: given [geo-coordinates, count] pairs with corresponding color hint, it can draw circles on the map, with areas proportional to the counts at that location.
<p float='left'>
  <img src="https://github.com/xuancong84/singapore-address-heatmap/raw/master/example/countmap.png" alt="" width="60%" />
</p>
4. The heat-map highlighter: given a table with columns [datetime,address,count] or [datetime,latitude,longitude,count], it shows a timestamped heatmap, with color intensity proportional to the counts at that location.
<p float='left'>
  <img src="https://github.com/xuancong84/singapore-address-heatmap/raw/master/example/demo.gif" alt="" width="60%" />
</p>

Note: Use of the data is governed by the [Open Data Licence](https://www.onemap.sg/legal/opendatalicence.html)

- This data dump contains information from Onemap.sg postal code search accessed on 10 Jun 2020, or later if the date is specified in the commit message.
- This data dump contains information from MyTransport.sg static data, accessed 1 Dec 2017.
- For postal codes, the 2017 database contains 141726 entries, and the 2020 database contains 141848 entries. Interestingly, the 2020 database is about 25% smaller because it keeps fewer floating point digits.
