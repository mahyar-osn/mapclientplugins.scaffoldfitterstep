import sys

from opencmiss.zinc.context import Context
from opencmiss.zinc.field import Field, FieldFindMeshLocation
from opencmiss.zinc.glyph import Glyph
from opencmiss.zinc.graphics import Graphics
from opencmiss.zinc.material import Material
from opencmiss.zinc.scenefilter import Scenefilter
from opencmiss.zinc.scenecoordinatesystem import SCENECOORDINATESYSTEM_NORMALISED_WINDOW_FIT_LEFT
from opencmiss.zinc.status import OK as ZINC_OK

from .master import MasterModel


class ScaffoldFitterModel(object):
    def __init__(self):
        self._context = Context('scaffoldfit')

        self._master_model = MasterModel(self._context)
        self._region = self._master_model.get_region()
        self._material_module = self._master_model.get_material_module()

    def _clear_all(self):
        self._scaffold_model = None
        self._point_cloud = None
        self._modelReferenceCoordinateField = None

    def get_context(self):
        return self._context

    def get_region(self):
        return self._region

    def initialise(self, model, point_cloud):
        self._load_scaffold_model(model)
        self._load_point_cloud(point_cloud)
        self._master_model.initialize_problem()

    def set_align_settings_change_callback(self, align_settings_chhange_callback):
        self._master_model.set_align_settings_change_callback(align_settings_chhange_callback)

    def _load_scaffold_model(self, model):
        self._scaffold_model = model
        self._master_model.set_scaffold_model(self._scaffold_model)

    def _load_point_cloud(self, point_cloud):
        self._point_cloud = point_cloud
        self._master_model.set_point_cloud(self._point_cloud)