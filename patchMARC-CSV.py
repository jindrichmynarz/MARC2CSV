#!/usr/bin/env python
#-*- coding:utf-8 -*-

import codecs, csv, cStringIO, os, sys
from marc2csv import UnicodeWriter


class PatchMARCCSV (object):
  """
    Patches MARC in CSV
  """
  
  def __init__(self,):
    self.checkArguments()
    self.arguments = {
      "input" : sys.argv[1],
      "patch" : sys.argv[2],
      "output" : sys.argv[3],
    }
    self.fileSizes = {
      "input" : os.path.getsize(self.arguments["input"]),
      "patch" : os.path.getsize(self.arguments["patch"]),
    }
    self.files = {
      "input" : open(self.arguments["input"], "r"),
      "patch" : open(self.arguments["patch"], "r"),
      "output" : open(self.arguments["output"], "w"),
    }
    self.fileSizes = self.compareFileSizes()
    self.writer = UnicodeWriter(
      self.files["output"],
      delimiter = ",",
      quoting = csv.QUOTE_MINIMAL
    )

  def checkArguments(self):
    if len(sys.argv) == 4:
      return True
    else:
      raise Exception(
        """
        Missing arguments. Usage: ./patchMARC-CSV.py input.csv patch.csv output.csv
        """
      )
  
  def closeFiles(self):
    for file in self.files:
      self.files[file].close()
    
  def compareFileSizes(self):
    if self.fileSizes["input"] > self.fileSizes["patch"]:
      return {
        "bigger" : self.files["input"],
        "smaller" : self.files["patch"],
        "type" : "input",
        
      }
    else:
      return {
        "bigger" : self.files["patch"],
        "smaller" : self.files["input"],
        "type" : "patch",
      }
  
  def patchLine(self, line):
    lineId = line[:-1]
    # Check if there is a patch
    for smallLine in csv.reader(self.fileSizes["smaller"], delimiter = ","):
      smallLineId = smallLine[:-1]
      if lineId == smallLineId:
        if self.fileSizes["type"] == "patch":
          return line
        else:
          return smallLine
    # If no patch is found, return the original
    return line
        
        
  def main(self):
    for bigLine in csv.reader(self.fileSizes["bigger"], delimiter = ","):
      patchedLine = self.patchLine(bigLine)
      self.writer.writerow(patchedLine)
      # Rewind smaller file    
      self.fileSizes["smaller"].seek(0)  
    self.closeFiles()
  
  
def main():
  pmc = PatchMARCCSV()
  pmc.main()
   
if __name__ == "__main__":
  main()
