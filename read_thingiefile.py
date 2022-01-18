#This file imports the list of thingies from CSV file and passes as an array when called.
import csv
import os
import numpy as np



def getThingiesFromCSV(ThingiCSV):
    ##Read URLS from a list of URLS Text File to determine which docs to scrape.
    line_counter = 0

    with open(ThingiCSV, "r",newline='') as thingiverse_url_file:
        reader = csv.reader(thingiverse_url_file)
        thingiesToScrape = []
        i = 0
        for row in reader:
            if row[1] == 'N':
                thingiesToScrape.append(row[0].removeprefix('https://www.thingiverse.com/thing:'))
    
    return thingiesToScrape

def markAsDownloadedInCSV(thing_id,ThingiCSV):
    thingiverse_url = 'https://www.thingiverse.com/thing:'
    reader = csv.reader(open(ThingiCSV))
    lines = list(reader)
    i = 0
    locs = [i for i, x in enumerate(lines) if x == [thingiverse_url + str(thing_id),'N']]
    
    for loc in locs:
        lines[loc] = [thingiverse_url + str(thing_id),'Y']
    writer = csv.writer(open(ThingiCSV,'w',newline=''))
    writer.writerows(lines)


def checkForThingieChanges(ThingiCSV,InternalCSV):
    readerExt = csv.reader(open(ThingiCSV))
    readerInt = csv.reader(open(InternalCSV))
    IntLines = list(readerInt)
    ExtLines = list(readerExt)
    TempIntLines = []
    DiffLines = []

    for line in IntLines:
        TempIntLines.append(line[0])
    ExtLines = (str(ExtLines).removesuffix(','))
    
    print(ExtLines)
    print(IntLines)
    # DiffLines = list(set(map(tuple,TempIntLines)) - set(map(tuple,ExtLines)))
    # print(DiffLines)

def getFileLength(ThingiCSV):
    with open(ThingiCSV,"r",newline='') as thingiverse_url_file:
        reader = csv.reader(thingiverse_url_file)
        return len(list(reader))    
    
