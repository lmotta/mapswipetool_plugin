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


from qgis.PyQt.QtCore import (
    Qt,
    QRect, QLine,
    QObject, pyqtSignal
)
from qgis.PyQt.QtGui import (
    QColor,
    QImage, QPainter
)

from qgis.core import (
    QgsMapRendererParallelJob,
    QgsMapSettings
)
from qgis.gui import (
    QgsMapCanvas, QgsMapCanvasItem
)


class SwipeSignals(QObject):
    creatingImage = pyqtSignal()
    finishedImage = pyqtSignal()

class SwipeMap(QgsMapCanvasItem):
    def __init__(self, canvas:QgsMapCanvas):
        self.canvas = canvas
        super().__init__( canvas )
        self.setZValue(10)

        self.signals = SwipeSignals()
        self.layers = []
        self.image = None
        self.length = 0
        self.is_vertical = True
        self.flg = False
      
    def clear(self)->None:
        self.layers = []
        self.image = None
        self.length = -1
        self.updateCanvas()

    def setLength(self, x:float, y:float)->None:
        y = int(self.boundingRect().height() - y )
        self.length = int(x) if self.is_vertical else int(y)
        self.updateCanvas() # Call self.paint
      
    def paint(self, painter:QPainter, *args): # NEED *args for   WINDOWS!
        def finished()->None:
            painter.setClipRect( region )
            painter.drawImage( 0,0, self.image )
            painter.setRenderHint( QPainter.RenderHint.Antialiasing ) # Smooths edges
            painter.drawLine( line )

        if not self.layers or self.length == -1 or self.image is None:
            return

        region = QRect(0,0,0,0)
        if self.is_vertical:
            w = int(self.length)
            h = int(self.boundingRect().height() - 2)
            region.setWidth( w )
            region.setHeight( h )
            line = QLine( w-1,0,w-1,h-1 )
            finished()

            return
        
        w = int(self.boundingRect().width() - 2) 
        h = int(self.boundingRect().height() - self.length) 
        region.setWidth( w )
        region.setHeight( h )
        line = QLine( 0,h-1,w-1,h-1 )
        finished()

    # It is a slot, the decorator 'pyqtSlot' fail because QgsMapCanvasItem not is QObject
    def setImage(self):
        def createMapSettings():
            settings = QgsMapSettings()
            settings.setBackgroundColor(QColor(Qt.GlobalColor.transparent))
            settings.setDevicePixelRatio( 1 )
            settings.setLayers( self.layers )
            settings.setDestinationCrs( self.canvas.mapSettings().destinationCrs() )
            settings.setOutputSize( self.canvas.size() )
            settings.setExtent( self.canvas.extent() )
            
            return settings

        def finished():
            image = job.renderedImage()
            if bool( self.canvas.property('retro') ):
                image = image.scaled( image.width() / 3, image.height() / 3 )
                image = image.convertToFormat( QImage.Format.Format_Indexed8, Qt.ImageConversionFlag.OrderedDither | Qt.ImageConversionFlag.OrderedAlphaDither )
            self.image = image
            self.signals.finishedImage.emit()
            self.updateCanvas()

        if not self.layers:
            return

        self.signals.creatingImage.emit()

        self.setRect( self.canvas.extent() )
        self.image = None
        job = QgsMapRendererParallelJob( createMapSettings() ) 
        job.start()
        job.finished.connect( finished ) 
        #job.waitForFinished()
