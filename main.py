#
# Library Imports
#
import time
import datetime
import sqlite3
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QCheckBox, QMainWindow, QGridLayout, QLabel, QStackedLayout, QStackedWidget, QWidget, QMenu
from PyQt5.QtWidgets import QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import QSize, QTimer
import sys


# Script Imports
from read_thingiefile import getFileLength, getThingiesFromCSV
from read_thingiefile import markAsDownloadedInCSV
from thingiverse_scraper import get_download_file_paths, get_sqlite_database_path, get_database_connection, get_database_cursor, check_if_valid_thingiverse_page_and_retrieve_html_and_page_title,thingiverse_table_name,insert_record_into_thingiverse_table, http_success_status_codes, page_title_max_size, download_thingiverse_zip_file, remote_zip_buffer_size, delay_between_downloads_seconds,close_database_connection,close_database_cursor,configureDescription





files_directory, html_directory = get_download_file_paths()

sqlite_database_path = get_sqlite_database_path()
database_connection = get_database_connection(sqlite_database_path)
database_cursor = get_database_cursor(database_connection)

thingiverse_url = 'https://www.thingiverse.com/thing:'


#Create GUI###################################################################
class GUIWindow(QWidget):
    def __init__(self):
        #Scraping Variables
        self.ThingiCSV = 'C:/Users/SR/Documents/GitHub/ThingiverseScraper/clone_list.csv'
        self.namesList = []
        self.linkList = []
        self.thingIdList = []
        self.ThingiesToScrape = []
        
        QWidget.__init__(self)
        # self.LoadCSVWidget = QWidget()
        # self.SelectDownloadWidget = QWidget()

        # self.stackedLayout = QStackedLayout()
        self.layout = QGridLayout()

        self.setMinimumSize(QSize(1000, 320))    
        self.setWindowTitle("Thingiverse Cloning App") 

        self.CSVLocation = QLineEdit()
        self.CSVLocation.setText(self.ThingiCSV)
        self.bt1 = QPushButton("Load CSV",self)
        self.cloneFiles = QPushButton("Clone",self)
        self.selectAll = QCheckBox("Select All files for download")
        self.selectAll.setChecked(False)
        self.layout.addWidget(self.CSVLocation,0,1,1,1)
        self.layout.addWidget(self.bt1,1,1,1,1)
        

        self.bt1.clicked.connect(self.LoadCSV)
        self.cloneFiles.clicked.connect(self.DownloadFiles)
        self.selectAll.stateChanged.connect(self.SelectAllFiles)

        #Hide all buttons
        self.selectAll.hide()
        self.cloneFiles.hide()

        self.count = 10
        self.time = QTimer(self)
        self.time.setInterval(1000)
        self.setLayout(self.layout)
        # self.time.timeout.connect(self.Refresh)
        

    def SelectAllFiles(self):
        if(self.selectAll.isChecked() == True):
            for i,v in enumerate(self.namesList):
                self.namesList[i].setEnabled(True)
                self.namesList[i].hide()
          

        
    def LoadCSV(self):
        self.ThingiesFromCSVToScrape = getThingiesFromCSV(self.CSVLocation.text())
        self.CSVLength = getFileLength(self.CSVLocation.text())
        # if self.bt1.isEnabled():
        #     self.time.start()
        #     self.bt1.setEnabled(False)

        if not self.ThingiesFromCSVToScrape:
            self.bt1.setStyleSheet('QPushButton {background-color: red;}')
        else:
            self.bt1.setStyleSheet('QPushButton {background-color: green;}')

            #Select All Button
            self.layout.addWidget(self.selectAll,0,0)
            self.layout.addWidget(QLabel("Thingie Links"),0,1)    
            self.layout.addWidget(QLabel("Clone State"),0,2)

            #List all the Thingies to scrape
            for i, thing_id in enumerate(self.ThingiesFromCSVToScrape):
                thing_html, thing_page_title = check_if_valid_thingiverse_page_and_retrieve_html_and_page_title(thing_id, thingiverse_url, http_success_status_codes)
                if not thing_html and not thing_page_title:
                    continue
                else:
                    self.namesList.append(thing_page_title)
                    self.linkList.append(thingiverse_url + thing_id)
                    self.thingIdList.append(thing_id)

            for i, v in enumerate(self.namesList):
                self.namesList[i] = QCheckBox(v)
                self.namesList[i].setChecked(True)
                htmlTag = '<a href="' + self.linkList[i] + '">' + self.linkList[i] + '</a>'
                self.linkList[i] = QLabel(htmlTag)
                
                self.layout.addWidget(self.namesList[i],i+1,0)
                self.layout.addWidget(self.linkList[i],i+1,1)
            self.layout.addWidget(self.cloneFiles,self.CSVLength,0,1,3)

            self.bt1.hide()
            self.CSVLocation.hide()
            self.cloneFiles.show()
            self.selectAll.show()
            # self.show()

    def DownloadFiles(self):
        for i, v in enumerate(self.namesList):
            if(self.namesList[i].isChecked() == True):
                thing_id = self.thingIdList[i]

                thing_timestamp = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')


                thing_html, thing_page_title = check_if_valid_thingiverse_page_and_retrieve_html_and_page_title(thing_id, thingiverse_url, http_success_status_codes)

                if not thing_html and not thing_page_title:
                    # Write empty page details to database and continue
                    insert_record_into_thingiverse_table(database_connection, database_cursor, thingiverse_table_name, None, thing_id, 'Blank Page', thing_timestamp)
                    continue
                if len(thing_page_title) > page_title_max_size:
                    thing_page_title = thing_page_title[:page_title_max_size]

                # If thing URL is valid, write page HTML to ../html/ directory
                with open(html_directory + f'{thing_id}-{thing_page_title}.txt', 'w') as f_html_file:
                    f_html_file.write(thing_html)

                # Download Thing zip file
                thing_description = download_thingiverse_zip_file(files_directory, thing_id, thing_page_title, thingiverse_url, http_success_status_codes, remote_zip_buffer_size)
                insert_record_into_thingiverse_table(database_connection, database_cursor, thingiverse_table_name, None, thing_id, thing_page_title, thing_timestamp)
                self.layout.addWidget(QLabel("Downloaded"),i+1,2)
                configureDescription(thing_description,thing_page_title,thingiverse_url,thing_id)
                markAsDownloadedInCSV(thing_id,self.CSVLocation.text())
                time.sleep(delay_between_downloads_seconds)
            else:
                self.layout.addWidget(QLabel("Not Downloaded"),i+1,2)


        close_database_cursor(database_cursor)
        close_database_connection(database_connection)
        


    
        self.cloneFiles.setStyleSheet('QPushButton {background-color: green;}')
        self.cloneFiles.setEnabled(False)

