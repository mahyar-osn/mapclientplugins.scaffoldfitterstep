from opencmiss.zinc.context import Context
from opencmiss.zinc.field import Field
from opencmiss.zinc.graphics import Graphics
from opencmiss.zinc.glyph import Glyph
from opencmiss.zinc.material import Material
from opencmiss.zinc.status import OK as ZINC_OK

from opencmiss.utils.zinc import define_standard_visualisation_tools
from opencmiss.utils.zinc import create_finite_element_field

from scaffoldfitter.src.scaffoldfitter.fitter import Fitter


class MasterModel(object):

    def __init__(self, context):
        self._clear_all()

        self._context = context
        self._initialize_region()

        self._ScaffoldFitter = Fitter(self._region)
        self._reset_align_settings()

        self._initialize_surface_material()
        self._initialize_glyph_material()
        self._initialize_tessellation(12)

    def _clear_all(self):
        self._context = None
        self._region = None
        self._materialmodule = None
        self._glyphmodule = None
        self._tessellationmodule = None
        self._location = None
        self._scaffold_model = None
        self._point_cloud = None
        self._model_reference_coordinate_field = None
        self._model_coordinate_field = None
        self._model_centre = None
        self._project_surface_group = None
        self._project_surface_element_group = None
        self._active_data_point_group_field = None
        self._scene = None

    def get_context(self):
        return self._context

    def get_scaffold_model(self):
        return self._scaffold_model

    def get_point_cloud(self):
        return self._point_cloud

    def get_region(self):
        return self._region

    def get_scene(self):
        return self._region.getScene()

    def get_material_module(self):
        return self._materialmodule

    def get_align_scale(self):
        return self._ScaffoldFitter.getAlignScale()

    def get_align_offset(self):
        return self._ScaffoldFitter.getAlignOffset()

    def get_align_euler_angles(self):
        return self._ScaffoldFitter.getAlignEulerAngles()

    # def _get_shareable_open_gl_widget(self):
    #     context = self._model.get_context()
    #     self._shareable_widget = BaseSceneviewerWidget()
    #     self._shareable_widget.set_context(context)
    #
    # def get_shareable_open_gl_widget(self):
    #     return self._shareable_widget

    def initialize_problem(self):
        self._initialize_scaffold_model(reference=True)  # once to generate a model with reference field
        self._initialize_scaffold_model(reference=False)  # again as a target model
        self._initialize_point_cloud()
        self._initialize_model_centre()
        self._initialize_project_surface_group()
        self._initialize_active_data_point()
        self._ScaffoldFitter.applyAlignSettings()
        self._initialize_scene()
        self._show_model_graphics()

    def is_align_mirror(self):
        return self._ScaffoldFitter.isAlignMirror()

    def set_location(self, location):
        self._location = location

    def set_scaffold_model(self, scaffold_model):
        self._scaffold_model = scaffold_model

    def set_point_cloud(self, point_cloud):
        self._point_cloud = point_cloud

    def set_align_settings_change_callback(self, align_settings_change_callback):
        self._ScaffoldFitter.setAlignSettingsChangeCallback(align_settings_change_callback)

    def auto_centre_model_on_data(self):
        self._ScaffoldFitter.autoCentreModelOnData()
        self._model_coordinate_field = self._ScaffoldFitter.setStatePostAlign()
        self._set_model_graphics_post_align()

    def rigid_align(self):
        self._ScaffoldFitter.initializeRigidAlignment()
        self._set_model_graphics_post_align()

    def _create_line_graphics(self):
        lines = self._region.getScene().createGraphicsLines()
        fieldmodule = self._context.getMaterialmodule()
        lines.setCoordinateField(self._model_reference_coordinate_field)
        lines.setName('display_lines')
        black = fieldmodule.findMaterialByName('heart_lines')
        lines.setMaterial(black)
        return lines

    def _create_surface_graphics(self):
        surface = self._scene.createGraphicsSurfaces()
        surface.setCoordinateField(self._model_reference_coordinate_field)
        surface.setRenderPolygonMode(Graphics.RENDER_POLYGON_MODE_SHADED)
        surface_material = self._materialmodule.findMaterialByName('heart_tissue')
        surface.setMaterial(surface_material)
        surface.setName('display_surface')
        # surface.setVisibilityFlag(self.is_display_surface('display_surface'))
        return surface

    def _create_data_point_graphics(self):
        points = self._scene.createGraphicsPoints()
        points.setFieldDomainType(Field.DOMAIN_TYPE_DATAPOINTS)
        points.setCoordinateField(self._data_coordinate_field)
        point_attr = points.getGraphicspointattributes()
        point_attr.setGlyphShapeType(Glyph.SHAPE_TYPE_POINT)
        point_size = self._ScaffoldFitter.getAutoPointSize()
        point_attr.setBaseSize(point_size)
        points.setMaterial(self._materialmodule.findMaterialByName('silver'))

    def _initialize_region(self):
        self._region = self._context.createRegion()

    def _initialize_surface_material(self):
        self._materialmodule = self._context.getMaterialmodule()
        self._materialmodule.beginChange()
        self._materialmodule.defineStandardMaterials()
        # self._shareable_widget = image_context_data.get_shareable_open_gl_widget()

        # default tissue color:
        self._surfaceMaterial = self._materialmodule.createMaterial()
        self._surfaceMaterial.setName('default_surface')
        self._surfaceMaterial.setManaged(True)
        self._surfaceMaterial.setAttributeReal3(Material.ATTRIBUTE_AMBIENT, [0.7, 0.7, 1.0])
        self._surfaceMaterial.setAttributeReal3(Material.ATTRIBUTE_DIFFUSE, [0.7, 0.7, 1.0])
        self._surfaceMaterial.setAttributeReal3(Material.ATTRIBUTE_SPECULAR, [0.5, 0.5, 0.5])
        self._surfaceMaterial.setAttributeReal(Material.ATTRIBUTE_ALPHA, 0.5)
        self._surfaceMaterial.setAttributeReal(Material.ATTRIBUTE_SHININESS, 0.3)

        self._solidTissue = self._materialmodule.createMaterial()
        self._solidTissue.setName('heart_tissue')
        self._solidTissue.setManaged(True)
        self._solidTissue.setAttributeReal3(Material.ATTRIBUTE_AMBIENT, [0.913, 0.541, 0.33])
        self._solidTissue.setAttributeReal3(Material.ATTRIBUTE_EMISSION, [0.0, 0.0, 0.0])
        self._solidTissue.setAttributeReal3(Material.ATTRIBUTE_SPECULAR, [0.2, 0.2, 0.3])
        self._solidTissue.setAttributeReal(Material.ATTRIBUTE_ALPHA, 0.5)
        self._solidTissue.setAttributeReal(Material.ATTRIBUTE_SHININESS, 0.6)

        self._materialmodule.endChange()

    def _initialize_glyph_material(self):
        self._glyphmodule = self._context.getGlyphmodule()
        self._glyphmodule.defineStandardGlyphs()

    def _initialize_tessellation(self, res):
        self._tessellationmodule = self._context.getTessellationmodule()
        self._tessellationmodule = self._tessellationmodule.getDefaultTessellation()
        self._tessellationmodule.setRefinementFactors([res])

    def _initialize_reference_model_coordinate(self):
        self._model_reference_coordinate_field = self._ScaffoldFitter.modelReferenceCoordinateField = self._ScaffoldFitter.getModelCoordinateField()
        name = self._model_reference_coordinate_field.getName()
        number = 0
        number_string = ''
        while True:
            result = self._model_reference_coordinate_field.setName('reference_' + name + number_string)
            if result == ZINC_OK:
                break
            number = number + 1
            number_string = str(number)

    def _initialize_scaffold_model(self, reference=True):
        if reference:
            if self._model_reference_coordinate_field is None:
                result = self._region.readFile(self._scaffold_model)
                if result != ZINC_OK:
                    raise ValueError('Failed to read reference scaffold model')
                self._initialize_reference_model_coordinate()
        else:
            result = self._region.readFile(self._scaffold_model)
            if result != ZINC_OK:
                raise ValueError('Failed to read scaffold model')
            self._model_coordinate_field = self._ScaffoldFitter.modelCoordinateField = self._ScaffoldFitter.getModelCoordinateField()

    def _initialize_point_cloud(self):
        sir = self._region.createStreaminformationRegion()
        point_cloud_resource = sir.createStreamresourceFile(self._point_cloud)
        sir.setResourceDomainTypes(point_cloud_resource, Field.DOMAIN_TYPE_DATAPOINTS)
        result = self._region.read(sir)
        if result != ZINC_OK:
            raise ValueError('Failed to read point cloud')
        self._data_coordinate_field = self._ScaffoldFitter._dataCoordinateField = self._ScaffoldFitter.getDataCoordinateField()

    def _initialize_project_surface_group(self):
        self._project_surface_group, self._project_surface_element_group = self._ScaffoldFitter.getProjectSurfaceGroup()

    def _initialize_model_centre(self):
        self._model_centre = self._ScaffoldFitter.getModelCentre()

    def _initialize_active_data_point(self):
        fm = self._region.getFieldmodule()
        datapoints = fm.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_DATAPOINTS)
        self._active_data_point_group_field = fm.createFieldNodeGroup(datapoints)
        active_data_point_group_field = self._active_data_point_group_field.getNodesetGroup()
        active_data_point_group_field.addNodesConditional(fm.createFieldConstant([1]))

    def _initialize_scene(self):
        self._scene = self._region.getScene()

    def _reset_align_settings(self):
        self._ScaffoldFitter.resetAlignSettings()

    def _show_model_graphics(self):
        self._scene.beginChange()
        self._create_line_graphics()
        self._create_surface_graphics()
        self._create_data_point_graphics()
        self._scene.endChange()

    def _set_model_graphics_post_align(self):
        self._scene.beginChange()
        for name in ['display_lines', 'display_surface']:
            graphics = self._scene.findGraphicsByName(name)
            graphics.setCoordinateField(self._model_coordinate_field)
        self._scene.endChange()
