# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Translate
Description          : Class for translate Plugin
Date                 : 2018-10-19
copyright            : (C) 2018 by Luiz Motta
email                : motta.luiz@gmail.com
 ***************************************************************************/

For create file 'qm'
1) Install pyqt5-dev-tools
2) Define that files need for translation: pluginname.pro
3) Create 'ts': pylupdate5 -verbose pluginname.pro
4) Edit your translation: QtLinquist (use Release for create 'qm' file)
"""

__author__ = 'Luiz Motta'
__date__ = '2018-10-19'
__copyright__ = '(C) 2016, Luiz Motta'
__revision__ = '$Format:%H$'


import os

from qgis.PyQt.QtCore import QFileInfo, QSettings, QLocale, QTranslator, QCoreApplication
from qgis.core import QgsApplication

class Translate():
  def __init__(self, pluginName):
    def getFile():
      overrideLocale = QSettings().value('locale/overrideFlag', False, type=bool)
      localeFullName = QLocale.system().name() if not overrideLocale else QSettings().value('locale/userLocale', '')
      qmPathFile = f"i18n/{pluginName}_{localeFullName}.qm"
      pluginPath = os.path.dirname(__file__)
      translationFile = f"{pluginPath}/{qmPathFile}"
      return translationFile

    self.translator = None
    translationFile = getFile()
    if QFileInfo( translationFile ).exists():
        self.translator = QTranslator()
        self.translator.load( translationFile )
        QCoreApplication.installTranslator( self.translator )