def ScrapingScript(self):
    for i,thing_id in enumerate(self.ThingiesToScrape):
        thing_timestamp = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')


        thing_html, thing_page_title = check_if_valid_thingiverse_page_and_retrieve_html_and_page_title(thing_id, thingiverse_url, http_success_status_codes)

        if not thing_html and not thing_page_title:
            # Write empty page details to database and continue
            insert_record_into_thingiverse_table(database_connection, database_cursor, thingiverse_table_name, None, thing_id, 'Blank Page', thing_timestamp)
            continue
        if len(thing_page_title) > page_title_max_size:
            thing_page_title = thing_page_title[:page_title_max_size]

        # If thing URL is valid, write page HTML to ../html/ directory
        with open(html_directory + f'{thing_id}-{thing_page_title}.txt', 'w') as f_html_file:
            f_html_file.write(thing_html)
            

        # Download Thing zip file
        download_thingiverse_zip_file(files_directory, thing_id, thing_page_title, thingiverse_url, http_success_status_codes, remote_zip_buffer_size)
        insert_record_into_thingiverse_table(database_connection, database_cursor, thingiverse_table_name, None, thing_id, thing_page_title, thing_timestamp)
        self.layout.addWidget(QLabel("Downloaded"),i+1,2)
        time.sleep(delay_between_downloads_seconds)


    close_database_cursor(database_cursor)
    close_database_connection(database_connection)
    



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    HomeScreen = GUIWindow()
    HomeScreen.show()
    sys.exit(app.exec_())