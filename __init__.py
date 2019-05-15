bl_info = {
    "name": "Curve Builder",
    "description": "Diplom project",
    "author": "Akeyn",
    "version": (0, 0, 2),
    "blender": (2, 70, 0),
    "location": "3D View > Tools",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Development"
}

import os
import bpy
import shutil
import logging
import logging.config
import inspect
import yaml

from bpy.props import (StringProperty,
                       CollectionProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy_extras.io_utils import ExportHelper
from bpy.types import (Panel,
                       Operator,
                       OperatorFileListElement,
                       PropertyGroup,
                       )

#logging.config.fileConfig('logging.conf')

# ------------------------------------------------------------------------
#    Localization (custom translations)
# ------------------------------------------------------------------------

translation_dict = {
    "en_US" :
        {
            ("*", "Slam Algorithm") : "Slam Algorithm",
            ("*", "Apply Algorithm to attribute.") : "Apply Algorithm to attribute.",
            ("*", "Video File Path") : "Video File Path",
            ("*", "Output Folder Path") : "Output Folder Path",
            ("*", "Build Algorithm") : "Build Algorithm",
            ("*", "Import Settings") : "Import Settings",
            ("*", "Export Settings") : "Export Settings",
            ("*", "Apply Settings") : "Apply Settings",
            ("*", "Convert Video To Sequence") : "Convert Video To Sequence",
            ("*", "Processing Video Sequence") : "Processing Video Sequence",
            ("*", "Convert Points To Curve") : "Convert Points To Curve",
            ("*", "Add Virtual Camera") : "Add Virtual Camera",
            ("*", "Create Camera Animation") : "Create Camera Animation",
            ("*", "Curve Builder") : "Curve Builder",
            ("*", "Motion Capture") : "Motion Capture",
            ("*", "Select Algorithm") : "Select Algorithm",
            ("*", "Camera Settings") : "Camera Settings",
            ("*", "Camera frames per second") : "Camera frames per second",
            ("*", "Color order of the images") : "Color order of the images",
            ("*", "Number of features per image") : "Number of features per image",
            ("*", "Scale factor between levels in the scale pyramid") : "Scale factor between levels in the scale pyramid",
            ("*", "Number of levels in the scale pyramid") : "Number of levels in the scale pyramid",
            ("*", "Fast threshold") : "Fast threshold",
            ("*", "Viewer Parameters") : "Viewer Parameters",
        },
    "uk_UA" :
        {
            ("*", "Slam Algorithm") : "Slam Алгоритм",
            ("*", "Apply Algorithm to attribute.") : "Застосувати алгоритм до атрибута.",
            ("*", "Video File Path") : "Шлях до відеофайлу",
            ("*", "Output Folder Path") : "Шлях до папки виводу",
            ("*", "Build Algorithm") : "Зібрати Алгоритм",
            ("*", "Import Settings") : "Імпортувати налаштування",
            ("*", "Export Settings") : "Експортувати налаштування",
            ("*", "Apply Settings") : "Застосувати  налаштування",
            ("*", "Convert Video To Sequence") : "Перетворення відео у послідовність",
            ("*", "Processing Video Sequence") : "Обробка послідовності відео",
            ("*", "Convert Points To Curve") : "Перетворити точки у криву",
            ("*", "Add Virtual Camera") : "Додати віртуальну камеру",
            ("*", "Create Camera Animation") : "Створити анімацію камери",
            ("*", "Curve Builder") : "Будівельник кривої",
            ("*", "Motion Capture") : "Захоплення руху",
            ("*", "Select Algorithm") : "Виберіть Алгоритм",
            ("*", "Camera Settings") : "Налаштування камери",
            ("*", "Camera frames per second") : "Кадри камери у секунду",
            ("*", "Color order of the images") : "Порядок кольорів у зображень",
            ("*", "Number of features per image") : "Кількість точок на одне зображення",
            ("*", "Scale factor between levels in the scale pyramid") : "Коефіцієнт масштабування між рівнями у масштабі піраміди",
            ("*", "Number of levels in the scale pyramid") : "Кількість рівнів у масштабі піраміди",
            ("*", "Fast threshold") : "Швидкий поріг",
            ("*", "Viewer Parameters") : "Параметри перегляду",
        }
}

# ------------------------------------------------------------------------
#    Scene Properties (custom fields)
# ------------------------------------------------------------------------

class CurveBuilderFields(PropertyGroup):

    slam_algorithm = EnumProperty(
        name="Slam Algorithm",
        description="Apply Algorithm to attribute.",
        items=[ ('ORB_SLAM2', "ORB SLAM", ""),
                #('dir_name', "alg_name", ""),
               ],
        default=None,
        update=None,
        get=None,
        set=None
        )

    video_file_path = StringProperty(
        name="Video File Path",
        description=":",
        default="",
        maxlen=1024,
        subtype='FILE_PATH',
        )

    output_folder_path = StringProperty(
        name="Output Folder Path",
        description=":",
        default="/tmp",
        maxlen=1024,
        subtype='DIR_PATH',
        )

    #--------------------------------------------------------------------------------------------
    # Camera Parameters. Adjust them!
    #--------------------------------------------------------------------------------------------
    # Camera calibration and distortion parameters (OpenCV)
    camera_fx = FloatProperty(
        name="Camera.fx",
        description=":",
        default=724.6891736,
        )
    camera_fy = FloatProperty(
        name="Camera.fy",
        description=":",
        default=726.65674145,
        )

    camera_cx = FloatProperty(
        name="Camera.cx",
        description=":",
        default=303.71051608,
        )
    camera_cy = FloatProperty(
        name="Camera.cy",
        description=":",
        default=204.18022629,
        )

    camera_k1 = FloatProperty(
        name="Camera.k1",
        description=":",
        default=0.10975062,
        )
    camera_k2 = FloatProperty(
        name="Camera.k2",
        description=":",
        default=0.75393683,
        )

    camera_p1 = FloatProperty(
        name="Camera.p1",
        description=":",
        default=-0.019259,
        )
    camera_p2 = FloatProperty(
        name="Camera.p2",
        description=":",
        default=-0.00708093,
        )

    camera_k3 = FloatProperty(
        name="Camera.k3",
        description=":",
        default=-5.05405739,
        )
    # Camera frames per second
    camera_fps = IntProperty(
        name="Camera.fps",
        description=":",
        default=20,
        max=30
        )
    # Color order of the images (0: BGR, 1: RGB. It is ignored if images are grayscale)
    camera_RGB = IntProperty(
        name="Camera.RGB",
        description=":",
        default=1,
        max=1,
        min=0
        )
    # ORB Extractor: Number of features per image
    ORBextractor_nFeatures = IntProperty(
        name="ORBextractor.nFeatures",
        description=":",
        default=1000,
        )
    # ORB Extractor: Scale factor between levels in the scale pyramid
    ORBextractor_scaleFactor = FloatProperty(
        name="ORBextractor.scaleFactor",
        description=":",
        default=1.2,
        )
    # ORB Extractor: Number of levels in the scale pyramid
    ORBextractor_nLevels = IntProperty(
        name="ORBextractor.nLevels",
        description=":",
        default=8,
        )
    # ORB Extractor: Fast threshold
    # Image is divided in a grid. At each cell FAST are extracted imposing a minimum response.
    # Firstly we impose iniThFAST. If no corners are detected we impose a lower value minThFAST
    # You can lower these values if your images have low contrast
    ORBextractor_iniThFAST = IntProperty(
        name="ORBextractor.iniThFAST",
        description=":",
        default=20,
        )
    ORBextractor_minThFAST = IntProperty(
        name="ORBextractor.minThFAST",
        description=":",
        default=7,
        )
    #--------------------------------------------------------------------------------------------
    # Viewer Parameters
    #--------------------------------------------------------------------------------------------
    viewer_KeyFrameSize = FloatProperty(
        name="Viewer.KeyFrameSize",
        description=":",
        default=0.05,
        )
    viewer_KeyFrameLineWidth = IntProperty(
        name="Viewer.KeyFrameLineWidth",
        description=":",
        default=1,
        )
    viewer_GraphLineWidth = FloatProperty(
        name="Viewer.GraphLineWidth",
        description=":",
        default=0.9,
        )
    viewer_PointSize = IntProperty(
        name="Viewer.PointSize",
        description=":",
        default=2,
        )
    viewer_CameraSize = FloatProperty(
        name="Viewer.CameraSize",
        description=":",
        default=0.08,
        )
    viewer_CameraLineWidth = IntProperty(
        name="Viewer.CameraLineWidth",
        description=":",
        default=3,
        )
    viewer_ViewpointX = FloatProperty(
        name="Viewer.ViewpointX",
        description=":",
        default=0,
        )
    viewer_ViewpointY = FloatProperty(
        name="Viewer.ViewpointY",
        description=":",
        default=-0.7,
        )
    viewer_ViewpointZ = FloatProperty(
        name="Viewer.ViewpointZ",
        description=":",
        default=-1.8,
        )
    viewer_ViewpointF = IntProperty(
        name="Viewer.ViewpointF",
        description=":",
        default=500,
        )

# ------------------------------------------------------------------------
#    Operators (custom functions)
# ------------------------------------------------------------------------

class WM_OT_build_algorithm(bpy.types.Operator):
    bl_idname = "wm.build_algorithm"
    bl_label = "Build Algorithm"

    def execute(self, context):
        slam_folder_path = get_slam_folder_path()
        bash = 'build.sh'

        path_to_bash = os.path.join(slam_folder_path, bash)
        os.system("chmod 777 {0}".format(path_to_bash))

        os.system("cd {0}; ./{1}".format(slam_folder_path, bash)) 
		#os.system("cd /home/asterios/Akeyn/VideoTo3DCurve/ORB_SLAM2; ./build.sh")
        return {'FINISHED'}

class WM_OT_import_settings(bpy.types.Operator, ExportHelper):
    bl_idname = "wm.import_settings"
    bl_label = "Import Settings"


    files = CollectionProperty(
            name="File Path",
            type=OperatorFileListElement,
            )
    directory = StringProperty(
            subtype='DIR_PATH',
            )
    
    filename_ext = ""

    def execute(self, context):        
        directory = self.directory
        for file_elem in self.files:
            filepath = os.path.join(directory, file_elem.name)

        repair_yaml_file(filepath)

        skip_lines = 2
        with open(filepath) as infile:
            for i in range(skip_lines):
                _ = infile.readline()
            data = yaml.safe_load(infile)

        print(data)

        field_names = get_field_names()
        for variable_name in field_names:
            attribute_name = field_names.get(variable_name)

            attribute = data.get(attribute_name)
            if attribute or attribute == 0:
                setattr(bpy.context.scene.curve_builder_fields, variable_name, attribute)

        return {'FINISHED'}

class WM_OT_export_settings(bpy.types.Operator, ExportHelper):
    bl_idname = "wm.export_settings"
    bl_label = "Export Settings"


    files = CollectionProperty(
            name="File Path",
            type=OperatorFileListElement,
            )
    directory = StringProperty(
            subtype='DIR_PATH',
            )
    
    filename_ext = ""

    def execute(self, context):
        directory = self.directory
        for file_elem in self.files:
            setting_path = os.path.join(directory, file_elem.name)

        setting_doc = {}
        write_settings_file(setting_doc, setting_path)

        return {'FINISHED'}

class WM_OT_apply_settings(bpy.types.Operator):
    bl_idname = "wm.apply_settings"
    bl_label = "Apply Settings"

    def execute(self, context):

        slam_folder_path = get_slam_folder_path()
        setting_path = os.path.join(slam_folder_path, "Examples/Monocular/sam.yaml")        # refactor set as setting variable (camera settings)

        repair_yaml_file(setting_path)

        skip_lines = 2
        with open(setting_path) as infile:
            for i in range(skip_lines):
                _ = infile.readline()
            setting_doc = yaml.safe_load(infile)

        write_settings_file(setting_doc, setting_path)

        return {'FINISHED'}

#class WM_OT_load_video(bpy.types.Operator, ExportHelper):  # Create base class (name = wm.get_filepath)
#    bl_idname = "wm.load_video"
#    bl_label = "Load video file"
#    files = CollectionProperty(
#            name="File Path",
#            type=OperatorFileListElement,
#            )
#    directory = StringProperty(
#            subtype='DIR_PATH',
#            )
#
#    filename_ext = ""
#
#    def execute(self, context):        
#        directory = self.directory
#        for file_elem in self.files:
#            filepath = os.path.join(directory, file_elem.name)
#
#        bpy.context.scene.curve_builder_fields.video_file_path = filepath
#        return {'FINISHED'}

class WM_OT_convert_video_to_sequence(bpy.types.Operator):
    bl_idname = "wm.convert_video"
    bl_label = "Convert Video To Sequence"

    def execute(self, context):  # in tmp
        tmp = bpy.context.scene.curve_builder_fields.output_folder_path
        video_file_path = bpy.context.scene.curve_builder_fields.video_file_path
        video_file_name = os.path.splitext(os.path.basename(bpy.context.scene.curve_builder_fields.video_file_path))[0]
        out_folder = os.path.join(tmp, video_file_name)

        if os.path.basename(tmp) == video_file_name:
            return {'FINISHED'}
            
        bpy.context.scene.curve_builder_fields.output_folder_path = out_folder

        if os.path.exists(out_folder):
            shutil.rmtree(out_folder, ignore_errors=True)

        os.makedirs(out_folder)
        
        video_to_points = "video_to_points.sh"
        script_folder_path = get_script_folder_path()
        path_to_bash = os.path.join(script_folder_path, video_to_points)

        os.system("chmod 777 {0}".format(path_to_bash))

        # TODO get current python file path
        fps = 20  # fps like in the sam.yaml settings (20 or 30)
        rotchoice = 'n'  # rotation(yes or no)
        os.system("{0} {1} {2} {3} {4}".format(path_to_bash, video_file_path, out_folder, fps, rotchoice))
        
        return {'FINISHED'}

class WM_OT_processing_video_sequence(bpy.types.Operator):
    bl_idname = "wm.processing_video_sequence"
    bl_label = bpy.app.translations.pgettext("Processing Video Sequence")

    def execute(self, context):
        # TODO /home/asterios/Akeyn/VideoTo3DCurve/ORB_SLAM2/ - create method for getting current folder path
        slam_folder_path = get_slam_folder_path()


        mono_rcs = os.path.join(slam_folder_path, "Examples/Monocular/mono_rcs")   # mono_rcs.cc (Save camera trajectory "KeyFrameTrajectory.txt")
                                                                                # mono_rcs - have to build by bash "/home/asterios/Akeyn/VideoTo3DCurve/ORB_SLAM2/build.sh" (If it was edit)
        
        ORBvoc = os.path.join(slam_folder_path, "Vocabulary/ORBvoc.txt")           # refactor set as CONST (vocabulary)
        sam = os.path.join(slam_folder_path, "Examples/Monocular/sam.yaml")        # refactor set as setting variable (camera settings)
        out_folder = bpy.context.scene.curve_builder_fields.output_folder_path
        os.system("{0} {1} {2} {3}".format(mono_rcs, ORBvoc, sam, out_folder))
        return {'FINISHED'}

class WM_OT_convert_points_to_curve(bpy.types.Operator):
    bl_idname = "wm.convert_points_to_curve"
    bl_label = bpy.app.translations.pgettext("Convert Points To Curve")

    def execute(self, context):
        out_folder = bpy.context.scene.curve_builder_fields.output_folder_path
        key_frame_trajectory = os.path.join(out_folder,'KeyFrameTrajectory.txt')

        verts = []
        with open(key_frame_trajectory) as file:
            for line in file:
                vector = map(lambda a: float(a), line.split(' ')[1:4])
                verts.append(vector)

        verts_count = len(verts)
        edges = []
        for i in range(verts_count):
            if i+1 != verts_count:
                connection = [i, i+1]
                edges.append(connection)

        faces = []

        mesh_data = bpy.data.meshes.new("trajectory_cam_mesh")
        mesh_data.from_pydata(verts, edges, faces)
        mesh_data.update()

        obj = bpy.data.objects.new("Trajectory_Object", mesh_data)

        scene = bpy.context.scene
        scene.objects.link(obj)
        obj.select = True
        
        scene.objects.active = obj  # make the selection effective
        bpy.ops.object.convert(target='CURVE') # convert selected object to curve

        bpy.ops.transform.resize(value=(5, 5, 5), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.curve.spline_type_set(type='NURBS')
        bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}

class WM_OT_add_virtual_camera(bpy.types.Operator):
    bl_idname = "wm.add_virtual_camera"
    bl_label = bpy.app.translations.pgettext("Add Virtual Camera")

    def execute(self, context):
        bpy.ops.object.camera_add(
            view_align=True,
            enter_editmode=False,
            location=(0, 0, 0),
            rotation=(0, 0, 0),
            layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False)
        )
        return {'FINISHED'}

