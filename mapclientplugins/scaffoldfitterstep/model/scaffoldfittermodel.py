from opencmiss.zinc.field import Field
from opencmiss.zinc.glyph import Glyph
from opencmiss.zinc.graphics import Graphics
from opencmiss.zinc.material import Material
from opencmiss.zinc.status import OK as ZINC_OK

from scaffoldfitter.fitter import Fitter


class ScaffoldFitterModel(object):

    def __init__(self, context):
        self._ScaffoldFitter = None
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

        self._context = context
        self._material_module = self._context.getMaterialmodule()
        self._region = self._context.createRegion()
        self._region.setName('fitter_region')
        self._ScaffoldFitter = Fitter(self._region, self._context)
        self._region_initialised = False

        self._node_derivative_labels = ['D1', 'D2', 'D3', 'D12', 'D13', 'D23', 'D123']
        self._settings = {
            'display_node_points': False,
            'display_node_numbers': False,
            'display_node_derivatives': False,
            'display_node_derivative_labels': self._node_derivative_labels[0:3],
            'display_lines': True,
            'display_lines_post_fit': True,
            'display_lines_exterior': False,
            'display_surfaces': True,
            'display_surfaces_exterior': True,
            'display_surfaces_translucent': False,
            'display_surfaces_wireframe': False,
            'display_element_numbers': False,
            'display_element_axes': False,
            'display_axes': True,
            'display_annotation_points': False
        }

        self._initialise_surface_material()
        self._initialise_glyph_material()
        self._initialise_tessellation(12)

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

    def get_initial_scale(self):
        self._ScaffoldFitter.getInitialDataScale()
        self._ScaffoldFitter.getInitialScale()

    def get_align_offset(self):
        return self._ScaffoldFitter.getAlignOffset()

    def get_align_euler_angles(self):
        return self._ScaffoldFitter.getAlignEulerAngles()

    def _get_visibility(self, graphics_name):
        return self._settings[graphics_name]

    def initialise(self, point_cloud, scaffold_sir):
        self._reset_align_settings()
        self._load_point_cloud(point_cloud)
        self._load_scaffold(scaffold_sir)
        self.initialise_problem()

    def _load_scaffold(self, scaffold):
        self._scaffold_model = scaffold

    def _load_point_cloud(self, point_cloud):
        self._point_cloud = point_cloud

    def initialise_problem(self):
        self._initialise_scaffold_model(reference=True)  # once to generate a model with reference field
        self._initialise_scaffold_model(reference=False)  # again as a target model
        self._initialise_point_cloud()
        self._initialise_active_data_point()
        self._initialise_scene()
        self._show_graphics()

    def is_align_mirror(self):
        return self._ScaffoldFitter.isAlignMirror()

    def set_visibility(self, graphics_name, show):
        self._settings[graphics_name] = show
        graphics = self._region.getScene().findGraphicsByName(graphics_name)
        graphics.setVisibilityFlag(show)

    def set_location(self, location):
        self._location = location

    def set_align_settings_change_callback(self, align_settings_change_callback):
        self._ScaffoldFitter.setAlignSettingsChangeCallback(align_settings_change_callback)

    def auto_align_model_on_data(self):
        self._model_coordinate_field = self._ScaffoldFitter.autoCentreModelOnData()
        # self._ScaffoldFitter.initializeRigidAlignment()
        # self._set_model_graphics_post_align()

    def rigid_align(self):
        _ = self._ScaffoldFitter.initializeRigidAlignment()
        self._model_coordinate_field = self._ScaffoldFitter.setStatePostAlign()

    def _create_line_graphics(self):
        lines = self._region.getScene().createGraphicsLines()
        fieldmodule = self._context.getMaterialmodule()
        lines.setCoordinateField(self._model_reference_coordinate_field)
        lines.setName('display_lines')
        black = fieldmodule.findMaterialByName('white')
        lines.setMaterial(black)
        return lines

    def _create_line_graphics_post_fit(self):
        lines_post_fit = self._region.getScene().createGraphicsLines()
        fieldmodule = self._context.getMaterialmodule()
        lines_post_fit.setCoordinateField(self._model_coordinate_field)
        lines_post_fit.setName('display_lines_post_fit')
        black = fieldmodule.findMaterialByName('orange')
        lines_post_fit.setMaterial(black)
        return lines_post_fit

    def _create_surface_graphics(self):
        surface = self._scene.createGraphicsSurfaces()
        surface.setCoordinateField(self._model_reference_coordinate_field)
        surface.setRenderPolygonMode(Graphics.RENDER_POLYGON_MODE_SHADED)
        surface_material = self._materialmodule.findMaterialByName('trans_blue')
        surface.setMaterial(surface_material)
        surface.setName('display_surfaces')
        return surface

    def _create_surface_graphics_post_fit(self):
        surface_post_fit = self._scene.createGraphicsSurfaces()
        surface_post_fit.setCoordinateField(self._model_coordinate_field)
        surface_post_fit.setRenderPolygonMode(Graphics.RENDER_POLYGON_MODE_SHADED)
        surface_material_post_fit = self._materialmodule.findMaterialByName('heart_tissue_trans_postfit')
        surface_post_fit.setMaterial(surface_material_post_fit)
        surface_post_fit.setName('display_surfaces_post_fit')
        return surface_post_fit

    def _create_surface_trans_graphics(self):
        surface_trans = self._scene.createGraphicsSurfaces()
        surface_trans.setCoordinateField(self._model_reference_coordinate_field)
        surface_trans.setRenderPolygonMode(Graphics.RENDER_POLYGON_MODE_SHADED)
        surface_material = self._materialmodule.findMaterialByName('heart_tissue_trans')
        surface_trans.setMaterial(surface_material)
        surface_trans.setName('display_surfaces_translucent')
        return surface_trans

    def _create_data_point_graphics(self):
        points = self._scene.createGraphicsPoints()
        points.setFieldDomainType(Field.DOMAIN_TYPE_DATAPOINTS)
        points.setCoordinateField(self._data_coordinate_field)
        point_attr = points.getGraphicspointattributes()
        point_attr.setGlyphShapeType(Glyph.SHAPE_TYPE_CROSS)
        point_size = self._ScaffoldFitter.getAutoPointSize()
        point_attr.setBaseSize(point_size)
        points.setMaterial(self._materialmodule.findMaterialByName('silver'))

    def _create_axis_graphics(self):
        axes_scale = [10]*3
        axes = self._scene.createGraphicsPoints()
        pointattr = axes.getGraphicspointattributes()
        pointattr.setGlyphShapeType(Glyph.SHAPE_TYPE_AXES_XYZ)
        # pointattr.setBaseSize([axes_scale, axes_scale, axes_scale])
        pointattr.setBaseSize(axes_scale)
        axes.setMaterial(self._materialmodule.findMaterialByName('red'))
        axes.setName('display_axes')
        axes.setVisibilityFlag(self.is_display_axes())

    @staticmethod
    def _get_node_coordinates_range(coordinates):
        fm = coordinates.getFieldmodule()
        fm.beginChange()
        nodes = fm.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        min_coordinates = fm.createFieldNodesetMinimum(coordinates, nodes)
        max_coordinates = fm.createFieldNodesetMaximum(coordinates, nodes)
        components_count = coordinates.getNumberOfComponents()
        cache = fm.createFieldcache()
        result, min_x = min_coordinates.evaluateReal(cache, components_count)
        result, max_x = max_coordinates.evaluateReal(cache, components_count)
        fm.endChange()
        return min_x, max_x

    def _initialise_surface_material(self):
        self._materialmodule = self._context.getMaterialmodule()
        self._materialmodule.beginChange()
        self._materialmodule.defineStandardMaterials()
        solid_tissue = self._materialmodule.createMaterial()
        solid_tissue.setName('heart_tissue')
        solid_tissue.setManaged(True)
        solid_tissue.setAttributeReal3(Material.ATTRIBUTE_AMBIENT, [0.913, 0.541, 0.33])
        solid_tissue.setAttributeReal3(Material.ATTRIBUTE_EMISSION, [0.0, 0.0, 0.0])
        solid_tissue.setAttributeReal3(Material.ATTRIBUTE_SPECULAR, [0.2, 0.2, 0.3])
        solid_tissue.setAttributeReal(Material.ATTRIBUTE_ALPHA, 1.0)
        solid_tissue.setAttributeReal(Material.ATTRIBUTE_SHININESS, 0.6)

        trans_blue = self._material_module.createMaterial()

        trans_blue.setName('trans_blue')
        trans_blue.setManaged(True)
        trans_blue.setAttributeReal3(Material.ATTRIBUTE_AMBIENT, [0.0, 0.2, 0.6])
        trans_blue.setAttributeReal3(Material.ATTRIBUTE_DIFFUSE, [0.0, 0.7, 1.0])
        trans_blue.setAttributeReal3(Material.ATTRIBUTE_EMISSION, [0.0, 0.0, 0.0])
        trans_blue.setAttributeReal3(Material.ATTRIBUTE_SPECULAR, [0.1, 0.1, 0.1])
        trans_blue.setAttributeReal(Material.ATTRIBUTE_ALPHA, 0.3)
        trans_blue.setAttributeReal(Material.ATTRIBUTE_SHININESS, 0.2)
        glyph_module = self._context.getGlyphmodule()
        glyph_module.defineStandardGlyphs()
        self._materialmodule.endChange()

    def _initialise_glyph_material(self):
        self._glyphmodule = self._context.getGlyphmodule()
        self._glyphmodule.defineStandardGlyphs()

    def _initialise_tessellation(self, res):
        self._tessellationmodule = self._context.getTessellationmodule()
        self._tessellationmodule = self._tessellationmodule.getDefaultTessellation()
        self._tessellationmodule.setRefinementFactors([res])

    def _initialise_scaffold_model(self, reference=True):
        filename = 'D:\\sparc\\fitting\\Shwaber\\model.exf'

        if reference:
            # exnodeFile = filename + '.exnode'
            # exelemFile = filename + '.exelem'
            # result = self._region.readFile(exnodeFile)
            result = self._region.readFile(filename)
            # result = self._region.read(self._scaffold_model)
            if result != ZINC_OK:
                raise ValueError('Failed to initiate reference scaffold')
            self._model_reference_coordinate_field = self._ScaffoldFitter.getModelCoordinateField()
            name = self._model_reference_coordinate_field.getName()
            number = 0
            number_string = ''
            while True:
                result = self._model_reference_coordinate_field.setName('reference_' + name + number_string)
                if result == ZINC_OK:
                    break
                number = number + 1
            self._ScaffoldFitter.setRefereceModelCoordinates(self._model_reference_coordinate_field)
        else:
            # exnodeFile = filename+ '.exnode'
            # exelemFile = filename + '.exelem'
            # result = self._region.readFile(exnodeFile)
            result = self._region.readFile(filename)
            # result = self._region.read(self._scaffold_model)
            if result != ZINC_OK:
                raise ValueError('Failed to initiate model scaffold')
            self._model_coordinate_field = self._ScaffoldFitter.getModelCoordinateField()
            self._ScaffoldFitter.setModelCoordinates(self._model_coordinate_field)

    def _initialise_point_cloud(self):
        filename = 'D:\\sparc\\fitting\\Shwaber\\data.exdata'
        sir = self._region.createStreaminformationRegion()
        # point_cloud_resource = sir.createStreamresourceFile(self._point_cloud)
        point_cloud_resource = sir.createStreamresourceFile(filename)
        sir.setResourceDomainTypes(point_cloud_resource, Field.DOMAIN_TYPE_DATAPOINTS)
        result = self._region.read(sir)
        if result != ZINC_OK:
            raise ValueError('Failed to read point cloud')
        self._data_coordinate_field = self._ScaffoldFitter.getDataCoordinateField()
        self._ScaffoldFitter.setDataCoordinates(self._data_coordinate_field)

    def _initialise_active_data_point(self):
        fm = self._region.getFieldmodule()
        datapoints = fm.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_DATAPOINTS)
        self._active_data_point_group_field = fm.createFieldNodeGroup(datapoints)
        active_data_point_group_field = self._active_data_point_group_field.getNodesetGroup()
        active_data_point_group_field.addNodesConditional(fm.createFieldConstant([1]))

    def _initialise_scene(self):
        self._scene = self._region.getScene()

    def is_display_lines(self):
        return self._get_visibility('display_lines')

    def is_display_axes(self):
        return self._get_visibility('display_axes')

    def is_display_surfaces(self):
        return self._get_visibility('display_surfaces')

    def is_display_surfaces_translucent(self):
        return self._settings['display_surfaces_translucent']

    def _reset_align_settings(self):
        self._ScaffoldFitter.resetAlignSettings()

    def _show_graphics(self):
        self._scene.beginChange()
        self._create_data_point_graphics()
        self._create_line_graphics()
        self._create_surface_graphics()
        self._create_surface_trans_graphics()
        # self._create_axis_graphics()
        self._scene.endChange()

    def _set_model_graphics_post_align(self):
        self._scene.beginChange()
        for name in ['display_lines_post_fit', 'display_surfaces_post_fit']:
            graphics = self._scene.findGraphicsByName(name)
            graphics.setCoordinateField(self._model_coordinate_field)
        self._scene.endChange()

    def _show_post_fit_graphics(self):
        self._scene.beginChange()
        self._create_surface_graphics_post_fit()
        self._create_line_graphics_post_fit()
        self._scene.endChange()

    def _set_explicit_model_graphics(self, field):
        self._scene.beginChange()
        for name in ['display_lines', 'display_surfaces']:
            graphics = self._scene.findGraphicsByName(name)
            graphics.setCoordinateField(field)
        self._scene.endChange()

    def swap_axes(self, axes=None):
        self._ScaffoldFitter.swapAxes(axes=axes)

    def project_data(self):
        self._ScaffoldFitter.computeProjection()

    def fit_data(self):
        self._ScaffoldFitter.fit()
        self._show_post_fit_graphics()

    def perturb_lines(self):
        if self._region is None:
            return False
        mesh2d = self._region.getFieldmodule().findMeshByDimension(2)
        if mesh2d.getSize() == 0:
            return False
        return self.is_display_lines() and self.is_display_surfaces() and not self.is_display_surfaces_translucent()
