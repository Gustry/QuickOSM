"""
/***************************************************************************
 QuickOSM
 A QGIS plugin
 OSM Overpass API frontend
                             -------------------
        begin                : 2014-06-11
        copyright            : (C) 2014 by 3Liz
        email                : info at 3liz dot com
        contributor          : Etienne Trimaille
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
from qgis.PyQt.QtWidgets import QStyledItemDelegate, QComboBox
from qgis.PyQt.QtCore import QStringListModel


class QueryItemDelegate(QStyledItemDelegate):

    def createEditor(self, parent, option, index):
        if index.column() == 0:
            key_editor = QComboBox(parent)
            key_editor.setEditable(True)
            model = QStringListModel(parent)
            model.setStringList(['a', 'b', 'c'])
            key_editor.setModel(model)
            key_editor.lineEdit().setPlaceholderText(
                self.tr('Query on all keys'))
            return key_editor

        elif index.column() == 1:
            value_editor = QComboBox(parent)
            value_editor.setEditable(True)
            model = QStringListModel(parent)
            model.setStringList(['1', '2', '3'])
            value_editor.setModel(model)
            value_editor.lineEdit().setPlaceholderText(
                self.tr('Query on all values'))
            return value_editor
