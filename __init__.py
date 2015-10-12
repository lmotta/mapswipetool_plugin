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
from PyQt4.QtCore import pyqtSlot

from mapswipetool import MapSwipeTool

import os

def classFactory(iface):
  return MapSwipePlugin( iface )

class MapSwipePlugin:

  def __init__(self, iface):
    self.iface = iface
    self.canvas = iface.mapCanvas() 

    self.action = None
    self.tool = MapSwipeTool( self.iface )

  def initGui(self):
    title = "Map swipe tool"
    icon = QIcon( os.path.join( os.path.dirname(__file__), 'mapswipetool.png' ) )
    self.action = QAction( icon, title, self.iface.mainWindow() )
    self.action.setObjectName( "MapSwipeTool" )
    self.action.setWhatsThis( title )
    self.action.setStatusTip( title )
    self.action.triggered.connect( self.run )

    # Maptool
    self.action.setCheckable( True )
    self.tool.setAction( self.action )

    self.iface.addToolBarIcon( self.action )

  def unload(self):
    self.canvas.unsetMapTool( self.tool )
    self.iface.removeToolBarIcon( self.action )
    del self.action

  @pyqtSlot()
  def run(self):
    if self.canvas.mapTool() != self.tool:
      self.canvas.setMapTool( self.tool)
