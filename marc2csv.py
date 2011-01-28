#!/usr/bin/env python
#-*- coding:utf-8 -*-

# TODO: 
# Solve unicode handling! \x?? and \u?? characters.
# What to do with records without a system number (field 001)? Log them!
## Use chardet? How to determine proper encoding? Characters like \xed are likely from a windows encoding.
## http://stackoverflow.com/questions/269060/is-there-a-python-library-function-which-attempts-to-guess-the-character-encoding

import codecs, cStringIO, csv, re, sys
from pymarc import MARCReader


def decode(s, encodings=('ascii', 'utf8', 'latin1')):
  ## http://stackoverflow.com/questions/269060/is-there-a-python-library-function-which-attempts-to-guess-the-character-encoding
  for encoding in encodings:
    try:
      return s.decode(encoding)
    except UnicodeDecodeError:
      pass
  return s.decode('ascii', 'ignore')


class UnicodeWriter:
  """
  A CSV writer which will write rows to CSV file "f",
  which is encoded in the given encoding.
  """

  def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
    # Redirect output to a queue
    self.queue = cStringIO.StringIO()
    self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
    self.stream = f
    self.encoder = codecs.getincrementalencoder(encoding)()

  def writerow(self, row):
    cleanRow = []
    for s in row:
      if isinstance(s, int):
        s = str(s)
      else:
        try:
          s.encode("UTF-8")
        except UnicodeDecodeError:
          s.decode("ISO-8859-1").encode("UTF-8")
      cleanRow.append(s)
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
    
    #self.cleanBackslashXChars(filepath)
    try:
      self.reader = MARCReader(
        open("{0}".format(filepath), "r"),
        to_unicode = True, # This seems to clean it a little bit.
        force_utf8 = True
      )
    except IOError:
      print >>sys.stderr, "Cannot open {0}".format(filepath)
      raise SystemExit
      
    self.log = open("{0}-records-wo-001.log".format(filepath), "w")
    self.outputFile = open("{0}.csv".format(filepath), "wb")
    self.writer = UnicodeWriter(
      self.outputFile,
      delimiter = ",",
      quoting = csv.QUOTE_MINIMAL
    )
  
  def cleanBackslashXChars(self, filepath):
    file = open(filepath, "r")
    doc = file.read()
    file.close()
    doc = re.sub("\xaf|\xbe|\xc5|\xa1|\x99", " ", doc)
    file = open("{0}-repaired".format(filepath), "wb")
    file.write(doc)
    file.close()
    
  def logRecord(self, record):
    output = "\n".join(
      ["{0}: {1}".format(str(field.tag), field.value()) for field in record.get_fields()]
    )
    self.log.write(output + "\n")
    
  def checkRecord(self, record):
    """Check if we have the primary identificator from the field 001."""
    if record["001"]:
      return True
    else:
      self.logRecord(record)
      return False
      # raise Exception("Field 001 missing.")
      # Where? How to identify the record since 001 is missing?
      # Output whole MARC record to see, if there are any other identifiers.
      # If there are no identifiers, provide hash of the whole record as an identifier. 
  
  def writeRow(self, row):
    """
      Printed CSV header:
      System number, field tag, number of field's occurrence, first indicator,
      secord indicator, subfield label, number of subfield's occurrence, value
    """
    self.writer.writerow(row)
      
  def processRecord(self, record):
    """Process individual MARC record"""
        
    if self.checkRecord(record):
      # Initialize dict for tracking which field tags and how many times were used
      usedTags = {}
        
      sysno = record["001"].value()
      for field in record.fields:
        # Initialize dict for tracking which field tags and how many times were used
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
              # Print it!
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
            else: # Even (zero-based) items are subfield label
              subfieldLabel = subfield
              # Increment used subfield labels
              if not usedSubfields.has_key(subfieldLabel):
                usedSubfields[subfieldLabel] = 1
              else:
                usedSubfields[subfieldLabel] += 1 
            
        except AttributeError:
          # The field has no subfields. Print it!
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
