from opencmiss.zinc.context import Context

from .scaffoldfittermodel import ScaffoldFitterModel


class MasterModel(object):

    def __init__(self, context):

        self._context = Context(context)
        self._scaffoldFitterModel = ScaffoldFitterModel(self._context)

    def auto_align_model_on_data(self):
        self._scaffoldFitterModel.auto_align_model_on_data()

    def get_context(self):
        return self._context

    def get_scaffold_model(self):
        return self._scaffoldFitterModel

    def get_point_cloud(self):
        return self._scaffoldFitterModel.get_point_cloud()

    def get_region(self):
        return self._scaffoldFitterModel.get_region()

    def get_scene(self):
        return self._scaffoldFitterModel.get_scene()

    def get_material_module(self):
        return self._scaffoldFitterModel.get_material_module()

    def get_align_scale(self):
        return self._scaffoldFitterModel.get_align_scale()

    def get_initial_scale(self):
        self._scaffoldFitterModel.get_initial_scale()

    def get_align_offset(self):
        return self._scaffoldFitterModel.get_align_offset()

    def get_align_euler_angles(self):
        return self._scaffoldFitterModel.get_align_euler_angles()

    def initialise(self, point_cloud, scaffold_path):
        self._scaffoldFitterModel.initialise(point_cloud, scaffold_path)

    def is_align_mirror(self):
        self._scaffoldFitterModel.is_align_mirror()

    def set_align_settings_change_callback(self, align_settings_change_callback):
        self._scaffoldFitterModel.set_align_settings_change_callback(align_settings_change_callback)

    def swap_yz(self):
        self._scaffoldFitterModel.swap_axes(axes='yz')

    def show_axes(self, graphics, show):
        self._scaffoldFitterModel.set_visibility(graphics, show)

    def project_data(self):
        self._scaffoldFitterModel.project_data()

    def fit_scaffold(self):
        self._scaffoldFitterModel.fit_data()
