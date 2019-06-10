from PySide import QtGui, QtCore

from functools import partial

from .ui_scaffoldfitterwidget import Ui_ScaffoldfitterWidget

from opencmiss.zinchandlers.scenemanipulation import SceneManipulation
from opencmiss.zincwidgets.basesceneviewerwidget import BaseSceneviewerWidget

# from scaffoldmaker.scaffoldpackage import ScaffoldPackage


class ScaffoldFitterWidget(QtGui.QWidget):

    def __init__(self, model, scaffold_path, scaffold_name, scaffold_species, scaffold_params, scaffold_object,
                 point_cloud, parent=None):
        super(ScaffoldFitterWidget, self).__init__(parent)
        self._model = model

        self._ui = Ui_ScaffoldfitterWidget()
        self._ui.setupUi(self._get_shareable_open_gl_widget(), self)
        self._setup_handlers()

        self._scaffold_path = scaffold_path
        self._scaffold_name = scaffold_name
        self._scaffold_species = scaffold_species
        self._scaffold_params = scaffold_params
        self._scaffold_object = scaffold_object

        self._point_cloud = point_cloud

        # self._generator_model.registerCustomParametersCallback(self._custom_parameters_change)
        # self._generator_model.registerSceneChangeCallback(self._scene_changed)

        self._scene = None
        self._callback = None
        self._done_callback = None
        self._settings = {'view-parameters': {}}
        self._initialise()

        self._model.set_align_settings_change_callback(self._align_settings_display)
        self._model.get_initial_scale()

        self._ui.sceneviewerWidget.set_context(model.get_context())
        # self._ui.sceneviewerWidget.set_generator_model(self._generator_model)

        # self._refresh_scaffold_type_names()
        # self._refresh_parameter_set_names()
        self._yz = False
        self._make_connections()

    def _make_connections(self):
        # general connections
        self._ui.sceneviewerWidget.graphics_initialized.connect(self._graphics_initialized)
        self._ui.doneButton.clicked.connect(self._done_clicked)
        self._ui.viewAllButton.clicked.connect(self._view_all)

        # scaffold page connections
        self._ui.meshType_label.setText(self._scaffold_name)
        self._ui.parameterSet_label.setText(self._scaffold_species)
        self._ui.displayAnnotationPoints_checkBox.clicked.connect(self._display_annotation_points_clicked)
        self._ui.displayAxes_checkBox.clicked.connect(self._display_axes_clicked)
        self._ui.displayElementAxes_checkBox.clicked.connect(self._display_element_axes_clicked)
        self._ui.displayElementNumbers_checkBox.clicked.connect(self._display_element_numbers_clicked)
        self._ui.displayLines_checkBox.clicked.connect(self._display_lines_clicked)
        self._ui.displayLinesExterior_checkBox.clicked.connect(self._display_lines_exterior_clicked)
        self._ui.displayNodeDerivativeLabelsD1_checkBox.clicked.connect(self._display_node_derivative_labels_d1_clicked)
        self._ui.displayNodeDerivativeLabelsD2_checkBox.clicked.connect(self._display_node_derivative_labels_d2_clicked)
        self._ui.displayNodeDerivativeLabelsD3_checkBox.clicked.connect(self._display_node_derivative_labels_d3_clicked)
        self._ui.displayNodeDerivativeLabelsD12_checkBox.clicked.connect(self._display_node_derivative_labels_d12_clicked)
        self._ui.displayNodeDerivativeLabelsD13_checkBox.clicked.connect(self._display_node_derivative_labels_d13_clicked)
        self._ui.displayNodeDerivativeLabelsD23_checkBox.clicked.connect(self._display_node_derivative_labels_d23_clicked)
        self._ui.displayNodeDerivativeLabelsD123_checkBox.clicked.connect(self._display_node_derivative_labels_d123_clicked)
        self._ui.displayNodeDerivatives_checkBox.clicked.connect(self._display_node_derivatives_clicked)
        self._ui.displayNodeNumbers_checkBox.clicked.connect(self._display_node_numbers_clicked)
        self._ui.displayNodePoints_checkBox.clicked.connect(self._display_node_points_clicked)
        self._ui.displaySurfaces_checkBox.clicked.connect(self._display_surfaces_clicked)
        self._ui.displaySurfacesExterior_checkBox.clicked.connect(self._display_surfaces_exterior_clicked)
        self._ui.displaySurfacesTranslucent_checkBox.clicked.connect(self._display_surfaces_translucent_clicked)
        self._ui.displaySurfacesWireframe_checkBox.clicked.connect(self._display_surfaces_wireframe_clicked)

        # rigid alignment page connections
        self._ui.yz_radioButton.clicked.connect(self._swap_yz_clicked)
        self._ui.alignAutoCentreButton.clicked.connect(self._auto_align_button_clicked)
        self._ui.alignResetButton.clicked.connect(self._reset_clicked)

        # Smooth fitting page connections
        self._ui.projectPointsButton.clicked.connect(self._project_clicked)
        self._ui.fitPerformButton.clicked.connect(self._fit_clicked)

    def _done_clicked(self):
        self._done_callback()

    def _custom_parameters_change(self):
        self._refresh_parameter_set_names()

    def _initialise_parent_region_scaffold(self):
        self._model.initialise_region(self._scaffold_model_parent_region)

    def _initialise(self):
        self._model.initialise(self._point_cloud, self._scaffold_path)
        self._setup_ui()
        self._graphics_initialized()

    def _setup_ui(self):
        self._ui.toolBox.setCurrentIndex(0)
        self._align_settings_display()

    def set_settings(self, settings):
        self._settings.update(settings)

    def _auto_perturb_lines(self):
        sceneviewer = self._ui.sceneviewerWidget.get_zinc_sceneviewer()
        if sceneviewer is not None:
            sceneviewer.setPerturbLinesFlag(self._generator_model.needPerturbLines())

    def _scene_changed(self):
        sceneviewer = self._ui.sceneviewerWidget.get_zinc_sceneviewer()
        if sceneviewer is not None:
            scene = self._model.get_scene()
            # scene = self._model.get_parent_scene()
            self._ui.sceneviewerWidget.set_scene(scene)
            self._auto_perturb_lines()

    def get_settings(self):
        eye, look_at, up, angle = self._ui.sceneviewerWidget.getViewParameters()
        self._settings['view-parameters'] = {'eye': eye, 'look_at': look_at, 'up': up, 'angle': angle}
        return self._settings

    def _graphics_initialized(self):
        scene_viewer = self._ui.sceneviewerWidget.get_zinc_sceneviewer()
        if scene_viewer is not None:
            scene = self._model.get_scene()
            self._refresh_options()
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
                self._view_all()

    def _setup_handlers(self):
        basic_handler = SceneManipulation()
        self._ui.sceneviewerWidget.register_handler(basic_handler)

    def _swap_yz_clicked(self):
        if not self._yz:
            self._model.swap_yz()
            self._yz = True

    def _auto_align_button_clicked(self):
        self._model.auto_align_model_on_data()

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

    # overriding the QWidget method
    def keyPressEvent(self, event):
        if (event.key() == QtCore.Qt.Key_S) and (event.isAutoRepeat() == False):
            self._ui.sceneviewerWidget._selectionKeyPressed = True
            event.setAccepted(True)
        else:
            event.ignore()

    # overriding the QWidget method
    def keyReleaseEvent(self, event):
        if (event.key() == QtCore.Qt.Key_S) and (event.isAutoRepeat() == False):
            self._ui.sceneviewerWidget._selectionKeyPressed = False
            event.setAccepted(True)
        else:
            event.ignore()

    def get_model(self):
        return self._model

    def register_done_execution(self, done_callback):
        self._done_callback = done_callback

    def _update_ui(self):
        pass

    def _done_button_clicked(self):
        # self._ui.dock_widget.setFloating(False)
        self._model.done()
        self._model = None
        self._done_callback()

    def _refresh_scaffold_options(self):
        layout = self._ui.meshTypeOptions_frame.layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        option_names = self._scaffold_params
        for key, value in option_names.items():
            label = QtGui.QLabel(self._ui.meshTypeOptions_frame)
            label.setObjectName(key)
            label.setText(key)
            layout.addWidget(label)
            line_edit = QtGui.QLineEdit(self._ui.meshTypeOptions_frame)
            line_edit.setObjectName(key)
            line_edit.setText(str(value))
            # callback = partial(self._mesh_type_option_line_edit_changed, line_edit)
            # line_edit.returnPressed.connect(callback)
            # line_edit.editingFinished.connect(callback)
            layout.addWidget(line_edit)
            # if type(value) is bool:
            #     check_box = QtGui.QCheckBox(self._ui.meshTypeOptions_frame)
            #     check_box.setObjectName(key)
            #     check_box.setText(key)
            #     check_box.setChecked(value)
            #     callback = partial(self._meshType_option_check_box_clicked, check_box)
            #     check_box.clicked.connect(callback)
            #     layout.addWidget(check_box)
            # else:
            #     label = QtGui.QLabel(self._ui.meshTypeOptions_frame)
            #     label.setObjectName(key)
            #     label.setText(key)
            #     layout.addWidget(label)
            #     if isinstance(value, ScaffoldPackage):
            #         push_button = QtGui.QPushButton()
            #         push_button.setObjectName(key)
            #         push_button.setText('Edit >>')
            #         callback = partial(self._mesh_type_option_scaffold_package_button_pressed, push_button)
            #         push_button.clicked.connect(callback)
            #         layout.addWidget(push_button)
            #     else:
            #         line_edit = QtGui.QLineEdit(self._ui.meshTypeOptions_frame)
            #         line_edit.setObjectName(key)
            #         line_edit.setText(str(value))
            #         callback = partial(self._mesh_type_option_line_edit_changed, line_edit)
            #         #line_edit.returnPressed.connect(callback)
            #         line_edit.editingFinished.connect(callback)
            #         layout.addWidget(line_edit)

    def _refresh_options(self):
        self._refresh_scaffold_options()
        self._ui.doneButton.setEnabled(True)
        self._ui.modifyOptions_frame.setVisible(True)

    def _display_annotation_points_clicked(self):
        self._generator_model.setDisplayAnnotationPoints(self._ui.displayAnnotationPoints_checkBox.isChecked())

    def _display_axes_clicked(self):
        self._model.show_axes('display_axes', self._ui.displayAxes_checkBox.isChecked())

    def _display_element_axes_clicked(self):
        self._generator_model.setDisplayElementAxes(self._ui.displayElementAxes_checkBox.isChecked())

    def _display_element_numbers_clicked(self):
        self._generator_model.setDisplayElementNumbers(self._ui.displayElementNumbers_checkBox.isChecked())

    def _display_lines_clicked(self):
        self._generator_model.setDisplayLines(self._ui.displayLines_checkBox.isChecked())
        self._auto_perturb_lines()

    def _display_lines_exterior_clicked(self):
        self._generator_model.setDisplayLinesExterior(self._ui.displayLinesExterior_checkBox.isChecked())

    def _display_node_derivatives_clicked(self):
        self._generator_model.setDisplayNodeDerivatives(self._ui.displayNodeDerivatives_checkBox.isChecked())

    def _display_node_derivative_labels_d1_clicked(self):
        self._generator_model.setDisplayNodeDerivativeLabels('D1', self._ui.displayNodeDerivativeLabelsD1_checkBox.isChecked())

    def _display_node_derivative_labels_d2_clicked(self):
        self._generator_model.setDisplayNodeDerivativeLabels('D2', self._ui.displayNodeDerivativeLabelsD2_checkBox.isChecked())

    def _display_node_derivative_labels_d3_clicked(self):
        self._generator_model.setDisplayNodeDerivativeLabels('D3', self._ui.displayNodeDerivativeLabelsD3_checkBox.isChecked())

    def _display_node_derivative_labels_d12_clicked(self):
        self._generator_model.setDisplayNodeDerivativeLabels('D12', self._ui.displayNodeDerivativeLabelsD12_checkBox.isChecked())

    def _display_node_derivative_labels_d13_clicked(self):
        self._generator_model.setDisplayNodeDerivativeLabels('D13', self._ui.displayNodeDerivativeLabelsD13_checkBox.isChecked())

    def _display_node_derivative_labels_d23_clicked(self):
        self._generator_model.setDisplayNodeDerivativeLabels('D23', self._ui.displayNodeDerivativeLabelsD23_checkBox.isChecked())

    def _display_node_derivative_labels_d123_clicked(self):
        self._generator_model.setDisplayNodeDerivativeLabels('D123', self._ui.displayNodeDerivativeLabelsD123_checkBox.isChecked())

    def _display_node_numbers_clicked(self):
        self._generator_model.setDisplayNodeNumbers(self._ui.displayNodeNumbers_checkBox.isChecked())

    def _display_node_points_clicked(self):
        self._generator_model.setDisplayNodePoints(self._ui.displayNodePoints_checkBox.isChecked())

    def _display_surfaces_clicked(self):
        self._generator_model.setDisplaySurfaces(self._ui.displaySurfaces_checkBox.isChecked())
        self._auto_perturb_lines()

    def _display_surfaces_exterior_clicked(self):
        self._generator_model.setDisplaySurfacesExterior(self._ui.displaySurfacesExterior_checkBox.isChecked())

    def _display_surfaces_translucent_clicked(self):
        self._generator_model.setDisplaySurfacesTranslucent(self._ui.displaySurfacesTranslucent_checkBox.isChecked())
        self._auto_perturb_lines()

    def _display_surfaces_wireframe_clicked(self):
        self._generator_model.setDisplaySurfacesWireframe(self._ui.displaySurfacesWireframe_checkBox.isChecked())

    @staticmethod
    def _annotation_item_changed(item):
        print(item.text(0))
        print(item.data(0, QtCore.Qt.UserRole + 1))

    def _view_all(self):
        if self._ui.sceneviewerWidget.get_zinc_sceneviewer() is not None:
            self._ui.sceneviewerWidget.view_all()

    def _project_clicked(self):
        self._model.project_data()

    def _fit_clicked(self):
        self._model.fit_scaffold()
