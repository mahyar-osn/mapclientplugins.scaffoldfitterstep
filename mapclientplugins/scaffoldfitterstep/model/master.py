from opencmiss.zinc.context import Context

from .scaffoldfittermodel import ScaffoldFitterModel


class MasterModel(object):

    def __init__(self, context):

        # self._context = Context(context)
        self._context = context
        self._scaffoldFitterModel = ScaffoldFitterModel(self._context)

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

    def get_align_offset(self):
        return self._scaffoldFitterModel.get_align_offset()

    def get_align_euler_angles(self):
        return self._scaffoldFitterModel.get_align_euler_angles()

    def initialise(self, point_cloud, region_initialised=True):
        if region_initialised:
            self._scaffoldFitterModel.initialise(point_cloud)
        else:
            self._scaffoldFitterModel.initialise(point_cloud, region_initialised=False)

    def initialise_region(self, region):
        self._scaffoldFitterModel.initialise_region(region)

    def is_align_mirror(self):
        self._scaffoldFitterModel.is_align_mirror()

    def set_align_settings_change_callback(self, align_settings_change_callback):
        self._scaffoldFitterModel.set_align_settings_change_callback(align_settings_change_callback)
