bl_info = {
    "name": "Curve Builder",
    "description": "Diplom project",
    "author": "Akeyn",
    "version": (0, 0, 1),
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

from bpy_extras.io_utils import ExportHelper
from bpy.props import (StringProperty,
                       CollectionProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       OperatorFileListElement,
                       PropertyGroup,
                       )

#logging.config.fileConfig('logging.conf')

# ------------------------------------------------------------------------
#    Scene Properties (custom fields)
# ------------------------------------------------------------------------

class CurveBuilderFields(PropertyGroup):

    slam_algorithm = EnumProperty(
        name="Slam Algorithm",
        description="Apply Algorithm to attribute.",
        items=[ ('OP1', "ORB SLAM", ""),
                #('OP2', "LSD SLAM", ""),
               ],
        default=None,
        update=None,
        get=None,
        set=None
        )

    file_path_to_settings = StringProperty(
        name="File Path To Settings",
        description=":",
        default="",
        maxlen=1024,
        )

    video_file_path = StringProperty(
        name="Video File Path",
        description=":",
        default="",
        maxlen=1024,
        )

    out_folder_path = StringProperty(
        name="Out Folder Path",
        description=":",
        default="",
        maxlen=1024,
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
    camera_fps = FloatProperty(
        name="Camera.fps",
        description=":",
        default=20,
        max=30
        )
    # Color order of the images (0: BGR, 1: RGB. It is ignored if images are grayscale)
    camera_RGB = FloatProperty(
        name="Camera.RGB",
        description=":",
        default=1,
        max=1
        )
    # ORB Extractor: Number of features per image
    ORBextractor_nFeatures = FloatProperty(
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
    ORBextractor_nLevels = FloatProperty(
        name="ORBextractor.nLevels",
        description=":",
        default=8,
        )
    # ORB Extractor: Fast threshold
    # Image is divided in a grid. At each cell FAST are extracted imposing a minimum response.
    # Firstly we impose iniThFAST. If no corners are detected we impose a lower value minThFAST
    # You can lower these values if your images have low contrast
    ORBextractor_iniThFAST = FloatProperty(
        name="ORBextractor.iniThFAST",
        description=":",
        default=20,
        )
    ORBextractor_minThFAST = FloatProperty(
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
    viewer_KeyFrameLineWidth = FloatProperty(
        name="Viewer.KeyFrameLineWidth",
        description=":",
        default=1,
        )
    viewer_GraphLineWidth = FloatProperty(
        name="Viewer.GraphLineWidth",
        description=":",
        default=0.9,
        )
    viewer_PointSize = FloatProperty(
        name="Viewer.PointSize",
        description=":",
        default=2,
        )
    viewer_CameraSize = FloatProperty(
        name="Viewer.CameraSize",
        description=":",
        default=0.08,
        )
    viewer_CameraLineWidth = FloatProperty(
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
    viewer_ViewpointF = FloatProperty(
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
        # TODO add logic to the case of assembly of the selected algorithm
        os.system("cd /home/asterios/Akeyn/VideoTo3DCurve/ORB_SLAM2; ./build.sh")
        return {'FINISHED'}

class WM_OT_import_settings(bpy.types.Operator):
    bl_idname = "wm.import_settings"
    bl_label = "Import Settings"

    def execute(self, context):
        # TODO
        return {'FINISHED'}

class WM_OT_export_settings(bpy.types.Operator):
    bl_idname = "wm.export_settings"
    bl_label = "Export Settings"

    def execute(self, context):
        # TODO
        return {'FINISHED'}

class WM_OT_apply_settings(bpy.types.Operator):
    bl_idname = "wm.apply_settings"
    bl_label = "Apply Settings"

    def execute(self, context):
        # TODO
        return {'FINISHED'}

class WM_OT_load_video(bpy.types.Operator, ExportHelper):  # Create base class (name = wm.get_filepath)
    bl_idname = "wm.load_video"
    bl_label = "Load video file"
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

        bpy.context.scene.curve_builder_fields.video_file_path = filepath
        return {'FINISHED'}

class WM_OT_convert_video_to_sequence(bpy.types.Operator):
    bl_idname = "wm.convert_video"
    bl_label = "Convert Video To Sequence"

    def execute(self, context):  # in tmp
        tmp = '/tmp'
        video_file_path = bpy.context.scene.curve_builder_fields.video_file_path
        video_file_name = os.path.splitext(os.path.basename(bpy.context.scene.curve_builder_fields.video_file_path))[0]
        out_folder = os.path.join(tmp, video_file_name)

        bpy.context.scene.curve_builder_fields.out_folder_path = out_folder

        if os.path.exists(out_folder):
            shutil.rmtree(out_folder, ignore_errors=True)

        os.makedirs(out_folder)
        
        # TODO get current python file path
        fps = 20  # fps like in the sam.yaml settings (20 or 30)
        rotchoice = 'n'  # rotation(yes or no)
        os.system("/home/asterios/Akeyn/VideoTo3DCurve/video_to_points.sh {0} {1} {2} {3}".format(video_file_path, out_folder, fps, rotchoice))
        
        return {'FINISHED'}

class WM_OT_processing_video_sequence(bpy.types.Operator):
    bl_idname = "wm.processing_video_sequence"
    bl_label = "Processing Video Sequence"

    def execute(self, context):
        # TODO /home/asterios/Akeyn/VideoTo3DCurve/ORB_SLAM2/ - create method for getting current folder path
        mono_rcs = "/home/asterios/Akeyn/VideoTo3DCurve/ORB_SLAM2/Examples/Monocular/mono_rcs"   # mono_rcs.cc (Save camera trajectory "KeyFrameTrajectory.txt")
                                                                                # mono_rcs - have to build by bash "/home/asterios/Akeyn/VideoTo3DCurve/ORB_SLAM2/build.sh" (If it was edit)
        
        ORBvoc = "/home/asterios/Akeyn/VideoTo3DCurve/ORB_SLAM2/Vocabulary/ORBvoc.txt"           # refactor set as CONST (vocabulary)
        sam = "/home/asterios/Akeyn/VideoTo3DCurve/ORB_SLAM2/Examples/Monocular/sam.yaml"        # refactor set as setting variable (camera settings)
        out_folder = bpy.context.scene.curve_builder_fields.out_folder_path
        os.system("{0} {1} {2} {3}".format(mono_rcs, ORBvoc, sam, out_folder))
        return {'FINISHED'}

class WM_OT_convert_points_to_curve(bpy.types.Operator):
    bl_idname = "wm.convert_points_to_curve"
    bl_label = "Convert Points To Curve"

    def execute(self, context):
        out_folder = bpy.context.scene.curve_builder_fields.out_folder_path
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

# ------------------------------------------------------------------------
#    Panel in Object Mode (custom groups)
# ------------------------------------------------------------------------

class CurveBuilder_CustomPanel(Panel):
    """Curve Builder Script"""
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label = "Curve Builder"
    bl_context = "objectmode"
    bl_category = "Diplom"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        field = scene.curve_builder_fields

        layout.label("Select Algorithm")
        algorithm_col = layout.column()
        algorithm_col.prop(field, "slam_algorithm") 
        algorithm_col.operator("wm.build_algorithm")
        algorithm_col.enabled = False
        #---------------------------------------------------------------
        layout.label("Camera Settings")

        settings_col = layout.column()
        
        settings_row1 = layout.row()
        settings_row1.prop(field, "camera_fx")
        settings_row1.prop(field, "camera_fy")
        
        settings_row2 = layout.row()
        settings_row2.prop(field, "camera_cx")
        settings_row2.prop(field, "camera_cy")
        
        settings_row3 = layout.row()
        settings_row3.prop(field, "camera_k1")
        settings_row3.prop(field, "camera_k2")

        settings_row4 = layout.row()
        settings_row4.prop(field, "camera_p1")
        settings_row4.prop(field, "camera_p2")

        layout.prop(field, "camera_k3")
        
        settings_row5 = layout.row()
        camera_fps_col = settings_row5.column()
        camera_fps_col.label("Camera frames per second")
        camera_fps_col.prop(field, "camera_fps")
        
        camera_RGB_col = settings_row5.column()
        camera_RGB_col.label("Color order of the images")
        camera_RGB_col.prop(field, "camera_RGB")

        ORBextractor_nFeatures_col = settings_row5.column()
        ORBextractor_nFeatures_col.label("Number of features per image")
        ORBextractor_nFeatures_col.prop(field, "ORBextractor_nFeatures")
        
        settings_row6 = layout.row()
        ORBextractor_scaleFactor_col = settings_row6.column()
        ORBextractor_scaleFactor_col.label("Scale factor between levels in the scale pyramid")
        ORBextractor_scaleFactor_col.prop(field, "ORBextractor_scaleFactor")

        ORBextractor_nLevels_col = settings_row6.column()
        ORBextractor_nLevels_col.label("Number of levels in the scale pyramid")
        ORBextractor_nLevels_col.prop(field, "ORBextractor_nLevels")
        
        fast_threshold_col = layout.column()
        fast_threshold_col.label("Fast threshold")
        settings_row7 = fast_threshold_col.row()
        settings_row7.prop(field, "ORBextractor_iniThFAST")
        settings_row7.prop(field, "ORBextractor_minThFAST")
        
        viewer_parameters_col = layout.column()
        viewer_parameters_col.label("Viewer Parameters")
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

        input_settings_col = layout.column()
        input_settings_col.prop(field, "file_path_to_settings")
        input_settings_col.enabled = False

        settings_action_row = layout.row()
        settings_action_row.operator("wm.import_settings")
        settings_action_row.operator("wm.export_settings")
        settings_action_row.operator("wm.apply_settings")
        #---------------------------------------------------------------
        video_file_path_col = layout.column()
        video_file_path_col.prop(field, "video_file_path")
        video_file_path_col.enabled = False
        
        layout.operator("wm.load_video")  # set video_file_path
        layout.operator("wm.convert_video")

        debug_col = layout.column()
        debug_col.prop(field, "out_folder_path")
        debug_col.enabled = False

        layout.operator("wm.processing_video_sequence")
        layout.operator("wm.convert_points_to_curve")
        #layout.prop(field, "create_cam_path")
        #layout.prop(field, "create_cam_animation")
        layout.separator()

# ------------------------------------------------------------------------
#    Registration (custom groups)
# ------------------------------------------------------------------------

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.curve_builder_fields = PointerProperty(type=CurveBuilderFields)

def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.curve_builder_fields

if __name__ == "__main__":
    register()
