from PySide import QtGui, QtCore

from functools import partial

from .ui_scaffoldfitterwidget import Ui_ScaffoldfitterWidget

from opencmiss.zinchandlers.scenemanipulation import SceneManipulation
from opencmiss.zincwidgets.basesceneviewerwidget import BaseSceneviewerWidget

from scaffoldmaker.scaffoldpackage import ScaffoldPackage


class ScaffoldFitterWidget(QtGui.QWidget):

    def __init__(self, model, generatormodel, point_cloud, parent=None):
        super(ScaffoldFitterWidget, self).__init__(parent)
        self._model = model
        self._model.set_align_settings_change_callback(self._align_settings_display)

        # self._scaffold_model = scaffold_model
        self._point_cloud = point_cloud

        self._ui = Ui_ScaffoldfitterWidget()
        self._ui.setupUi(self._get_shareable_open_gl_widget(), self)
        self._setup_handlers()

        self._initialise()

        self._generator_model = generatormodel
        self._generator_model.registerCustomParametersCallback(self._custom_parameters_change)
        self._generator_model.registerSceneChangeCallback(self._scene_changed)

        self._ui.sceneviewerWidget.set_context(model.get_context())
        self._ui.sceneviewerWidget.set_generator_model(self._generator_model)
        self._ui.sceneviewerWidget.graphics_initialized.connect(self._graphics_initialized)

        self._refresh_scaffold_type_names()
        self._refresh_parameter_set_names()

        self._makeConnections()

        self._scene = None
        self._callback = None

        self._settings = {'view-parameters': {}}
        self._done_callback = None

    def _makeConnections(self):
        self._ui.doneButton.clicked.connect(self._done_clicked)
        self._ui.viewAllButton.clicked.connect(self._view_all)
        self._ui.meshType_comboBox.currentIndexChanged.connect(self._mesh_type_changed)
        self._ui.alignAutoCentreButton.clicked.connect(self._align_auto_centre_button_clicked)
        self._ui.alignResetButton.clicked.connect(self._reset_clicked)

    def _done_clicked(self):
        self._callback()

    def register_done_execution(self, callback):
        self._callback = callback

    def _custom_parameters_change(self):
        self._refresh_parameter_set_names()

    def _initialise(self):
        self._model.initialise(self._point_cloud)
        self._scene = self._model.get_region().getScene()
        self._setup_ui()
        self._graphics_initialized()

    def _refresh_scaffold_type_names(self):
        self._refresh_combo_box_names(self._ui.meshType_comboBox,
            self._generator_model.getAvailableScaffoldTypeNames(),
            self._generator_model.getEditScaffoldTypeName())

    def _refresh_combo_box_names(self, combo_box, names, current_name):
        combo_box.blockSignals(True)
        combo_box.clear()
        currentIndex = 0
        index = 0
        for name in names:
            combo_box.addItem(name)
            if name == current_name:
                currentIndex = index
            index += 1
        combo_box.setCurrentIndex(currentIndex)
        combo_box.blockSignals(False)

    def _setup_ui(self):
        self._ui.toolBox.setCurrentIndex(0)
        self._align_settings_display()

    def set_settings(self, settings):
        self._settings.update(settings)

    def _autoPerturbLines(self):
        sceneviewer = self._ui.sceneviewerWidget.get_zinc_sceneviewer()
        if sceneviewer is not None:
            sceneviewer.setPerturbLinesFlag(self._generator_model.needPerturbLines())

    def _scene_changed(self):
        sceneviewer = self._ui.sceneviewerWidget.get_zinc_sceneviewer()
        if sceneviewer is not None:
            scene = self._model.get_scene()
            self._ui.sceneviewerWidget.set_scene(scene)
            self._autoPerturbLines()

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

    def _align_auto_centre_button_clicked(self):
        self._model.align_auto_centre_button_clicked()

    def _reset_clicked(self):
        self._model.reset_clicked()

    def _get_shareable_open_gl_widget(self):
        context = self._model.get_context()
        self._shareable_widget = BaseSceneviewerWidget()
        self._shareable_widget.set_context(context)

    def _align_settings_display(self):
        self._display_real(self._ui.alignScaleLineEdit, self._model.get_align_scale())
        self._display_vector(self._ui.alignRotationLineEdit, self._model.get_align_euler_angles())
        self._display_vector(self._ui.alignOffsetLineEdit, self._model.get_align_offset())
        self._ui.alignMirrorCheckBox.setCheckState(
            QtCore.Qt.Checked if self._model.is_align_mirror() else QtCore.Qt.Unchecked)

    def _display_real(self, widget, value):
        new_text = '{:.4g}'.format(value)
        widget.setText(new_text)

    def _display_vector(self, widget, values, number_format = '{:.4g}'):
        new_text = ", ".join(number_format.format(value) for value in values)
        widget.setText(new_text)

    def _mesh_type_changed(self, index):
        mesh_type_name = self._ui.meshType_comboBox.itemText(index)
        self._generator_model.setScaffoldTypeByName(mesh_type_name)
        # self._annotation_model.setMeshTypeByName(mesh_type_name)
        self._refresh_scaffold_options()
        self._refresh_parameter_set_names()

    def _mesh_type_option_line_edit_changed(self, line_edit):
        dependent_changes = self._generator_model.setScaffoldOption(line_edit.objectName(), line_edit.text())
        if dependent_changes:
            self._refresh_scaffold_options()
        else:
            final_value = self._generator_model.getEditScaffoldOption(line_edit.objectName())
            line_edit.setText(str(final_value))

    def _mesh_type_option_check_box_clicked(self, check_box):
        dependent_changes = self._generator_model.setScaffoldOption(check_box.objectName(), check_box.isChecked())
        if dependent_changes:
            self._refresh_scaffold_options()

    def _mesh_type_option_scaffold_package_button_pressed(self, pushButton):
        optionName = pushButton.objectName()
        self._generator_model.editScaffoldPackageOption(optionName)
        # show/hide widgets
        self._ui.doneButton.setEnabled(False)
        self._ui.subscaffold_label.setText(self._generator_model.getEditScaffoldOptionDisplayName())
        self._ui.subscaffold_frame.setVisible(True)
        self._ui.modifyOptions_frame.setVisible(False)
        self._refreshScaffoldTypeNames()
        self._refreshParameterSetNames()
        self._refreshScaffoldOptions()

    def _refresh_scaffold_options(self):
        layout = self._ui.meshTypeOptions_frame.layout()
        # remove all current mesh type widgets
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
              child.widget().deleteLater()
        optionNames = self._generator_model.getEditScaffoldOrderedOptionNames()
        for key in optionNames:
            value = self._generator_model.getEditScaffoldOption(key)
            if type(value) is bool:
                check_box = QtGui.QCheckBox(self._ui.meshTypeOptions_frame)
                check_box.setObjectName(key)
                check_box.setText(key)
                check_box.setChecked(value)
                callback = partial(self._mesh_type_option_check_box_clicked, check_box)
                check_box.clicked.connect(callback)
                layout.addWidget(check_box)
            else:
                label = QtGui.QLabel(self._ui.meshTypeOptions_frame)
                label.setObjectName(key)
                label.setText(key)
                layout.addWidget(label)
                if isinstance(value, ScaffoldPackage):
                    push_button = QtGui.QPushButton()
                    push_button.setObjectName(key)
                    push_button.setText('Edit >>')
                    callback = partial(self._mesh_type_option_scaffold_package_button_pressed, push_button)
                    push_button.clicked.connect(callback)
                    layout.addWidget(push_button)
                else:
                    line_edit = QtGui.QLineEdit(self._ui.meshTypeOptions_frame)
                    line_edit.setObjectName(key)
                    line_edit.setText(str(value))
                    callback = partial(self._mesh_type_option_line_edit_changed, line_edit)
                    line_edit.editingFinished.connect(callback)
                    layout.addWidget(line_edit)

    def _refresh_parameter_set_names(self):
        self._refresh_combo_box_names(self._ui.parameterSet_comboBox,
            self._generator_model.getAvailableParameterSetNames(),
            self._generator_model.getParameterSetName())
