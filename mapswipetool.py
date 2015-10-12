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

from PyQt4.QtCore import ( Qt, QPoint, pyqtSlot )
from PyQt4.QtGui import ( QCursor )

from qgis.gui import ( QgsMessageBar, QgsMapTool )
from qgis.core import ( QgsLayerTreeLayer, QgsMapLayerRegistry )

from swipemap import SwipeMap

class MapSwipeTool(QgsMapTool):
  def __init__(self, iface):
    canvas = iface.mapCanvas()
    super(MapSwipeTool, self).__init__( canvas )
    self.view = iface.layerTreeView()
    self.msgBar = iface.messageBar()
    self.swipe = SwipeMap( canvas )
    self.checkDirection =  self.hasSwipe = self.disabledSwipe = None
    self.firstPoint = QPoint()
    self.cursorV = QCursor( Qt.SplitVCursor )
    self.cursorH = QCursor( Qt.SplitHCursor )
  
  def activate(self):
    canvas = self.canvas()
    canvas.setCursor( QCursor( Qt.CrossCursor ) )

    canvas.mapCanvasRefreshed.connect( self.swipe.setMap )
    self.view.currentLayerChanged.connect( self.setLayersSwipe )
    QgsMapLayerRegistry.instance().removeAll.connect( self.disable )

    self.hasSwipe = False
    self.disabledSwipe = False
    
    node = self.view.currentNode()
    layer = self.view.currentNode().layer() if isinstance( node, QgsLayerTreeLayer ) else None 
    self.setLayersSwipe( layer )

  def canvasPressEvent(self, e):
    if len(self.swipe.layers) == 0:
      msg = "Select active Layer or Group(with layers)  in legend."
      self.msgBar.clearWidgets()
      self.msgBar.pushMessage( "MapSwipeTool", msg, QgsMessageBar.WARNING, 4 )
      return
    
    self.hasSwipe = True
    self.firstPoint.setX( e.x() )
    self.firstPoint.setY( e.y() )
    self.checkDirection = True

  def canvasReleaseEvent(self, e):
    self.hasSwipe = False
    self.canvas().setCursor( QCursor( Qt.CrossCursor ) )
    
  def canvasMoveEvent(self, e):
    if self.hasSwipe:
      if self.checkDirection:
        dX = abs( e.x() - self.firstPoint.x() )
        dY = abs( e.y() - self.firstPoint.y() )
        isVertical = dX > dY
        self.swipe.setIsVertical( isVertical )
        self.checkDirection = False
        self.canvas().setCursor( self.cursorH if isVertical else self.cursorV )
        
      self.swipe.setLength( e.x(), e.y() )

  @pyqtSlot( "QgsMapLayer" )
  def setLayersSwipe(self, layer):
    if self.disabledSwipe:
      return

    if layer is None and self.view.currentGroupNode().parent() is None: # Root
      return

    ids = msg = None
    if layer is None:
      group = self.view.currentGroupNode()
      ids = group.findLayerIds()
      msg = "Active group is '%s'." % group.name()
    else:
      ids = [ layer.id() ]
      msg = "Active layer is '%s'." % layer.name()
      
    self.swipe.clear()
    self.swipe.setLayersId( ids )
    self.msgBar.clearWidgets()
    self.msgBar.pushMessage( "MapSwipeTool", msg, QgsMessageBar.INFO, 2 )
    self.swipe.setMap()

  @pyqtSlot()
  def disable(self):
    self.swipe.clear()
    self.hasSwipe = False
    self.disabledSwipe = True
  
  def deactivate(self):
      super( MapSwipeTool, self ).deactivate()
      self.deactivated.emit()
      self.swipe.clear()

      self.canvas().mapCanvasRefreshed.disconnect( self.swipe.setMap )
      self.view.currentLayerChanged.disconnect( self.setLayersSwipe )
      QgsMapLayerRegistry.instance().removeAll.disconnect( self.disable )
      

