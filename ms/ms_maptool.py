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
  QItemSelection
)
from qgis.PyQt.QtGui import QCursor


from qgis.core import QgsLayerTreeLayer, QgsMapLayer, QgsProject
from qgis.gui import QgisInterface, QgsMapTool, QgsMapMouseEvent

from .swipemap import SwipeMap
from .translate import tr


class MapSwipeTool(QgsMapTool):
    def __init__(self, title:str, iface:QgisInterface):
        self.canvas = iface.mapCanvas()
        super().__init__( self.canvas )
        self.view = iface.layerTreeView()
        self.msg_bar = iface.messageBar()
        self.title = title
        self.swipe = SwipeMap( self.canvas )
        self.has_direction, self.has_swipe, self.disabled_swipe = None, None, None
        self.first_point = QPoint()
        self.cursor_v = QCursor( Qt.SplitVCursor )
        self.cursor_h = QCursor( Qt.SplitHCursor )

        self._signal_slot = (
            { 'signal': QgsProject.instance().removeAll, 'slot': self.disable },
            { 'signal': self.view.selectionModel().selectionChanged, 'slot': self.setLayersSwipe },
            { 'signal': self.canvas.mapCanvasRefreshed, 'slot': self.swipe.setMap }
        )
  
    def _connect(self, isConnect:bool = True)->None:
        if isConnect:
            for item in self._signal_slot:
                item['signal'].connect( item['slot'] )
            return

        for item in self._signal_slot:
            item['signal'].disconnect( item['slot'] )

    @pyqtSlot()
    def activate(self)->None:
        super().activate()
        self.canvas.setCursor( QCursor( Qt.PointingHandCursor ) )
        self._connect()
        self.has_swipe = False
        self.disabled_swipe = False
        self.setLayersSwipe( None, None )

    @pyqtSlot()
    def deactivate(self)->None:
        super().deactivate()
        self.deactivated.emit()
        self.swipe.clear()
        self._connect( False )

    @pyqtSlot(QgsMapMouseEvent)
    def canvasPressEvent(self, e:QgsMapMouseEvent)->None:
        if len( self.swipe.layers ) == 0:
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
            self.swipe.is_vertical = dX > dY
            self.has_direction = True
            self.canvas.setCursor( self.cursor_h if self.swipe.is_vertical else self.cursor_v )
        
        self.swipe.setLength( e.x(), e.y() )

    @pyqtSlot(QItemSelection,QItemSelection)
    def setLayersSwipe(self, selected:QItemSelection, deselected:QItemSelection)->None:
        def finished(layers:List[QgsMapLayer], message:str)->None:
            self.swipe.clear()
            self.swipe.setLayers( layers )
            self.swipe.setMap()

            self.msg_bar.clearWidgets()
            self.msg_bar.pushInfo( self.title, message )

        if self.disabled_swipe:
            return

        layers, msg = None, None
        node = self.view.currentNode()
        if node.itemVisibilityChecked():
            node.setItemVisibilityChecked( False )

        if isinstance( node, QgsLayerTreeLayer ):
            layer = node.layer()
            if not layer.isSpatial():
                f = tr("Active layer '{}' need be a spatial layer.")
                msg = f.format( layer.name() )
                self.msgBar.pushWarning( self.pluginName, msg )

                return

            layers = [ layer ]
            f = tr("Active layer is '{}'.")
            msg = f.format( layer.name() )
            finished( layers, msg )

            return

        group = self.view.currentGroupNode()
        if group.parent() is None: # Root
            return

        layers = [ ltl.layer() for ltl in group.findLayers() if ltl.itemVisibilityChecked() ]
        if len( layers ) ==  0:
            self.msg_bar.clearWidgets()
            f = tr("Active group '{}' need at least one item with visible checked")
            msg = f.format( group.name() )
            self.msg_bar.pushWarning( self.title, msg )

            return

        f = tr("Active group is '{}'.")
        msg = f.format( group.name() )
        finished( layers, msg )

    @pyqtSlot()
    def disable(self):
        self.swipe.clear()
        self.has_swipe = False
        self.disabled_swipe = True
