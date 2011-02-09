MARC to CSV and CSV to MARC converters
======================================

`marc2csv.py` converts MARC to CSV. Usage: `$ ./marc2csv.py marc_file`. This creates a file named `marc_file.csv`. The outputted CSV has this header:

System number, field tag, number of field's occurrence, first indicator, secord indicator, subfield label, number of subfield's occurrence, value

`csv2marc.py` converts CSV to MARC. It takes the CSV with the same structure as is in the output of `marc2csv.py`. Usage: `$ ./csv2marc.py csv_file`. The script produces a file named `csv_file.mrc`.

Requirements
------------

* Python 2.x.x
* Python libraries: [chardet](http://chardet.feedparser.org/), [pymarc](https://github.com/edsu/pymarc). These can be installed via `easy_install`: `$ sudo easy_install chardet; sudo easy_install pymarc`
