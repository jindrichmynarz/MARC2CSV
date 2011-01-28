#!/usr/bin/env python
#-*- coding:utf-8 -*-

import csv, os, sys
from pymarc import Field, MARCWriter, Record


class CSV2MARC (object):
  """
    Converts CSV to MARC records.
  """
  
  def __init__(self):
    """
      Load the CSV file.
    """
    if len(sys.argv) > 1:
      filepath = sys.argv[1]
    else:
      raise Exception(
        "You need to provide a file path to the CSV file as an argument."
      )
    try:
      self.reader = csv.reader(
        open(filepath, "r"),
        delimiter=","
      )
    except IOError:
      print >>sys.stderr, "Cannot open {0}".format(filepath)
      raise SystemExit
    
    output = "{0}.mrc".format(os.path.splitext(filepath)[0])
    self.file = open(output, "w")
    
    # State variables
    self.sysno = False
    self.record = False
    self.field = False
    self.fieldTag = False
    self.fieldTagOccurrence = False
    self.subfieldLabel = False
    self.subfieldLabelOccurrence = False
    self.line = False
      
  def checkFieldChange(self, fieldTag, fieldTagOccurrence):
    if (self.fieldTag != fieldTag) or ((self.fieldTag == fieldTag) and (self.fieldTagOccurrence != fieldTagOccurrence)):
      return True
    else:
      return False
     
  def writeMARCRecord(self, record):
    writer = MARCWriter(self.file)
    writer.write(record)
  
  def hasRecordChanged(self, sysno):
    if not (sysno == self.sysno):
      return True
    else:
      return False
  
  def getNewRecord(self, sysno):
    self.sysno = sysno
    self.record = Record()
  
  def getNewField(self, line):
    self.fieldTag = line["fieldTag"]
    self.fieldTagOccurrence = line["fieldTagOccurrence"]
    if line["subfieldLabel"]:
      # Normal field
      self.field = Field(
        tag = line["fieldTag"],
        indicators = [
          line["indicator1"],
          line["indicator2"]
        ]
      )
    else:
      # Datafield    
      self.field = Field(
        tag = line["fieldTag"],
        data = line["value"]
      )
  
  def checkMissing246(self, line):
    if line["sysno"] == "000649385" and line["value"] == "Řada bezpečnostního inženýrství":
      return True
    else:
      return False
        
  def main(self):
    for line in self.reader:
      # Parse the line
      line = {
        "sysno" : line[0],
        "fieldTag" : line[1],
        "fieldTagOccurrence" : line[2],
        "indicator1" : line[3],
        "indicator2" : line[4],
        "subfieldLabel" : line[5],
        "subfieldLabelOccurrence" : line[6],
        "value" : line[7],
      }
      #print line
      #print "self.sysno: " + str(self.sysno)
      #print "self.fieldTag: " + str(self.fieldTag)
      #print "self.fieldTagOccurrence: " + str(self.fieldTagOccurrence)
      #print "self.subfieldLabel: " + str(self.subfieldLabel)
      #print "self.subfieldLabelOccurrence: " + str(self.subfieldLabelOccurrence)
      
      #if self.checkMissing246(line): # Added for testing the missing field
      #  self.line = line
      #  break
        
      if not self.sysno:
        #print "[INFO] New record"
        self.getNewRecord(line["sysno"])
      if self.hasRecordChanged(line["sysno"]):
        #print "[INFO] New record 2"
        self.record.add_field(self.field) # Add the last field of the previous record
        self.field = False # Remove the last field of the previous record
        self.fieldTag = False
        self.writeMARCRecord(self.record)
        self.getNewRecord(line["sysno"])
      
      if not self.fieldTag:
        #print "[INFO] New field"
        self.getNewField(line)
      if self.checkFieldChange(line["fieldTag"], line["fieldTagOccurrence"]):
        #print "[INFO] New field"
        self.record.add_field(self.field)
        self.getNewField(line)
      
      if line["subfieldLabel"]: # If we have a subfield
        self.field.add_subfield(
          line["subfieldLabel"],
          line["value"]
        )
    self.record.add_field(self.field) # Write the last field
    self.writeMARCRecord(self.record) # Write the last record after the iteration has ended
    self.file.close()
    

def main():
  c2m = CSV2MARC()
  c2m.main()
  
if __name__ == "__main__":
  main()
