# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : MapSwipe tool
Description          : Plugin for swipe active layer
Date                 : October, 2015
copyright            : (C) 2015 by Hirofumi Hayashi and Luiz Motta
email                : hayashi@apptec.co.jp and motta.luiz@gmail.com

 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4.QtGui import ( QAction, QIcon )
from PyQt4.QtCore import ( QSettings, QTranslator, qVersion, QCoreApplication, pyqtSlot )

from mapswipetool import MapSwipeTool

import os

def classFactory(iface):
  return MapSwipePlugin( iface )

class MapSwipePlugin:

  def __init__(self, iface):
    
    def translate():
      #
      # For create file 'qm'
      # 1) Define that files need for translation: mapswipetool.pro
      # 2) Create 'ts': pylupdate4 -verbose mapswipetool.pro
      # 3) Edit your translation: QtLinquist
      # 4) Create 'qm': lrelease *.ts 
      #
      dirname = os.path.dirname( os.path.abspath(__file__) )
      locale = QSettings().value("locale/userLocale")
      localePath = os.path.join( dirname, "i18n", "%s_%s.qm" % ( name_src, locale ) )
      if os.path.exists(localePath):
        self.translator = QTranslator()
        self.translator.load(localePath)
        if qVersion() > '4.3.3':
          QCoreApplication.installTranslator(self.translator)      

    self.iface = iface
    self.canvas = iface.mapCanvas() 
    self.action = None # Define by initGui
    self.tool = MapSwipeTool( self.iface )
    self.prevTool = None # Define by run

    name_src = "mapswipetool"
    translate()

  def initGui(self):
    title = "Map swipe tool"
    icon = QIcon( os.path.join( os.path.dirname(__file__), 'mapswipetool.png' ) )
    self.action = QAction( icon, title, self.iface.mainWindow() )
    self.action.setObjectName( "MapSwipeTool" )
    self.action.setWhatsThis( title )
    self.action.setStatusTip( title )
    self.action.triggered.connect( self.run )
    self.menu = "&Map swipe tool"

    # Maptool
    self.action.setCheckable( True )
    self.tool.setAction( self.action )

    self.iface.addToolBarIcon( self.action )
    self.iface.addPluginToMenu( self.menu, self.action )

  def unload(self):
    self.canvas.unsetMapTool( self.tool )
    self.iface.removeToolBarIcon( self.action )
    self.iface.removePluginMenu( self.menu, self.action )
    del self.action

  @pyqtSlot()
  def run(self):
    if self.canvas.mapTool() != self.tool:
      self.prevTool = self.canvas.mapTool()
      self.canvas.setMapTool( self.tool )
    else:
      self.canvas.setMapTool( self.prevTool )

