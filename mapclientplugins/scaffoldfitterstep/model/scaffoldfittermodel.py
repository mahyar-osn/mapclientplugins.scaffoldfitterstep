from opencmiss.zinc.context import Context
from opencmiss.zinc.field import Field, FieldFindMeshLocation
from opencmiss.zinc.glyph import Glyph
from opencmiss.zinc.graphics import Graphics
from opencmiss.zinc.material import Material
from opencmiss.zinc.scenefilter import Scenefilter
from opencmiss.zinc.scenecoordinatesystem import SCENECOORDINATESYSTEM_NORMALISED_WINDOW_FIT_LEFT
from opencmiss.zinc.status import OK as ZINC_OK


class ScaffoldFitterModel(object):
    def __init__(self):
        self._context = Context('scaffoldfit')
        materialmodule = self._context.getMaterialmodule()
        materialmodule.beginChange()
        materialmodule.defineStandardMaterials()
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

    def getContext(self):
        return self._context

    def setLocation(self, location):
        self._location = location

    def getRegion(self):
        return self._region

    def setZincModelFile(self, zincModelFile):
        self._zincModelFile = zincModelFile

    def setZincPointCloudFile(self, zincPointCloudFile):
        self._zincPointCloudFile = zincPointCloudFile

    def setPointCloudData(self, pointCloudData):
        self._pointCloudData = pointCloudData

    def initialise(self):
        self._region = self._context.createRegion()
        self.setStateAlign()
