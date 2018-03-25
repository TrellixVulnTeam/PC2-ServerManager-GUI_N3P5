#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Project Cars 2 / Dedicated Server Manager - GUI.

by David Maus/neslane at www.gef-gaming.de

Randomized weather slots server config for Project Cars 2 dedicated server .
Info at www.gef-gaming.de.

WARNING MESSY CODE! :)
"""
import os
import sys; sys.dont_write_bytecode = True
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
from PyQt5 import uic, QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog
from PyQt5.QtGui import QPalette, QColor, QFont
import glob
import webbrowser
from ui import resources
from configparser import ConfigParser
import pysteamcmd
import pathlib
import shutil
import tempfile
import urllib.request
import zipfile
import progressbar
import tarfile
import base64
import stat
import subprocess
import re
import time


pbar = None


def show_progress(block_num, block_size, total_size):
    global pbar
    if total_size == 0:
        total_size = 50
    if pbar is None:
        pbar = progressbar.ProgressBar(maxval=total_size)

    downloaded = block_num * block_size
    if downloaded < total_size:
        pbar.update(downloaded)
    else:
        pbar.finish()
        pbar = None


def encode(key, clear):
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc).encode()).decode()

def decode(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc).decode()
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)



def installServer(serverName):
    steamcmd_path = os.path.join(installPath, '_steamcmd_')
    gameserver_path = os.path.join(installPath, serverName)

    pathlib.Path(installPath).mkdir(parents=False, exist_ok=True)
    pathlib.Path(steamcmd_path).mkdir(parents=False, exist_ok=True)
    pathlib.Path(gameserver_path).mkdir(parents=False, exist_ok=True)

    steamcmd = pysteamcmd.Steamcmd(steamcmd_path)
    steamcmd.install()
    steamcmd.install_gamefiles(gameid=413770, game_install_dir=gameserver_path, user=steam_user, password=steam_pw, validate=True)


    serverWrapperURL = 'https://github.com/david-maus/PC2-ServerManager-CMDtool/archive/master.zip'
    zip_name = 'DedicatedServerWrapperCMDtool.zip'
    serverWrapperDLname = os.path.join(installPath, zip_name)

    print('\n\n\nDownloading DedicatedServerWrapper Tool:\n')

    urllib.request.urlretrieve(serverWrapperURL, serverWrapperDLname, show_progress)

    ROOT_PATH = 'PC2-ServerManager-CMDtool-master/'
    temp_dir = tempfile.mkdtemp()
    extraction_dir = os.path.join(gameserver_path, os.path.splitext(zip_name)[0])

    print('\n\n\nUnzipping DedicatedServerWrapper Tool: \n')

    with zipfile.ZipFile(serverWrapperDLname, 'r') as zip_file:

        members = zip_file.namelist()
        members_to_extract = [m for m in members if m.startswith(ROOT_PATH)]

        fileCount = len(members)
        count = 0

        bar = progressbar.ProgressBar(max_value=fileCount, redirect_stdout=True)
        for item in members:
            count += 1
            print('Unzip file: ' + item.replace(ROOT_PATH, ''))
            bar.update(count)

        zip_file.extractall(temp_dir, members_to_extract)
        shutil.move(os.path.join(temp_dir, ROOT_PATH), extraction_dir)
    os.remove(serverWrapperDLname)

    print('\n\n\nServer install finished! \n')


def updateServer():
    steamcmd_path = os.path.join(installPath, '_steamcmd_')
    gameserver_path = os.path.join(installPath, selectedServer)
    if(selectedServer == ''):
        pass
    else:
        pathlib.Path(steamcmd_path).mkdir(parents=False, exist_ok=True)
        pathlib.Path(gameserver_path).mkdir(parents=False, exist_ok=True)

        steamcmd = pysteamcmd.Steamcmd(steamcmd_path)
        steamcmd.install()
        steamcmd.install_gamefiles(gameid=413770, game_install_dir=gameserver_path, user=steam_user, password=steam_pw, validate=True)

        serverWrapperURL = 'https://github.com/david-maus/PC2-ServerManager-CMDtool/archive/master.zip'
        zip_name = 'DedicatedServerWrapperCMDtool.zip'
        serverWrapperDLname = os.path.join(installPath, zip_name)

        print('\n\n\nDownloading DedicatedServerWrapper Tool:\n')

        urllib.request.urlretrieve(serverWrapperURL, serverWrapperDLname, show_progress)

        ROOT_PATH = 'PC2-ServerManager-CMDtool-master/'
        temp_dir = tempfile.mkdtemp()
        extraction_dir = os.path.join(gameserver_path, os.path.splitext(zip_name)[0])

        print('\n\n\nUnzipping DedicatedServerWrapper Tool: \n')

        with zipfile.ZipFile(serverWrapperDLname, 'r') as zip_file:

            members = zip_file.namelist()
            members_to_extract = [m for m in members if m.startswith(ROOT_PATH)]

            fileCount = len(members)
            count = 0

            bar = progressbar.ProgressBar(max_value=fileCount, redirect_stdout=True)
            for item in members:
                count += 1
                print('Unzip file: ' + item.replace(ROOT_PATH, ''))
                bar.update(count)

            zip_file.extractall(temp_dir, members_to_extract)
            shutil.move(os.path.join(temp_dir, ROOT_PATH), extraction_dir)
        os.remove(serverWrapperDLname)

        print('\n\n\nServer install finished! \n')

def on_rm_error( func, path, exc_info):
    # path contains the path of the file that couldn't be removed
    # let's just assume that it's read-only and unlink it.
    os.chmod( path, stat.S_IWRITE )
    os.unlink( path )

def removeSelectedServer(selectedServer):
    gameserver_path = os.path.join(installPath, selectedServer)
    if(selectedServer == ''):
        pass
    else:
        if os.path.isdir(gameserver_path):
            shutil.rmtree( gameserver_path, onerror =on_rm_error)
        else:
            pass


def readSettings():
    global installPath
    global steam_user
    global steam_pw
    if os.path.isfile(settingsPath):

        config = ConfigParser()
        config.read(settingsPath, encoding='utf8')

        installPath = config['SETTINGS']['installPath']
        steam_user = config['SETTINGS']['steam_user']
        steam_pw = config['SETTINGS']['steam_pw']

        steam_pw = decode('1231231', steam_pw)
    else:
        installPath = ''
        steam_user = ''
        steam_pw = ''
        open(settingsPath, "w+").close()
        config = ConfigParser()
        config.read(settingsPath, encoding='utf8')
        config.add_section('SETTINGS')
        config.set('SETTINGS','installPath', installPath)
        config.set('SETTINGS','steam_user', steam_user)
        config.set('SETTINGS','steam_pw', steam_pw)
        with open(settingsPath, 'w', encoding='utf8') as configfile:
            config.write(configfile)


def writeSettings(installPathNEW, steam_userNEW, steam_pwNEW):

    config = ConfigParser()
    config.read(settingsPath, encoding='utf8')

    config['SETTINGS']['installPath'] = installPathNEW
    config['SETTINGS']['steam_user'] = steam_userNEW
    config['SETTINGS']['steam_pw'] = encode('1231231', steam_pwNEW)


    with open(settingsPath, 'w', encoding='utf8') as configfile:
        config.write(configfile)

    global installPath
    global steam_user
    global steam_pw

    installPath = installPathNEW
    steam_user = steam_userNEW
    steam_pw = steam_pwNEW



def resource_path(relative_path):
    """Get Absolute Path."""
    base_path = getattr(sys, '_MEIPASS',
                        os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def Start():
    """Start Main Window UI."""
    global m
    m = Ui()
    m.show()
    return m


WHITE = QColor(255, 255, 255)
BLACK = QColor(0, 0, 0)
RED = QColor(255, 0, 0)
PRIMARY = QColor(53, 53, 53)
SECONDARY = QColor(35, 35, 35)
TERTIARY = QColor(42, 130, 218)


def css_rgb(color, a=False):
    """Get a CSS `rgb` or `rgba` string from a `QtGui.QColor`."""
    return ("rgba({}, {}, {}, {})" if a else "rgb({}, {}, {})").format(*color.getRgb())


class QDarkPalette(QPalette):
    """Set Dark palette for Qt meant to be used with the Fusion theme."""

    def __init__(self, *__args):
        """Initialize Palettes."""
        super().__init__(*__args)

        # Set all the colors based on the constants in globals
        self.setColor(QPalette.Window,          PRIMARY)
        self.setColor(QPalette.WindowText,      WHITE)
        self.setColor(QPalette.Base,            SECONDARY)
        self.setColor(QPalette.AlternateBase,   PRIMARY)
        self.setColor(QPalette.ToolTipBase,     WHITE)
        self.setColor(QPalette.ToolTipText,     WHITE)
        self.setColor(QPalette.Text,            WHITE)
        self.setColor(QPalette.Button,          PRIMARY)
        self.setColor(QPalette.ButtonText,      WHITE)
        self.setColor(QPalette.BrightText,      RED)
        self.setColor(QPalette.Link,            TERTIARY)
        self.setColor(QPalette.Highlight,       TERTIARY)
        self.setColor(QPalette.HighlightedText, BLACK)

    @staticmethod
    def set_stylesheet(app):
        """Start method to set the tooltip stylesheet to a `QtApplication`."""
        app.setStyleSheet("QToolTip {{"
                          "color: {white};"
                          "background-color: {tertiary};"
                          "border: 1px solid {white};"
                          "}}".format(white=css_rgb(WHITE), tertiary=css_rgb(TERTIARY)))

    def set_app(self, app):
        """Set the Fusion theme and this palette to a `QApplication`."""
        app.setStyle("Fusion")
        app.setPalette(self)
        self.set_stylesheet(app)


class UiSteamLogin(QtWidgets.QDialog):
    """Make Steam Login Window."""

    def __init__(self):
        """Initialize Steam Login Window."""
        super(UiSteamLogin, self).__init__()
        uic.loadUi(uiLoginFilePath, self)
        self.setWindowTitle('Steam Login Data')
        self.lineEdit.setText(steam_user)
        self.lineEdit_2.setText(steam_pw)

        self.accepted.connect(self.setLoginData)

    def setLoginData(self):
        steam_userNEW = self.lineEdit.text()
        steam_pwNEW = self.lineEdit_2.text()
        writeSettings(installPath, steam_userNEW, steam_pwNEW)



class Ui(QtWidgets.QDialog):
    """Make Main Window."""

    def __init__(self):
        """Initialize Main Window."""
        super(Ui, self).__init__()
        uic.loadUi(uiFilePath, self)
        #self.widget_4.click.connect(self.openURL)
        self.widget_4.installEventFilter(self)
        self.fillComboBoxServer()
        self.fillComboBoxConfigs()
        self.comboBox.activated.connect(self.getCombo)
        self.comboBox_2.activated.connect(self.getComboConfigs)
        self.toolButton.clicked.connect(self.saveFileDialog)
        self.lineEdit_5.setText(installPath)
        self.pushButton_9.clicked.connect(self.handleOpenDialog)
        self.pushButton_4.clicked.connect(self.addServer)
        self.pushButton_5.clicked.connect(self.removeServer)
        self.pushButton_6.clicked.connect(lambda: updateServer())
        self.show()

    def handleOpenDialog(self):
        """Show Steam Login Window."""
        self.dialog = UiSteamLogin()
        self.dialog.exec_()

    def getCombo(self):
        """Show Steam Login Window."""
        global selectedServer
        selectedServer = self.comboBox.currentText()
        self.fillComboBoxConfigs()

    def getComboConfigs(self):
        """Show Steam Login Window."""
        global selectedConfig
        selectedConfig = self.comboBox_2.currentText()
        self.readServerSettings()

    def addServer(self):
        """Show Steam Login Window."""
        serverName = self.lineEdit_6.text()
        serverName = '_PC2DS-' + serverName
        if(self.lineEdit_6.text() == ''):
            pass
        else:
            installServer(serverName)
            self.lineEdit_6.setText('')
            self.fillComboBoxServer()
            index = self.comboBox.findText(serverName, QtCore.Qt.MatchFixedString)
            if index >= 0:
                 self.comboBox.setCurrentIndex(index)

    def removeServer(self):
        """Show Steam Login Window."""
        selectedServer = self.comboBox.currentText()
        removeSelectedServer(selectedServer)
        self.fillComboBoxServer()
        self.fillComboBoxConfigs()

    def saveFileDialog(self):
        my_dir = QFileDialog.getExistingDirectory(self, "Open a folder", installPath, QFileDialog.ShowDirsOnly)
        if(my_dir == ''):
            my_dir = installPath

        else:
            writeSettings(my_dir, steam_user, steam_pw)
            readSettings()
            self.fillComboBoxServer()
            self.fillComboBoxConfigs()
            self.lineEdit_5.setText(installPath)

    def eventFilter(self, target, event):
        """Start Main Function."""
        if target == self.widget_4 and event.type() == QtCore.QEvent.MouseButtonPress:
            self.openURL()

        return False

    def fillComboBoxServer(self):
        """Start Main Function."""



        self.comboBox.clear()
        output = []
        if os.path.isdir(installPath):
            for d in os.listdir(installPath):
                if os.path.isdir(os.path.join(installPath, d)):
                    if '_steamcmd_' not in d and '_PC2DS-' in d:
                        output.append(d)

        else:
            output = []

        self.comboBox.addItems(output)
        global selectedServer
        selectedServer = self.comboBox.currentText()
        self.fillComboBoxConfigs()

    def fillComboBoxConfigs(self):
        """Start Main Function."""
        self.comboBox_2.clear()
        self.comboBox_6.clear()
        self.comboBox_12.clear()
        self.comboBox_13.clear()
        self.comboBox_14.clear()
        self.comboBox_15.clear()
        self.comboBox_11.clear()
        self.comboBox_4.clear()

        self.comboBox_16.clear()
        self.comboBox_17.clear()
        self.comboBox_18.clear()

        self.comboBox_21.clear()
        self.comboBox_22.clear()
        self.comboBox_23.clear()

        ProgressValues = ['Realtime', '0x', '2x', '5x', '10x', '15x', '20x', '25x', '30x', '40x', '50x', '60x']

        self.comboBox_21.addItems(ProgressValues)
        self.comboBox_22.addItems(ProgressValues)
        self.comboBox_23.addItems(ProgressValues)

        timeValue = list(range(0, 23+1))
        timeValue = [str(x) for x in timeValue]

        self.comboBox_16.addItems(timeValue)
        self.comboBox_17.addItems(timeValue)
        self.comboBox_18.addItems(timeValue)

        maxPlayers = list(range(1, 32+1))
        maxPlayers = [str(x) for x in maxPlayers]
        maxPlayers.append('AUTO')
        self.comboBox_4.addItems(maxPlayers)

        ClassSlots = list(range(1, 4+1))
        ClassSlots = [str(x) for x in ClassSlots]
        ClassSlots.append('ALL')
        self.comboBox_11.addItems(ClassSlots)

        ServerConfigsPath = os.path.join(installPath, self.comboBox.currentText(), 'DedicatedServerWrapperCMDtool', 'configs')

        output = []
        if os.path.isdir(ServerConfigsPath):
            for d in os.listdir(ServerConfigsPath):
                if os.path.isdir(os.path.join(installPath, d)):
                    output = []
                else:
                    if '.ini' in d:
                        output.append(d)
        else:
            output = []

        trackFile = os.path.join(folderCurrent, 'help', 'tracks.txt')

        tracksAll = []
        with open(trackFile, "r", encoding='utf8') as trackFileIO:
            for line in trackFileIO:
                line = re.search('".*"', line).group(0)
                line = line.replace('"', '')
                tracksAll.append(line)
        self.comboBox_6.addItems(tracksAll)




        classesFile = os.path.join(folderCurrent, 'help', 'classes.txt')

        classesAll = []
        with open(classesFile, "r", encoding='utf8') as classesFileIO:
            for line in classesFileIO:
                line = line.replace('"', '')
                classesAll.append(line)
        self.comboBox_12.addItems(classesAll)
        self.comboBox_13.addItems(classesAll)
        self.comboBox_14.addItems(classesAll)
        self.comboBox_15.addItems(classesAll)




        self.comboBox_2.addItems(output)
        global selectedConfig
        selectedConfig = self.comboBox_2.currentText()
        if (selectedConfig != ''):
            self.readServerSettings()

    def readServerSettings(self):
        ServerConfigsPath = os.path.join(installPath, selectedServer, 'DedicatedServerWrapperCMDtool', 'configs', selectedConfig)
        config = ConfigParser()
        config.read(ServerConfigsPath, encoding='utf8')


        self.lineEdit_2.setText(config['SETTINGS']['ServerName'])
        self.lineEdit_3.setText(config['SETTINGS']['Password'])
        self.lineEdit_4.setText(config['SETTINGS']['ServerRestart'])

        self.lineEdit_14.setText(config['SERVERSETTINGS']['hostPort'])
        self.lineEdit_15.setText(config['SERVERSETTINGS']['queryPort'])

        self.lineEdit_16.setText(config['SERVERSETTINGS']['sleepWaiting'])
        self.lineEdit_17.setText(config['SERVERSETTINGS']['sleepActive'])

        if(config['SETTINGS']['PracticeServer'] == '1'):
            self.checkBox.setChecked(True)
        else:
            self.checkBox.setChecked(False)

        if(config['WEATHERCHANCE']['Sunshine'] == '1'):
            self.checkBox_2.setChecked(True)
        else:
            self.checkBox_2.setChecked(False)

        if(config['SERVERSETTINGS']['selectDS'] == '1'):
            self.checkBox_4.setChecked(True)
        else:
            self.checkBox_4.setChecked(False)

        if(config['SERVERSETTINGS']['enableHttpApi'] == '1'):
            self.checkBox_3.setChecked(True)
        else:
            self.checkBox_3.setChecked(False)


        if(config['WEATHERCHANCE']['AuthenticWeather'] == '1'):
            self.checkBox_10.setChecked(True)
        else:
            self.checkBox_10.setChecked(False)





        if(config['RACESETTINGS']['MandatoryPitStop'] == '1'):
            self.checkBox_5.setChecked(True)
        else:
            self.checkBox_5.setChecked(False)

        if(config['RACESETTINGS']['Cooldownlap'] == '1'):
            self.checkBox_6.setChecked(True)
        else:
            self.checkBox_6.setChecked(False)

        if(config['RACESETTINGS']['Formationlap'] == '1'):
            self.checkBox_7.setChecked(True)
        else:
            self.checkBox_7.setChecked(False)

        if(config['RACESETTINGS']['Rollingstart'] == '1'):
            self.checkBox_9.setChecked(True)
        else:
            self.checkBox_9.setChecked(False)

        MaxGrid = config['SETTINGS']['MaxGrid']
        if MaxGrid == 'max':
            MaxGrid = 'AUTO'

        index = self.comboBox_4.findText(MaxGrid, QtCore.Qt.MatchFixedString)
        if index >= 0:
             self.comboBox_4.setCurrentIndex(index)

        trackConfig = config['RACESETTINGS']['Track']
        trackFile = os.path.join(folderCurrent, 'help', 'tracks.txt')

        with open(trackFile, "r", encoding='utf8') as trackFileIO:
            for line in trackFileIO:
                line = re.search('".*"', line).group(0)
                line = line.replace('"', '')
                if trackConfig in line:
                    trackCurrent = line


        index = self.comboBox_6.findText(trackCurrent, QtCore.Qt.MatchFixedString)
        if index >= 0:
             self.comboBox_6.setCurrentIndex(index)

        ClassSlots = config['RACESETTINGS']['ClassSlots']
        if ClassSlots == '0':
            ClassSlots = 'ALL'

        index = self.comboBox_11.findText(ClassSlots, QtCore.Qt.MatchFixedString)
        if index >= 0:
             self.comboBox_11.setCurrentIndex(index)







        class01Config = config['RACESETTINGS']['Class1']
        class02Config = config['RACESETTINGS']['Class2']
        class03Config = config['RACESETTINGS']['Class3']
        class04Config = config['RACESETTINGS']['Class4']

        classesFile = os.path.join(folderCurrent, 'help', 'classes.txt')

        with open(classesFile, "r", encoding='utf8') as classesFileIO:
            for line in classesFileIO:
                line = line.replace('"', '')
                if class01Config in line:
                    class01Current = line
                if class02Config in line:
                    class02Current = line
                if class03Config in line:
                    class03Current = line
                if class04Config in line:
                    class04Current = line


        index = self.comboBox_12.findText(class01Current, QtCore.Qt.MatchFixedString)
        if index >= 0:
             self.comboBox_12.setCurrentIndex(index)
        index = self.comboBox_14.findText(class02Current, QtCore.Qt.MatchFixedString)
        if index >= 0:
             self.comboBox_14.setCurrentIndex(index)
        index = self.comboBox_13.findText(class03Current, QtCore.Qt.MatchFixedString)
        if index >= 0:
             self.comboBox_13.setCurrentIndex(index)
        index = self.comboBox_15.findText(class04Current, QtCore.Qt.MatchFixedString)
        if index >= 0:
             self.comboBox_15.setCurrentIndex(index)


        Year = config['RACESETTINGS']['Year']
        Month = config['RACESETTINGS']['Month']
        if (Month == '10' or Month == '11' or Month == '12'):
            pass
        else:
            Month = '0' + Month
        Day = config['RACESETTINGS']['Day']
        if (len(Day) - Day.count(" ")) < 2:
            Day = '0' + Day
        myPythonicDate = Year + '-' + Month + '-' + Day
        qtDate = QtCore.QDate.fromString(myPythonicDate, 'yyyy-MM-dd')
        self.dateEdit.setDate(qtDate)


        TimePractice = config['RACESETTINGS']['TimePractice']
        TimeQuali = config['RACESETTINGS']['TimeQuali']
        TimeRace = config['RACESETTINGS']['TimeRace']

        index = self.comboBox_16.findText(TimePractice, QtCore.Qt.MatchFixedString)
        if index >= 0:
             self.comboBox_16.setCurrentIndex(index)

        index = self.comboBox_17.findText(TimeQuali, QtCore.Qt.MatchFixedString)
        if index >= 0:
             self.comboBox_17.setCurrentIndex(index)

        index = self.comboBox_18.findText(TimeRace, QtCore.Qt.MatchFixedString)
        if index >= 0:
             self.comboBox_18.setCurrentIndex(index)


        self.lineEdit_18.setText(config['RACESETTINGS']['PracticeLenght'])
        self.lineEdit_19.setText(config['RACESETTINGS']['QualifyLenght'])

        RaceLenght = config['RACESETTINGS']['RaceLenght']
        if (RaceLenght.endswith(('L'))):
            self.checkBox_8.setChecked(True)
            RaceLenght = RaceLenght[:-1]
        else:
            self.checkBox_8.setChecked(False)
            RaceLenght = RaceLenght[:-1]
        self.lineEdit_20.setText(RaceLenght)


        DateprogressP = config['RACESETTINGS']['DateprogressP']
        DateprogressQ = config['RACESETTINGS']['DateprogressQ']
        DateprogressR = config['RACESETTINGS']['DateprogressR']

        index = self.comboBox_21.findText(DateprogressP, QtCore.Qt.MatchFixedString)
        if index >= 0:
             self.comboBox_21.setCurrentIndex(index)

        index = self.comboBox_22.findText(DateprogressQ, QtCore.Qt.MatchFixedString)
        if index >= 0:
             self.comboBox_22.setCurrentIndex(index)

        index = self.comboBox_23.findText(DateprogressR, QtCore.Qt.MatchFixedString)
        if index >= 0:
             self.comboBox_23.setCurrentIndex(index)


        if(config['WEATHERCHANCE']['AuthenticWeather'] == '1'):
            self.checkBox_10.setChecked(True)
        else:
            self.checkBox_10.setChecked(False)




        Clear = int(config['WEATHERCHANCE']['Clear'])
        LightCloud = int(config['WEATHERCHANCE']['LightCloud'])
        MediumCloud = int(config['WEATHERCHANCE']['MediumCloud'])
        HeavyCloud = int(config['WEATHERCHANCE']['HeavyCloud'])
        Overcast = int(config['WEATHERCHANCE']['Overcast'])
        LightRain = int(config['WEATHERCHANCE']['LightRain'])
        Rain = int(config['WEATHERCHANCE']['Rain'])
        Storm = int(config['WEATHERCHANCE']['Storm'])
        ThunderStorm = int(config['WEATHERCHANCE']['ThunderStorm'])
        snow = int(config['WEATHERCHANCE']['snow'])
        heavysnow = int(config['WEATHERCHANCE']['heavysnow'])
        blizzard = int(config['WEATHERCHANCE']['blizzard'])
        Foggy = int(config['WEATHERCHANCE']['Foggy'])
        FogWithRain = int(config['WEATHERCHANCE']['FogWithRain'])
        HeavyFog = int(config['WEATHERCHANCE']['HeavyFog'])
        HeavyFogWithRain = int(config['WEATHERCHANCE']['HeavyFogWithRain'])
        Hazy = int(config['WEATHERCHANCE']['Hazy'])

        self.horizontalSlider_7.setValue(Clear)
        self.horizontalSlider.setValue(LightCloud)
        self.horizontalSlider_2.setValue(MediumCloud)
        self.horizontalSlider_3.setValue(HeavyCloud)
        self.horizontalSlider_4.setValue(Overcast)
        self.horizontalSlider_5.setValue(LightRain)
        self.horizontalSlider_6.setValue(Rain)
        self.horizontalSlider_13.setValue(Storm)
        self.horizontalSlider_8.setValue(ThunderStorm)
        self.horizontalSlider_9.setValue(snow)
        self.horizontalSlider_10.setValue(heavysnow)
        self.horizontalSlider_11.setValue(blizzard)
        self.horizontalSlider_12.setValue(Foggy)
        self.horizontalSlider_17.setValue(FogWithRain)
        self.horizontalSlider_14.setValue(HeavyFog)
        self.horizontalSlider_16.setValue(HeavyFogWithRain)
        self.horizontalSlider_15.setValue(Hazy)


    def openURL(self):
        """Start Main Function."""
        webbrowser.open_new_tab('http://www.gef-gaming.de/forum')


def main():
    """Start Main Function."""
    app = QtWidgets.QApplication(sys.argv)
    # font = QFont()
    # font.setPointSize(7)
    # app.setFont(font)
    QDarkPalette().set_app(app)
    window = Start()
    window.setWindowTitle(
        'Project Cars 2 Dedicated Server wrapper 1.1 - by GEF-GAMING.DE')

    sys.exit(app.exec_())


if __name__ == '__main__':
    uiFilePath = resource_path("ui/interfaceNEW.ui")
    uiLoginFilePath = resource_path("ui/interfaceLogin.ui")
    if getattr(sys, 'frozen', False):
        folderCurrent = os.path.dirname(sys.executable)
        settingsPath = os.path.abspath(os.path.join(folderCurrent, 'data', 'settings.ini'))
    else:
        folderCurrent = os.path.abspath(os.path.dirname(__file__))
        folderCurrent = os.path.abspath(os.path.join(folderCurrent, '../'))
        settingsPath = os.path.abspath(os.path.join(folderCurrent, 'data', 'settings.ini'))

    #os.environ['GIT_PYTHON_GIT_EXECUTABLE'] = GIT_PATH
    readSettings()
    main()
