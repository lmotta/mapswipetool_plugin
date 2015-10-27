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

from PyQt4.QtCore import ( QRect, QLine, pyqtSlot )

from qgis.core import ( QgsMapRendererParallelJob, QgsMapSettings )
from qgis.gui import ( QgsMapCanvasMap )

class SwipeMap(QgsMapCanvasMap):
  def __init__(self, canvas):
    super(SwipeMap, self).__init__(canvas)
    self.length = 0
    self.isVertical = True
    self.setZValue(-9.0)
    self.flg = False
    self.layers = []
    self.canvas = canvas
      
  def clear(self):
    del self.layers[:]
    self.length = -1

  def setLayersId(self, layers):
    del self.layers[:]
    for item in layers:
      self.layers.append(item)

  def setIsVertical(self, isVertical):
    self.isVertical = isVertical

  def setLength(self, x, y):
    y = self.boundingRect().height() - y
    self.length = x if self.isVertical else y
    self.update()
      
<<<<<<< HEAD
  def paint(self, painter, *args): # NEED *args for   WINDOWS!
=======
  def paint(self, painter, *args):
>>>>>>> origin/patch-3
    if len( self.layers ) == 0 or self.length == -1:
      return
  
    if self.isVertical:
    	h = self.boundingRect().height() - 2
    	w = self.length
    	line = QLine( w-1,0,w-1,h-1 )
    else:
    	h = self.boundingRect().height() - self.length
    	w = self.boundingRect().width() - 2
    	line = QLine( 0,h-1,w-1,h-1 )
  
    image = self.contentImage().copy( 0, 0, w, h )
    painter.drawImage( QRect( 0,0,w,h ), image )
    painter.drawLine( line )

  @pyqtSlot()
  def setMap(self):
    def finished():
      super(SwipeMap, self).setContent( job.renderedImage(), self.canvas.extent() )

    if len( self.layers ) == 0:
      return

    settings = QgsMapSettings( self.canvas.mapSettings() )
    settings.setLayers( self.layers )
    
    job = QgsMapRendererParallelJob( settings) 
    job.start()
    job.finished.connect( finished) 
    job.waitForFinished()
