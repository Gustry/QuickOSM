"""Panel OSM base class."""

from json import load
from os.path import isfile

from qgis.PyQt.QtGui import QStandardItemModel
from qgis.PyQt.QtWidgets import QDialogButtonBox, QCompleter

from .base_overpass_panel import BaseOverpassPanel
from ..core.exceptions import OsmObjectsException
from ..core.process import process_quick_query
from ..core.query_factory import QueryFactory
from ..core.utilities.utilities_qgis import open_map_features
from ..definitions.gui import Panels
from ..definitions.osm import QueryType, OsmType
from ..qgis_plugin_tools.i18n import tr
from ..qgis_plugin_tools.resources import resources_path


__copyright__ = 'Copyright 2019, 3Liz'
__license__ = 'GPL version 3'
__email__ = 'info@3liz.org'
__revision__ = '$Format:%H$'


class QuickQueryPanel(BaseOverpassPanel):

    """Final implementation for the panel."""

    def __init__(self, dialog):
        super().__init__(dialog)
        self.panel = Panels.QuickQuery
        self.osm_keys = None
        self.queries_model = None

    def setup_panel(self):
        super().setup_panel()
        """Setup the UI for the QuickQuery."""
        # Query type
        self.dialog.combo_query_type_qq.addItem(tr('In'), 'in')
        self.dialog.combo_query_type_qq.addItem(tr('Around'), 'around')
        self.dialog.combo_query_type_qq.addItem(tr('Canvas Extent'), 'canvas')
        self.dialog.combo_query_type_qq.addItem(tr('Layer Extent'), 'layer')
        self.dialog.combo_query_type_qq.addItem(tr('Not Spatial'), 'attributes')

        # self.cb_query_type_qq.setItemIcon(
        #   0, QIcon(resources_path('in.svg')))
        # self.cb_query_type_qq.setItemIcon(
        #   1, QIcon(resources_path('around.svg')))
        # self.cb_query_type_qq.setItemIcon(
        #   2, QIcon(resources_path('map_canvas.svg')))
        # self.cb_query_type_qq.setItemIcon(
        #   3, QIcon(resources_path('extent.svg')))
        # self.cb_query_type_qq.setItemIcon(
        #   4, QIcon(resources_path('mIconTableLayer.svg')))

        self.dialog.combo_query_type_qq.currentIndexChanged.connect(
            self.query_type_updated)

        self.dialog.line_file_prefix_qq.setDisabled(True)

        self.dialog.button_run_query_qq.clicked.connect(self.run)
        self.dialog.button_show_query.clicked.connect(self.show_query)
        self.dialog.combo_key.editTextChanged.connect(self.key_edited)
        self.dialog.button_map_features.clicked.connect(open_map_features)
        self.dialog.button_box_qq.button(QDialogButtonBox.Reset).clicked.connect(
            self.dialog.reset_form)

        # Setup auto completion
        map_features_json_file = resources_path('json', 'map_features.json')
        if isfile(map_features_json_file):
            with open(map_features_json_file) as f:
                self.osm_keys = load(f)
                keys = list(self.osm_keys.keys())
                keys.append('')  # All keys request #118
                keys.sort()
                keys_completer = QCompleter(keys)
                self.dialog.combo_key.addItems(keys)
                self.dialog.combo_key.setCompleter(keys_completer)
                self.dialog.combo_key.completer().setCompletionMode(
                    QCompleter.PopupCompletion)

        self.dialog.combo_key.lineEdit().setPlaceholderText(
            tr('Query on all keys'))
        self.dialog.combo_value.lineEdit().setPlaceholderText(
            tr('Query on all values'))
        self.key_edited()

        self.query_type_updated()
        self.init_nominatim_autofill()

        self.dialog.table_queries.set_osm_keys(self.osm_keys)
        self.queries_model = QStandardItemModel(self.dialog.table_queries)
        self.queries_model.setColumnCount(2)
        self.queries_model.setRowCount(1)

        headers = [tr('Key'), tr('Value')]
        self.queries_model.setHorizontalHeaderLabels(headers)
        self.dialog.table_queries.setModel(self.queries_model)

    def query_type_updated(self):
        self._core_query_type_updated(
            self.dialog.combo_query_type_qq,
            self.dialog.stacked_query_type,
            self.dialog.spin_place_qq)

    def key_edited(self):
        """Add values to the combobox according to the key."""
        self.dialog.combo_value.clear()
        self.dialog.combo_value.setCompleter(None)

        try:
            current_values = self.osm_keys[self.dialog.combo_key.currentText()]
        except KeyError:
            return
        except AttributeError:
            return

        if len(current_values) == 0:
            current_values.insert(0, '')

        if len(current_values) > 1 and current_values[0] != '':
            current_values.insert(0, '')

        values_completer = QCompleter(current_values)
        self.dialog.combo_value.setCompleter(values_completer)
        self.dialog.combo_value.addItems(current_values)

    def gather_values(self):
        properties = super().gather_values()
        osm_objects = []
        if self.dialog.checkbox_node.isChecked():
            osm_objects.append(OsmType.Node)
        if self.dialog.checkbox_way.isChecked():
            osm_objects.append(OsmType.Way)
        if self.dialog.checkbox_relation.isChecked():
            osm_objects.append(OsmType.Relation)
        properties['osm_objects'] = osm_objects

        if not properties['osm_objects']:
            raise OsmObjectsException

        properties['key'] = self.dialog.combo_key.currentText()
        properties['value'] = self.dialog.combo_value.currentText()
        properties['timeout'] = self.dialog.spin_timeout.value()

        # TODO move?
        properties['distance'] = self.dialog.spin_place_qq.value()
        return properties

    def _run(self):
        """Process for running the query."""
        properties = self.gather_values()
        num_layers = process_quick_query(
            dialog=self.dialog,
            key=properties['key'],
            value=properties['value'],
            area=properties['place'],
            is_around=properties['is_around'],
            distance=properties['distance'],
            bbox=properties['bbox'],
            osm_objects=properties['osm_objects'],
            timeout=properties['timeout'],
            output_directory=properties['output_directory'],
            prefix_file=properties['prefix_file'],
            output_geometry_types=properties['outputs'])
        self.end_query(num_layers)

    def show_query(self):
        """Show the query in the main window."""
        p = self.gather_values()

        # Transfer each output with zip
        check_boxes = zip(
            self.dialog.output_buttons[Panels.QuickQuery],
            self.dialog.output_buttons[Panels.Query])
        for couple in check_boxes:
            couple[1].setChecked(couple[0].isChecked())

        # Transfer the output
        self.dialog.output_directory_q.setFilePath(p['output_directory'])
        if p['prefix_file']:
            self.dialog.line_file_prefix_q.setText(p['prefix_file'])
            self.dialog.line_file_prefix_q.setEnabled(True)

        # TODO
        # Move this logic UP
        # Copy/paste in quick_query_dialog.py
        if p['is_around'] and p['place']:
            query_type = QueryType.AroundArea
        elif not p['is_around'] and p['place']:
            query_type = QueryType.InArea
            distance = None
        elif p['bbox']:
            query_type = QueryType.BBox
        else:
            query_type = QueryType.NotSpatial
        # End todo

        # Make the query
        query_factory = QueryFactory(
            query_type=query_type,
            key=p['key'],
            value=p['value'],
            area=p['place'],
            around_distance=p['distance'],
            osm_objects=p['osm_objects'],
            timeout=p['timeout']
        )
        query = query_factory.make()
        self.dialog.text_query.setPlainText(query)
        self.dialog.stacked_panels_widget.setCurrentIndex(self.dialog.query_index)