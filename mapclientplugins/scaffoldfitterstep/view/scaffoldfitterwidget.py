from PySide import QtGui, QtCore

from mapclientplugins.scaffoldfitterstep.view.ui_scaffoldfitterwidget import Ui_ScaffoldfitterWidget

from opencmiss.zinchandlers.scenemanipulation import SceneManipulation


class ScaffoldFitterWidget(QtGui.QWidget):

    def __init__(self, model, parent=None):
        super(ScaffoldFitterWidget, self).__init__(parent)
        self._ui = Ui_ScaffoldfitterWidget()
        self._ui.setupUi(model.get_shareable_open_gl_widget(), self)
        self._setup_handlers()

        self._ui.sceneviewerWidget.set_context(model.get_context())

        self._ui.sceneviewerWidget.setContext(model.getContext())
        self._ui.sceneviewerWidget.setModel(model)

        self._model = model

        self._ui.sceneviewerWidget.graphicsInitialized.connect(self._graphicsInitialized)

        self._scene = None
        self._callback = None

        self._settings = {'view-parameters': {}}
        self._done_callback = None

    def _done_clicked(self):
        self._done_callback()

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