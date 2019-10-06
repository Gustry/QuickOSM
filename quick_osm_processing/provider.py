"""Processing QuickOSM provider."""

__author__ = 'Etienne Trimaille'
__date__ = '2017-11-11'
__copyright__ = '(C) 2017 by Etienne Trimaille'


from qgis.PyQt.QtGui import QIcon

from qgis.core import QgsProcessingProvider

from QuickOSM.quick_osm_processing.advanced.build_query import (
    BuildQueryInAreaAlgorithm,
    BuildQueryAroundAreaAlgorithm,
    BuildQueryExtentAlgorithm,
    BuildQueryNotSpatialAlgorithm,
)
# from QuickOSM.quick_osm_processing.advanced.download_overpass import (
#   DownloadOverpassUrl)
from QuickOSM.quick_osm_processing.advanced.open_osm_file import OpenOsmFile
from QuickOSM.quick_osm_processing.advanced.raw_query import RawQueryAlgorithm
from QuickOSM.qgis_plugin_tools.resources import resources_path

__copyright__ = 'Copyright 2019, 3Liz'
__license__ = 'GPL version 3'
__email__ = 'info@3liz.org'
__revision__ = '$Format:%H$'


class Provider(QgsProcessingProvider):

    def id(self, *args, **kwargs):
        return 'quickosm'

    def name(self, *args, **kwargs):
        return 'QuickOSM'

    def icon(self):
        return QIcon(resources_path('icons', 'QuickOSM.svg'))

    def svgIconPath(self):
        return resources_path('icons', 'QuickOSM.svg')

    def loadAlgorithms(self, *args, **kwargs):
        self.addAlgorithm(BuildQueryInAreaAlgorithm())
        self.addAlgorithm(BuildQueryAroundAreaAlgorithm())
        self.addAlgorithm(BuildQueryExtentAlgorithm())
        self.addAlgorithm(BuildQueryNotSpatialAlgorithm())
        self.addAlgorithm(RawQueryAlgorithm())
        # self.addAlgorithm(DownloadOverpassUrl())
        self.addAlgorithm(OpenOsmFile())
