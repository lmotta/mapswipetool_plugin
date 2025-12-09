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


from typing import List

from qgis._core import QgsLayerTreeLayer
from qgis.PyQt.QtCore import (
  Qt,
  QPoint,
  pyqtSlot,
  QModelIndex
)
from qgis.PyQt.QtGui import QCursor

from qgis.core import (
    QgsMapLayer,
    QgsLayerTreeNode, QgsLayerTreeLayer, QgsLayerTreeGroup,
    QgsProject
)
from qgis.gui import (
    QgisInterface,
    QgsMapTool,
    QgsMapMouseEvent
)

from .swipemap import SwipeMap
from .translate import tr


class MapSwipeTool(QgsMapTool):
    def __init__(self, title:str, iface:QgisInterface):
        self.title = title
        self.canvas = iface.mapCanvas()
        super().__init__( self.canvas )
        self.view = iface.layerTreeView()
        self.msg_bar = iface.messageBar()
        self.project = QgsProject.instance()
        self.has_direction, self.has_swipe, self.disabled_swipe = None, None, None
        self.first_point = QPoint()
        self.cursor_v = QCursor( Qt.SplitVCursor )
        self.cursor_h = QCursor( Qt.SplitHCursor )

        self.swipe_map = SwipeMap( self.canvas )

        self.current_swipe = None

        self._signal_slot = (
            { 'signal': self.project.removeAll, 'slot': self.disable },
            { 'signal': self.view.selectionModel().currentChanged, 'slot': self.setLayers },
            { 'signal': self.canvas.extentsChanged, 'slot': self.swipe_map.setImage },
            # self.swipe_map Signals
            {
                'signal': self.swipe_map.signals.creatingImage,
                'slot': lambda: self.msg_bar.pushMessage(
                    self.title,
                    tr('Swipe image rendering in progress ({})...').format( self.current_swipe )
                )
            },
            {
                'signal': self.swipe_map.signals.finishedImage,
                'slot': lambda: self.msg_bar.clearWidgets()
            }
      )
  
    def _connect(self, isConnect:bool = True)->None:
        if isConnect:
            for item in self._signal_slot:
                item['signal'].connect( item['slot'] )
            return

        for item in self._signal_slot:
            item['signal'].disconnect( item['slot'] )

    def canExecute(self):
        if not len( self.project.mapLayers() ):
            self.msg_bar.pushWarning( self.title, tr('Missing layers required for tool.') )
            return False
        
        return True

    @pyqtSlot()
    def disable(self):
        self.swipe_map.clear()
        self.has_swipe = False
        self.disabled_swipe = True

    @pyqtSlot(QModelIndex,QModelIndex)
    def setLayers(self, current:QModelIndex, previous:QModelIndex)->None:
        def finished(node:QgsLayerTreeNode, layers:List[QgsMapLayer])->None:
            self.swipe_map.layers = layers
            self.current_swipe = node.name()

            # Set image of Magnifier
            is_checked = node.itemVisibilityChecked()
            if not is_checked:
                node.setItemVisibilityChecked( True )
            self.swipe_map.setImage()
            if not is_checked:
                node.setItemVisibilityChecked( False )

        def setTreeLayer(node:QgsLayerTreeLayer):
            layer = node.layer()
            if layer in self.swipe_map.layers:
                return

            if not layer.isSpatial():
                f = tr("Active layer '{}' need be a spatial layer.")
                msg = f.format( layer.name() )
                self.msgBar.pushWarning( self.pluginName, msg )

                return

            finished( node, [ layer ] )

        def setTreeGroup(node:QgsLayerTreeGroup):
            layers = [ ltl.layer() for ltl in node.findLayers() if ltl.itemVisibilityChecked() ]
            if not layers:
                self.msg_bar.clearWidgets()
                f = tr("Active group '{}' need at least one item with visible checked")
                msg = f.format( node.name() )
                self.msg_bar.pushWarning( self.title, msg )

                return
            
            finished( node, layers )

        if self.disabled_swipe or current is None:
            return

        node = self.view.index2node( current )
        if node is None: # index is subtree
            return

        if self.project.layerTreeRoot() == node:
            self.disable()
            self.msg_bar.clearWidgets()
            return

        if isinstance( node, QgsLayerTreeLayer ):
            setTreeLayer( node )
            return

        if isinstance( node, QgsLayerTreeGroup ):
            setTreeGroup( node )

    # QgsMapTool Signals
    @pyqtSlot()
    def activate(self)->None:
        super().activate()
        self.canvas.setCursor( QCursor( Qt.PointingHandCursor ) )
        self._connect()
        self.has_swipe = False
        self.disabled_swipe = False
        self.setLayers( self.view.currentIndex(), None )

    @pyqtSlot()
    def deactivate(self)->None:
        super().deactivate()
        self.deactivated.emit()
        self._connect( False )
        self.disable()
        self.msg_bar.clearWidgets()

    @pyqtSlot(QgsMapMouseEvent)
    def canvasPressEvent(self, e:QgsMapMouseEvent)->None:
        if not self.swipe_map.layers:
            self.msg_bar.clearWidgets()
            self.msg_bar.pushWarning( self.title, tr('Select Layer or Group in legend.') )

            return

        self.has_swipe = True
        self.first_point.setX( e.x() )
        self.first_point.setY( e.y() )
        self.has_direction = False

    @pyqtSlot(QgsMapMouseEvent)
    def canvasReleaseEvent(self, e:QgsMapMouseEvent)->None:
        self.has_swipe = False
        self.canvas.setCursor( QCursor( Qt.PointingHandCursor ) )
    
    @pyqtSlot(QgsMapMouseEvent)
    def canvasMoveEvent(self, e:QgsMapMouseEvent)->None:
        if not self.has_swipe:
            return

        if not self.has_direction:
            dX = abs( e.x() - self.first_point.x() )
            dY = abs( e.y() - self.first_point.y() )
            self.swipe_map.is_vertical = dX > dY
            self.has_direction = True
            self.canvas.setCursor( self.cursor_h if self.swipe_map.is_vertical else self.cursor_v )
        
        self.swipe_map.setLength( e.x(), e.y() )
