#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
  Converts MARC 21 to CSV.
"""

import chardet, codecs, cStringIO, csv, sys
from pymarc import MARCReader


class UnicodeWriter:
  """
  A CSV writer which will write rows to CSV file "f",
  which is encoded in the given encoding.
  Taken (and extended) from: <http://docs.python.org/library/csv.html>
  """

  def __init__(self, file, dialect = csv.excel, encoding = "utf-8", **kwds):
    # Redirect output to a queue
    self.queue = cStringIO.StringIO()
    self.writer = csv.writer(self.queue, dialect = dialect, **kwds)
    self.stream = file
    self.encoder = codecs.getincrementalencoder(encoding)()
  
  def decode(self, string, encodings = ("ascii", "utf8", "latin1")):
    """
      Decode a string.
    """
    # Try to decode string with the most common encodings.
    for encoding in encodings:
      try:
        return string.decode(encoding)
      except UnicodeDecodeError:
        pass
    # If not decoded, try to guess the encoding.
    guess = chardet.detect(string)
    if guess["encoding"]:
      return string.decode(guess["encoding"])
    # If everything fails, just decode it as ASCII and ignore errors.
    return string.decode("ascii", "ignore")
  
  def encode(self, string):
    """
      Encode a string into UTF-8.
    """
    try:
      return string.encode("UTF-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
      # If encoding attempt fails, try to decode the string first.
      string = self.decode(string)
      return string.encode("UTF-8")
    
  def cleanrow(self, row):
    """
      Try to clean the encodings in a CSV row first.
    """
    cleanRow = []
    for s in row:
      if isinstance(s, int):
        s = str(s)
      s = self.encode(s)
      cleanRow.append(s)
    return cleanRow
    
  def writerow(self, row):
    cleanRow = self.cleanrow(row)
    self.writer.writerow(cleanRow)
    # Fetch UTF-8 output from the queue ...
    data = self.queue.getvalue()
    data = data.decode("utf-8")
    # ... and reencode it into the target encoding
    data = self.encoder.encode(data)
    # write to the target stream
    self.stream.write(data)
    # empty queue
    self.queue.truncate(0)

  def writerows(self, rows):
    for row in rows:
      self.writerow(row)
            
            
class MARC2CSV (object):
  """
    Converts MARC records to CSV. Outputs CSV lines to stdout.
  """
  
  def __init__(self,):
    """
      Load the MARC file.
    """
    
    if len(sys.argv) > 1:
      filepath = sys.argv[1]
    else:
      raise Exception(
        "You need to provide a file path to the MARC file as an argument."
      )
    
    try:
      self.reader = MARCReader(
        open("{0}".format(filepath), "r"),
        to_unicode = True, # This seems to clean it a little bit.
        force_utf8 = True
      )
    except IOError:
      print >> sys.stderr, "Cannot open {0}".format(filepath)
      raise SystemExit
    
    # A file to log records without field 001 (system number)  
    self.log = open("{0}-records-wo-001.log".format(filepath), "w")
    self.outputFile = open("{0}.csv".format(filepath), "wb")
    self.writer = UnicodeWriter(
      self.outputFile,
      delimiter = ",",
      quoting = csv.QUOTE_MINIMAL
    )
    
  def logRecord(self, record):
    """
      Log a simple text dump of a record.
    """
    recordDump = ["{0}: {1}".format(str(field.tag), field.value()) for field in record.get_fields()]
    output = "\n".join(recordDump)
    self.log.write(output + "\n")
    
  def checkRecord(self, record):
    """
      Check if we have the primary identificator from the field 001.
    """
    if record["001"]:
      return True
    else:
      self.logRecord(record)
      return False
  
  def writeRow(self, row):
    """
      Printed CSV header:
      System number, field tag, number of field's occurrence, first indicator,
      secord indicator, subfield label, number of subfield's occurrence, value
    """
    self.writer.writerow(row)
      
  def processRecord(self, record):
    """
      Process individual MARC record
    """
        
    if self.checkRecord(record):
      # Initialize dict for tracking
      # which field tags and how many times were used.
      usedTags = {}
        
      sysno = record["001"].value()
      for field in record.fields:
        if not field.value() == "": # Skip empty fields
          # Initialize dict for tracking
          # which field tags and how many times were used
          usedSubfields = {}
          
          tag = field.tag
          # Increment used field tags
          if not usedTags.has_key(tag):
            usedTags[tag] = 1
          else:
            usedTags[tag] += 1
          
          # Get field indicators
          try:      
            ind1, ind2 = field.indicators
          except AttributeError: # The field has no indicators
            ind1 = ind2 = ""
            
          try:
            # The fields has some subfields.
            for index, subfield in enumerate(field.subfields):
              if index % 2: # Odd (zero-based) items are subfield values
                value = subfield
                self.writeRow([
                  sysno,
                  tag,
                  usedTags[tag],
                  ind1,
                  ind2,
                  subfieldLabel,
                  usedSubfields[subfieldLabel],
                  value
                ])
              else: # Even (zero-based) items are subfield labels
                subfieldLabel = subfield
                # Increment used subfield labels
                if not usedSubfields.has_key(subfieldLabel):
                  usedSubfields[subfieldLabel] = 1
                else:
                  usedSubfields[subfieldLabel] += 1 
              
          except AttributeError:
            # The field has no subfields.
            self.writeRow([
              sysno,
              tag,
              usedTags[tag],
              ind1,
              ind2,
              "", # Empty subfield label
              "", # Empty subfield count
              field.value()
            ])
        
  def main(self):
    for record in self.reader:
      self.processRecord(record)
      
    self.log.close()
    self.outputFile.close()

  
def main():
  m2c = MARC2CSV()
  m2c.main()
  
if __name__ == "__main__":
  main()
