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
2) Define that files need for translation: mapswipetool.pro
3) Create 'ts': pylupdate5 -verbose mapswipetool.pro
* pylupdate5 -verbose -translate-function self._tr mapswipetool.pro
4) Edit your translation: QtLinquist (use Release for create 'qm' file)
"""

from qgis.PyQt.QtCore import QFileInfo, QSettings, QLocale, QTranslator, QCoreApplication
from qgis.core import QgsApplication

class Translate():
  def __init__(self, pluginName, nameDir=None):
    def getFile():
      pluginPath = "python/plugins/{}".format( nameDir )

      userPath = QFileInfo( QgsApplication.qgisUserDatabaseFilePath() ).path()
      userPluginPath = "{0}/{1}".format( userPath, pluginPath)
      
      systemPath = QgsApplication.prefixPath()
      systemPluginPath = "{0}/{1}".format( systemPath, pluginPath )
      
      overrideLocale = QSettings().value('locale/overrideFlag', False, type=bool)
      localeFullName = QLocale.system().name() if not overrideLocale else QSettings().value('locale/userLocale', '')

      qmPathFile = "/i18n/{0}_{1}.qm".format( pluginName, localeFullName )
      pp = userPluginPath if QFileInfo(userPluginPath).exists() else systemPluginPath
      return "{0}{1}".format( pp, qmPathFile )

    if nameDir is None:
      nameDir = pluginName

    self.translator = None
    translationFile = getFile()
    if QFileInfo( translationFile ).exists():
        self.translator = QTranslator()
        self.translator.load( translationFile )
        QCoreApplication.installTranslator( self.translator )
