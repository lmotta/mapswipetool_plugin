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


import os

from qgis.PyQt.QtCore import (
    QObject,
    QDir,
    pyqtSlot
)
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from qgis.gui import QgisInterface, QgsMapTool

from .tool.maptool import MapSwipeTool
from .tool.translate import setTranslation


def classFactory(iface:QgisInterface):
    return MapSwipe( iface )

class MapSwipe(QObject):

    def __init__(self, iface:QgisInterface):
        super().__init__()
        self.iface = iface
        self.canvas = iface.mapCanvas() 

        setTranslation( type(self).__name__, os.path.dirname(__file__) )

        self.plugin_name = 'MapSwipe'
        self.action_name = 'MapSwipe'
        self.action = None
        self.maptool = None
        self.previus_maptool = None # Define by run

    def initGui(self):
        path = QDir( os.path.dirname(__file__) )
        icon = QIcon( path.filePath('resources/mapswipe.png'))
        self.action = QAction( icon, self.action_name, self.iface.mainWindow() )
        self.action.setToolTip( self.action_name )
        self.action.setCheckable(True)

        self.action.triggered.connect(self.on_Clicked)
        self.canvas.mapToolSet.connect( self.on_MapToolSet )

        self.maptool = MapSwipeTool( self.plugin_name, self.iface )
        self.previus_maptool = self.canvas.mapTool()

        self.menu_name = f"&{self.action_name}"
        self.iface.addPluginToMenu( self.menu_name, self.action )
        self.iface.addToolBarIcon( self.action )

    def unload(self)->None:
        self.iface.removePluginMenu( self.menu_name, self.action )
        self.iface.removeToolBarIcon( self.action )
        self.iface.unregisterMainWindowAction( self.action )
        
        if self.maptool:
            self.canvas.unsetMapTool( self.maptool )
        
        # Disconnect
        try:
            self.action.triggered.disconnect( self.on_Clicked )
        except Exception:
            pass
        self.action.deleteLater()

        del self.maptool

    @pyqtSlot(bool)
    def on_Clicked(self, enabled:bool)->None:
        if enabled:
            if not self.maptool.canExecute():
                self.action.setChecked(False)
                return

            self.previus_maptool = self.canvas.mapTool()
            self.canvas.setMapTool( self.maptool )
            return

        self.canvas.setMapTool( self.previus_maptool )

    @pyqtSlot(QgsMapTool, QgsMapTool)
    def on_MapToolSet(self, newTool:QgsMapTool, oldTool:QgsMapTool)->None:
        if oldTool == self.maptool:
            self.action.setChecked(False)
