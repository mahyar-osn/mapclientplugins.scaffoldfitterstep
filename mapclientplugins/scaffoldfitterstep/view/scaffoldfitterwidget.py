from PySide import QtGui, QtCore

from mapclientplugins.scaffoldfitterstep.view.ui_scaffoldfitterwidget import Ui_ScaffoldfitterWidget

from opencmiss.zinchandlers.scenemanipulation import SceneManipulation
from opencmiss.zincwidgets.basesceneviewerwidget import BaseSceneviewerWidget

# from scaffoldmaker.scaffolds import Scaffolds

# from scaffoldfitter.src.scaffoldfitter.fitter import Fitter


class ScaffoldFitterWidget(QtGui.QWidget):

    def __init__(self, model, parent=None):
        super(ScaffoldFitterWidget, self).__init__(parent)
        self._model = model
        self._model.set_align_settings_change_callback(self._align_settings_display)

        self._ui = Ui_ScaffoldfitterWidget()
        self._ui.setupUi(self._get_shareable_open_gl_widget(), self)
        self._setup_handlers()

        self._ui.sceneviewerWidget.set_context(model.get_context())

        # self._ui.sceneviewerWidget.setModel(model)

        self._ui.sceneviewerWidget.graphics_initialized.connect(self._graphics_initialized)

        self._scene = None
        self._callback = None

        self._settings = {'view-parameters': {}}
        self._done_callback = None

    def _done_clicked(self):
        self._done_callback()

    def register_done_execution(self, callback):
        self._callback = callback

    def initialise(self):
        self._model.initialise()
        self._scene = self._model.get_region().getScene()
        self._setup_ui()
        self._graphics_initialized()

    def _setup_ui(self):
        self._ui.toolBox.setCurrentIndex(0)
        self._align_settings_display()

    def set_settings(self, settings):
        self._settings.update(settings)

    def get_settings(self):
        eye, look_at, up, angle = self._ui.sceneviewerWidget.getViewParameters()
        self._settings['view-parameters'] = {'eye': eye, 'look_at': look_at, 'up': up, 'angle': angle}
        return self._settings

    def _graphics_initialized(self):
        scene_viewer = self._ui.sceneviewerWidget.get_zinc_sceneviewer()
        if scene_viewer is not None:
            scene = self._model.get_scene()
            # self._ui.sceneviewerWidget.set_tumble_rate(0)  # For 2D viewing only i.e. no rotation.
            self._ui.sceneviewerWidget.set_scene(scene)
            if len(self._settings['view-parameters']) == 0:
                self._view_all()
            else:
                eye = self._settings['view-parameters']['eye']
                look_at = self._settings['view-parameters']['look_at']
                up = self._settings['view-parameters']['up']
                angle = self._settings['view-parameters']['angle']
                self._ui.sceneviewerWidget.set_view_parameters(eye, look_at, up, angle)

    def _view_all(self):
        if self._ui.sceneviewerWidget.get_zinc_sceneviewer() is not None:
            self._ui.sceneviewerWidget.view_all()

    def register_done_callback(self, done_callback):
        self._done_callback = done_callback

    def _setup_handlers(self):
        basic_handler = SceneManipulation()
        self._ui.sceneviewerWidget.register_handler(basic_handler)

    def _get_shareable_open_gl_widget(self):
        context = self._model.get_context()
        self._shareable_widget = BaseSceneviewerWidget()
        self._shareable_widget.set_context(context)

    def _align_settings_display(self):
        self._displayReal(self._ui.alignScaleLineEdit, self._model.getAlignScale())
        self._displayVector(self._ui.alignRotationLineEdit, self._model.getAlignEulerAngles())
        self._displayVector(self._ui.alignOffsetLineEdit, self._model.getAlignOffset())
        self._ui.alignMirrorCheckBox.setCheckState(
            QtCore.Qt.Checked if self._model.isAlignMirror() else QtCore.Qt.Unchecked)
