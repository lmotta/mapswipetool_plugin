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


from qgis.PyQt.QtCore import Qt, QPoint, pyqtSlot, QCoreApplication
from qgis.PyQt.QtGui import QCursor

from qgis.core import QgsLayerTreeLayer, QgsProject
from qgis.gui import QgsMapTool

from .swipemap import SwipeMap
from .translate import Translate

class MapSwipeTool(QgsMapTool):
  def __init__(self, iface):
    canvas = iface.mapCanvas()
    super().__init__( canvas )
    self.view = iface.layerTreeView()
    self.msgBar = iface.messageBar()
    self.swipe = SwipeMap( canvas )
    self.checkDirection =  self.hasSwipe = self.disabledSwipe = None
    self.firstPoint = QPoint()
    self.cursorV = QCursor( Qt.SplitVCursor )
    self.cursorH = QCursor( Qt.SplitHCursor )
    self.pluginName = 'MapSwipeTool'
    self.translate = Translate( self.pluginName.lower() )
  
  def _connect(self, isConnect = True):
    signal_slot = (
      { 'signal': QgsProject.instance().removeAll, 'slot': self.disable },
      { 'signal': self.view.selectionModel().selectionChanged, 'slot': self.setLayersSwipe },
      { 'signal': self.canvas().mapCanvasRefreshed, 'slot': self.swipe.setMap }
    )
    if isConnect:
      for item in signal_slot:
        item['signal'].connect( item['slot'] )
    else:
      for item in signal_slot:
        item['signal'].disconnect( item['slot'] )

  def activate(self):
    super().activate()
    self.canvas().setCursor( QCursor( Qt.PointingHandCursor ) )
    self._connect()
    self.hasSwipe = False
    self.disabledSwipe = False
    self.setLayersSwipe( None, None )

  def deactivate(self):
      super().deactivate()
      self.deactivated.emit()
      self.swipe.clear()
      self._connect( False )

  def canvasPressEvent(self, e):
    if self.checkLayer():
      self.hasSwipe = True
      self.firstPoint.setX( e.x() )
      self.firstPoint.setY( e.y() )
      self.checkDirection = True

  def canvasReleaseEvent(self, e):
    self.hasSwipe = False
    self.canvas().setCursor( QCursor( Qt.PointingHandCursor ) )
    
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

  def checkLayer(self):
    if len( self.swipe.layers ) == 0:
      msg = QCoreApplication.translate('MapSwipeTool', 'Select Layer or Group in legend.')
      self.msgBar.clearWidgets()
      self.msgBar.pushWarning( self.pluginName, msg )
      return False
    else:
      return True

  @pyqtSlot('QItemSelection,QItemSelection')
  def setLayersSwipe(self, selected=None, deselected=None):
    if self.disabledSwipe:
      return

    layers = msg = None
    node = self.view.currentNode()
    if node.itemVisibilityChecked():
      node.setItemVisibilityChecked( False )
    if isinstance( node, QgsLayerTreeLayer ):
      layer = node.layer()
      if not layer.isSpatial():
        f = QCoreApplication.translate('MapSwipeTool', "Active layer '{}' need be a spatial layer." )
        msg = f.format( layer.name() )
        self.msgBar.pushWarning( self.pluginName, msg )
        return
      layers = [ layer ]
      f = QCoreApplication.translate('MapSwipeTool', "Active layer is '{}'." )
      msg = f.format( layer.name() )
    else:
      group = self.view.currentGroupNode()
      if group.parent() is None: # Root
        return
      ltls = list( filter( lambda ltl: ltl.itemVisibilityChecked(),  group.findLayers() ) )
      if len( ltls ) ==  0:
        self.msgBar.clearWidgets()
        f = QCoreApplication.translate('MapSwipeTool', "Active group '{}' need at least one item with visible checked")
        msg = f.format( group.name() )
        self.msgBar.pushWarning( self.pluginName, msg )
        return
      layers = map( lambda ltl: ltl.layer(), ltls )
      f = QCoreApplication.translate('MapSwipeTool', "Active group is '{}'.")
      msg = f.format( group.name() )

    self.swipe.clear()
    self.swipe.setLayers( layers )
    self.swipe.setMap()

    self.msgBar.clearWidgets()
    self.msgBar.pushInfo( self.pluginName, msg )

  @pyqtSlot()
  def disable(self):
    self.swipe.clear()
    self.hasSwipe = False
    self.disabledSwipe = True
