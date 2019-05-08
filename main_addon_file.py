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

logging.config.fileConfig('logging.conf')

# ------------------------------------------------------------------------
#    Scene Properties (custom fields)
# ------------------------------------------------------------------------

class CurveBuilderFields(PropertyGroup):

    select_algorithm = EnumProperty(
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

    input_cam_settings = StringProperty(
        name="Cam Settings",
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

# ------------------------------------------------------------------------
#    Operators (custom functions)
# ------------------------------------------------------------------------

class WM_OT_load_video(bpy.types.Operator, ExportHelper):  # Create base class (name = wm.get_filepath)
    bl_idname = "wm.load_video"
    bl_label = "Load video"
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
        
        subprocess.call(['video_to_points.sh', video_file_path, out_folder, 10, 'y'])
        
        return {'FINISHED'}

class WM_OT_processing_video_sequence(bpy.types.Operator):
    bl_idname = "wm.processing_video_sequence"
    bl_label = "Processing Video Sequence"

    def execute(self, context):
        mono_rcs = "/home/asterios/orb_slam2_mod/Examples/Monocular/mono_rcs"   # mono_rcs.cc (Save camera trajectory "KeyFrameTrajectory.txt")
                                                                                # mono_rcs - have to build by bash "/home/asterios/orb_slam2_mod/build.sh" (If it was edit)
        
        ORBvoc = "/home/asterios/orb_slam2_mod/Vocabulary/ORBvoc.txt"           # refactor set as CONST (vocabulary)
        sam = "/home/asterios/orb_slam2_mod/Examples/Monocular/sam.yaml"        # refactor set as setting variable (camera settings)
        out_folder = bpy.context.scene.curve_builder_fields.out_folder_path
        os.system("{0} {1} {2} {3}".format(mono_rcs, ORBvoc, sam, out_folder))
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

        layout.prop(field, "select_algorithm", text="Select Algorithm") 
        layout.prop(field, "input_cam_settings", text="Input Cam Settings")
        
        #layout.prop(field, "setting_filepath")
        #layout.operator("wm.load_video", text='Load video file')  # set video_file_path

        #layout.prop(field, "load_cam_settings")
        #layout.prop(field, "save_cam_settings")

        layout.prop(field, "video_file_path", text="Video File Path")
        layout.operator("wm.load_video", text='Load video file')  # set video_file_path
        layout.operator("wm.convert_video", text='Convert Video To Sequence')
        layout.prop(field, "out_folder_path", text="Out Folder Path")
        layout.operator("wm.processing_video_sequence", text='Processing Video Sequence')
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
