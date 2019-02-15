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

__author__ = 'Luiz Motta'
__date__ = '2015-10-14'
__copyright__ = '(C) 2018, Luiz Motta'
__revision__ = '$Format:%H$'


from qgis.PyQt.QtCore import QObject, pyqtSlot
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from .mapswipetool import MapSwipeTool

import os

def classFactory(iface):
  return MapSwipePlugin( iface )

class MapSwipePlugin(QObject):

  def __init__(self, iface):
    super().__init__()
    self.iface = iface
    self.canvas = iface.mapCanvas() 
    self.action = None # Define by initGui
    self.tool = MapSwipeTool( self.iface )
    self.prevTool = None # Define by run

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

  @pyqtSlot(bool)
  def run(self, checked):
    if self.canvas.mapTool() != self.tool:
      self.prevTool = self.canvas.mapTool()
      self.canvas.setMapTool( self.tool )
    else:
      self.canvas.setMapTool( self.prevTool )