class WM_OT_create_camera_animation(bpy.types.Operator):
    bl_idname = "wm.create_camera_animation"
    bl_label = bpy.app.translations.pgettext("Create Camera Animation")

    def execute(self, context):
        out_folder = bpy.context.scene.curve_builder_fields.output_folder_path
        key_frame_trajectory = os.path.join(out_folder,'KeyFrameTrajectory.txt')

        obj = bpy.data.objects[bpy.context.object.name]
        obj.rotation_mode = 'QUATERNION'
        i = 0
        with open(key_frame_trajectory) as file:
            for line in file:
                vector = list(map(lambda a: float(a), line.split(' ')[1:]))
                obj.rotation_quaternion = (vector[6] * 5, vector[3] * 5, vector[4] * 5, vector[5] * 5)  # w, x, y, z
                obj.location = (vector[0] * 5, vector[1] * 5, vector[2] * 5)  # x, y, z
                bpy.context.scene.frame_current = i
                bpy.ops.anim.keyframe_insert_menu(type='BUILTIN_KSI_LocRot')
                i += 1

        bpy.context.scene.frame_current = 0


        return {'FINISHED'}

# ------------------------------------------------------------------------
#    Panel in Object Mode (custom groups)
# ------------------------------------------------------------------------

class CurveBuilder_CustomPanel(Panel):
    """Curve Builder Script"""
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label = bpy.app.translations.pgettext("Curve Builder")
    bl_context = "objectmode"
    bl_category = bpy.app.translations.pgettext("Motion Capture")
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        field = scene.curve_builder_fields

        layout.label(bpy.app.translations.pgettext("Select Algorithm"))

        algorithm_box = layout.box()
        algorithm_col = algorithm_box.column()
        algorithm_col.prop(field, "slam_algorithm") 
        algorithm_col.operator("wm.build_algorithm", text=bpy.app.translations.pgettext("Build Algorithm"))
        #---------------------------------------------------------------
        layout.label(bpy.app.translations.pgettext("Camera Settings"))

        settings_box = layout.box()
        settings_col = settings_box.column()

        settings_action_row = settings_col.row()
        settings_action_row.operator("wm.import_settings", text=bpy.app.translations.pgettext("Import Settings"))
        settings_action_row.operator("wm.export_settings", text=bpy.app.translations.pgettext("Export Settings"))
        settings_action_row.operator("wm.apply_settings", text=bpy.app.translations.pgettext("Apply Settings"))

        settings_col.separator()
        settings_col = settings_col.column()
        
        settings_row1 = settings_col.row()
        settings_row1.prop(field, "camera_fx")
        settings_row1.prop(field, "camera_fy")
        
        settings_row2 = settings_col.row()
        settings_row2.prop(field, "camera_cx")
        settings_row2.prop(field, "camera_cy")
        
        settings_row3 = settings_col.row()
        settings_row3.prop(field, "camera_k1")
        settings_row3.prop(field, "camera_k2")

        settings_row4 = settings_col.row()
        settings_row4.prop(field, "camera_p1")
        settings_row4.prop(field, "camera_p2")

        settings_col.prop(field, "camera_k3")
        
        settings_row5 = settings_col.row()
        camera_fps_col = settings_row5.column()
        camera_fps_col.label(bpy.app.translations.pgettext("Camera frames per second"))
        camera_fps_col.prop(field, "camera_fps")
        
        camera_RGB_col = settings_row5.column()
        camera_RGB_col.label(bpy.app.translations.pgettext("Color order of the images"))
        camera_RGB_col.prop(field, "camera_RGB")

        ORBextractor_nFeatures_col = settings_row5.column()
        ORBextractor_nFeatures_col.label(bpy.app.translations.pgettext("Number of features per image"))
        ORBextractor_nFeatures_col.prop(field, "ORBextractor_nFeatures")
        
        settings_row6 = settings_col.row()
        ORBextractor_scaleFactor_col = settings_row6.column()
        ORBextractor_scaleFactor_col.label(bpy.app.translations.pgettext("Scale factor between levels in the scale pyramid"))
        ORBextractor_scaleFactor_col.prop(field, "ORBextractor_scaleFactor")

        ORBextractor_nLevels_col = settings_row6.column()
        ORBextractor_nLevels_col.label(bpy.app.translations.pgettext("Number of levels in the scale pyramid"))
        ORBextractor_nLevels_col.prop(field, "ORBextractor_nLevels")
        
        fast_threshold_col = settings_col.column()
        fast_threshold_col.label(bpy.app.translations.pgettext("Fast threshold"))
        settings_row7 = fast_threshold_col.row()
        settings_row7.prop(field, "ORBextractor_iniThFAST")
        settings_row7.prop(field, "ORBextractor_minThFAST")
        
        viewer_parameters_col = settings_col.column()
        viewer_parameters_col.label(bpy.app.translations.pgettext("Viewer Parameters"))
        settings_row8 = viewer_parameters_col.row()
        settings_row8.prop(field, "viewer_KeyFrameSize")
        settings_row8.prop(field, "viewer_KeyFrameLineWidth")
        
        settings_row9 = viewer_parameters_col.row()
        settings_row9.prop(field, "viewer_GraphLineWidth")
        settings_row9.prop(field, "viewer_PointSize")
        
        settings_row10 = viewer_parameters_col.row()
        settings_row10.prop(field, "viewer_CameraSize")
        settings_row10.prop(field, "viewer_CameraLineWidth")
        
        settings_row11 = viewer_parameters_col.row()
        settings_row11.prop(field, "viewer_ViewpointX")
        settings_row11.prop(field, "viewer_ViewpointY")
        
        settings_row12 = viewer_parameters_col.row()
        settings_row12.prop(field, "viewer_ViewpointZ")
        settings_row12.prop(field, "viewer_ViewpointF")
        #---------------------------------------------------------------
        video_file_path_col = layout.column()
        video_file_path_col.prop(field, "video_file_path")
        #video_file_path_col.enabled = False
        
        #layout.operator("wm.load_video")  # set video_file_path
        layout.operator("wm.convert_video", text=bpy.app.translations.pgettext("Convert Video To Sequence"))

        debug_col = layout.column()
        debug_col.prop(field, "output_folder_path")

        layout.operator("wm.processing_video_sequence", text=bpy.app.translations.pgettext("Processing Video Sequence"))
        layout.operator("wm.convert_points_to_curve", text=bpy.app.translations.pgettext("Convert Points To Curve"))
        layout.operator("wm.add_virtual_camera", text=bpy.app.translations.pgettext("Add Virtual Camera"))
        layout.operator("wm.create_camera_animation", text=bpy.app.translations.pgettext("Create Camera Animation"))
        layout.separator()

