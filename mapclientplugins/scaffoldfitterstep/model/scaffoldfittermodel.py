import sys

from opencmiss.zinc.context import Context
from opencmiss.zinc.glyph import Glyph
from opencmiss.zinc.material import Material
from opencmiss.zinc.status import OK as ZINC_OK

from scaffoldfitter.src.scaffoldfitter.utils.field_utils import createFiniteElementField, getModelCoordinateField, getMesh


class ScaffoldFitterModel(object):
    def __init__(self):
        self._context = Context('scaffoldfit')
        materialmodule = self._context.getMaterialmodule()
        materialmodule.beginChange()
        materialmodule.defineStandardMaterials()
        # self._shareable_widget = image_context_data.get_shareable_open_gl_widget()
        self._surfaceMaterial = materialmodule.createMaterial()
        self._surfaceMaterial.setName('surfacefit')
        self._surfaceMaterial.setAttributeReal3(Material.ATTRIBUTE_AMBIENT, [0.7, 0.7, 1.0])
        self._surfaceMaterial.setAttributeReal3(Material.ATTRIBUTE_DIFFUSE, [0.7, 0.7, 1.0])
        self._surfaceMaterial.setAttributeReal3(Material.ATTRIBUTE_SPECULAR, [0.5, 0.5, 0.5])
        self._surfaceMaterial.setAttributeReal(Material.ATTRIBUTE_ALPHA, 0.5)
        self._surfaceMaterial.setAttributeReal(Material.ATTRIBUTE_SHININESS, 0.3)
        materialmodule.endChange()
        glyphmodule = self._context.getGlyphmodule()
        glyphmodule.defineStandardGlyphs()
        tessellationmodule = self._context.getTessellationmodule()
        defaultTessellation = tessellationmodule.getDefaultTessellation()
        defaultTessellation.setRefinementFactors([12])

        self._modelReferenceCoordinateField = None

    def get_context(self):
        return self._context

    # def _get_shareable_open_gl_widget(self):
    #     context = self._model.get_context()
    #     self._shareable_widget = BaseSceneviewerWidget()
    #     self._shareable_widget.set_context(context)
    #
    # def get_shareable_open_gl_widget(self):
    #     return self._shareable_widget

    def set_location(self, location):
        self._location = location

    def get_region(self):
        return self._region

    def get_scene(self):
        return self._region.getScene()

    def set_zinc_model_file(self, zincModelFile):
        self._zincModelFile = zincModelFile

    def setZincPointCloudFile(self, zincPointCloudFile):
        self._zincPointCloudFile = zincPointCloudFile

    def setPointCloudData(self, pointCloudData):
        self._pointCloudData = pointCloudData

    def initialise(self):
        self._region = self._context.createRegion()
        # self.setStateAlign()
        self._load()

    def _load(self):
        if self._modelReferenceCoordinateField is None:
            result = self._region.readFile(self._zincModelFile)
            if result != ZINC_OK:
                raise ValueError('Failed to read reference model')
            self._modelReferenceCoordinateField = getModelCoordinateField(self._region, self._modelReferenceCoordinateField)
        self._mesh = getMesh(self._region)
        self._show_model_graphics()

    def _show_model_graphics(self):
        scene = self._region.getScene()
        scene.beginChange()
        scene.removeAllGraphics()
        materialmodule = scene.getMaterialmodule()
        axes = scene.createGraphicsPoints()
        pointAttr = axes.getGraphicspointattributes()
        pointAttr.setGlyphShapeType(Glyph.SHAPE_TYPE_AXES_XYZ)
        lines = scene.createGraphicsLines()
        if self._mesh.getDimension() == 3:
            lines.setExterior(True)
        lines.setName('fit-lines')
        surfaces = scene.createGraphicsSurfaces()
        surfaces.setName('fit-surfaces')
        surfaces.setMaterial(self._surfaceMaterial)
        scene.endChange()


