MARC to CSV and CSV to MARC converters
======================================

The scripts for converting [MARC](http://loc.gov/marc/ "MAchine Readable Cataloging") to [CSV](http://tools.ietf.org/html/rfc4180 "Comma-Separated Values") and back are intended to make traditional library data amenable to processing by common tools (e.g., command-line tools).
  
`marc2csv.py` converts MARC to CSV. Usage: `$ ./marc2csv.py marc_file`. This creates a file named `marc_file.csv`. The outputted CSV has the following header:

* System number
* field tag
* number of field's occurrence
* first indicator
* secord indicator
* subfield label
* number of subfield's occurrence
* value

`csv2marc.py` converts CSV to MARC. It takes the CSV with the same structure as is in the output of `marc2csv.py`. Usage: `$ ./csv2marc.py csv_file`. The script produces a file named `csv_file.mrc`.

There is also a script to patch the CSVs generated from MARC - `patchMARCCSV.py`. It can be used to apply patches to a CSV file (e.g., clean values, strip characters). The patch has the same structure as the CSV file. Usage: `$ ./patchMARCCSV.py input.csv patch.csv output.csv`.

Requirements
------------

* Python 2.x.x
* Python libraries: [chardet](http://chardet.feedparser.org/), [pymarc](https://github.com/edsu/pymarc). These can be installed via `easy_install`: `$ sudo easy_install chardet; sudo easy_install pymarc`
