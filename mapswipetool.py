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

from PyQt4.QtCore import ( Qt, QPoint, pyqtSlot, QCoreApplication )
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
  
  def tr(self, sourceText):
    context = 'MapSwipeTool'    
    return QCoreApplication.translate( context, sourceText )
  
  def activate(self):
    self.canvas().setCursor( QCursor( Qt.CrossCursor ) )

    self._connect()

    self.hasSwipe = False
    self.disabledSwipe = False
    
    self.setLayersSwipe( self.view.currentIndex() )

  def canvasPressEvent(self, e):
    if len(self.swipe.layers) == 0:
      msg = self.tr( "Select active Layer or Group(with layers) in legend." )
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

  def _connect(self, isConnect = True):
    signal_slot = (
      { 'signal': self.canvas().mapCanvasRefreshed, 'slot': self.swipe.setMap },
      { 'signal': self.view.activated, 'slot': self.setLayersSwipe },
      { 'signal': QgsMapLayerRegistry.instance().removeAll, 'slot': self.disable }
    )
    if isConnect:
      for item in signal_slot:
        item['signal'].connect( item['slot'] )
    else:
      for item in signal_slot:
        item['signal'].disconnect( item['slot'] )

  @pyqtSlot( "QModelIndex" )
  def setLayersSwipe(self, index):
    if self.disabledSwipe:
      return

    ids = msg = None
    node = self.view.currentNode()
    if isinstance( node, QgsLayerTreeLayer ):
      layer = node.layer()
      ids = [ layer.id() ]
      msg = self.tr( "Active layer is '%s'." ) % layer.name()
    else:
      group = self.view.currentGroupNode()
      if group.parent() is None: # Root
        return
      ids = group.findLayerIds()
      msg = self.tr( "Active group is '%s'." ) % group.name()

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
      self._connect( False )
      

