# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : Translate
Description          : Function for translate Plugin
Date                 : 2025-10-10
copyright            : (C) 2020 by Luiz Motta
email                : motta.luiz@gmail.com
 ***************************************************************************/

For create file 'qm'
1) Install pyqt5-dev-tools
2) Define that files need for translation: pluginname.pro
2.1) Define locale.ts(pt.ts, de.ts, ...)
3) Create 'locale.ts' files: pylupdate5 -verbose pluginname.pro
4) Edit your translation: QtLinquist (use Release for create 'qm' file)
4.1) 'locale.qm'
"""

__author__ = 'Luiz Motta'
__date__ = '2025-10-10'
__copyright__ = '(C) 2020, Luiz Motta'
__revision__ = '$Format:%H$'

import os

from qgis.PyQt.QtCore import QTranslator, QCoreApplication
from qgis.core import QgsApplication

CONTEXT = None
TRANSLATOR = None

def setTranslation(context:str, plugin_dir:str)->None:
    global CONTEXT
    global TRANSLATOR

    CONTEXT = context
    locale = QgsApplication.locale()
    locale_path = os.path.join( plugin_dir, 'i18n', f"{locale}.qm" )
    if os.path.exists( locale_path ):
        TRANSLATOR = QTranslator()
        TRANSLATOR.load( locale_path )
        QCoreApplication.installTranslator( TRANSLATOR )

def tr(message:str)->str:
    global CONTEXT
    if CONTEXT is None:
        return message
    return QCoreApplication.translate(CONTEXT, message)
