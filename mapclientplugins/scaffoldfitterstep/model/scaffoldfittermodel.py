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
        self._model_reference_coordinate_field = None

    def get_context(self):
        return self._context

    def get_region(self):
        return self._region

    def get_scene(self):
        return self._region.getScene()

    def get_align_scale(self):
        return self._master_model.get_align_scale()

    def get_align_offset(self):
        return self._master_model.get_align_offset()

    def get_align_euler_angles(self):
        return self._master_model.get_align_euler_angles()

    def is_align_mirror(self):
        return self._master_model.is_align_mirror()

    def align_auto_centre_button_clicked(self):
        self._master_model.auto_centre_model_on_data()

    def reset_clicked(self):
        self._master_model.rigid_align()

    def initialise(self, model, point_cloud):
        self._load_scaffold_model(model)
        self._load_point_cloud(point_cloud)
        self._master_model.initialize_problem()

    def set_align_settings_change_callback(self, align_settings_change_callback):
        self._master_model.set_align_settings_change_callback(align_settings_change_callback)

    def _load_scaffold_model(self, model):
        self._scaffold_model = model
        self._master_model.set_scaffold_model(self._scaffold_model)

    def _load_point_cloud(self, point_cloud):
        self._point_cloud = point_cloud
        self._master_model.set_point_cloud(self._point_cloud)