# ------------------------------------------------------------------------
#    Helpers
# ------------------------------------------------------------------------

def get_script_folder_path():
    script_filename = inspect.getframeinfo(inspect.currentframe()).filename
    script_folder_path = os.path.dirname(os.path.abspath(script_filename))

    return script_folder_path

def get_slam_folder_path():
    script_folder_path = get_script_folder_path()

    slam_algorithm = bpy.context.scene.curve_builder_fields.slam_algorithm
    slam_algorithm_path = os.path.join(script_folder_path, slam_algorithm)

    return slam_algorithm_path

def repair_yaml_file(filepath):
    s = open(filepath).read()
    s = s.replace(':', ': ')
    s = s.replace('  ', ' ')
    f = open(filepath, 'w')
    f.write(s)
    f.close()

def get_field_names():
    class_attributes = CurveBuilderFields.__dict__

    fields = {}
    for key in class_attributes.keys():
        value = class_attributes.get(key)
        if not value:
            continue

        try:
            if not value[1]:
                continue

            name = value[1].get('name')
            if '.' in name:
                fields[key] = name
        except:
            continue

    return fields

def write_settings_file(data, filepath):
    precision_first = 8
    precision_second = 2

    precision_first_list = [
        'Camera.fx',
        'Camera.fy',
        'Camera.cx',
        'Camera.cy',
        'Camera.k1',
        'Camera.k2',
        'Camera.p1',
        'Camera.p2',
        'Camera.k3',
    ]
    precision_second_list = [
        'ORBextractor.scaleFactor',
        'Viewer.KeyFrameSize',
        'Viewer.GraphLineWidth',
        'Viewer.CameraSize',
        'Viewer.ViewpointX',
        'Viewer.ViewpointY',
        'Viewer.ViewpointZ',
    ] 

    field_names = get_field_names()
    for variable_name in field_names:
        attribute_name = field_names.get(variable_name)

        value = getattr(bpy.context.scene.curve_builder_fields, variable_name)
        if attribute_name in precision_first_list:
            value = round(value, precision_first)
        elif attribute_name in precision_second_list:
            value = round(value, precision_second)
        data[attribute_name] = value

    file = open(filepath, "w")
    file.write("%YAML 1.0\n")
    file.close()

    with open(filepath, 'a') as outfile:
        yaml.dump(data, outfile, default_flow_style=False)
# ------------------------------------------------------------------------
#    Registration (custom groups)
# ------------------------------------------------------------------------

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.curve_builder_fields = PointerProperty(type=CurveBuilderFields)
    try:
        bpy.app.translations.register(__name__, translation_dict)  # register UA translations
    except:
        bpy.app.translations.unregister(__name__)
        bpy.app.translations.register(__name__, translation_dict)

def unregister():
    bpy.app.translations.unregister(__name__)  # unregister UA translations
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.curve_builder_fields


if __name__ == "__main__":
    register()
