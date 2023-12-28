'''
latk_video_001 (Blender)
Copyright (c) 2023 Nick Fox-Gieg
https://fox-gieg.com

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

latk_video_001 (Blender) is free software: you can redistribute it 
and/or modify it under the terms of the GNU General Public License 
as published by the Free Software Foundation, either version 3 of 
the License, or (at your option) any later version.

latk_video_001 (Blender) is distributed in the hope that it will 
be useful, but WITHOUT ANY WARRANTY; without even the implied warranty 
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with latk_video_001 (Blender). If not, see 
<http://www.gnu.org/licenses/>.
'''

bl_info = {
    "name": "latk_video_001", 
    "author": "Nick Fox-Gieg",
    "version": (0, 0, 1),
    "blender": (4, 0, 0),
    "description": "An open solution for streaming 3D point clouds",
    "category": "Animation"
}

import bpy
from bpy.types import Operator, AddonPreferences
from bpy.props import (BoolProperty, FloatProperty, StringProperty, IntProperty, PointerProperty, EnumProperty)
from bpy_extras.io_utils import (ImportHelper, ExportHelper)
#import gpu
import addon_utils
from mathutils import Vector, Matrix
import bmesh

import os
import sys
import subprocess
import platform
import argparse
import numpy as np

from . latk_video import *

class LatkVideoPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    '''
    Backend: EnumProperty(
        name="ML Backend",
        items=(
            ("NONE", "None", "...", 0),
            ("PYTORCH", "PyTorch", "...", 1),
            ("ONNX", "ONNX", "...", 2)
        ),
        default="NONE"
    )
    '''

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="Features")
        row = box.row()
        #row.prop(self, "feature_Meshing")


# This is needed to display the preferences menu
# https://docs.blender.org/api/current/bpy.types.AddonPreferences.html
class OBJECT_OT_latk_video_prefs(Operator):
    """Display example preferences"""
    bl_idname = "object." + __name__
    bl_label = "LatkVideo Preferences"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[__name__].preferences

        #info = ((addon_prefs.extraFormats_AfterEffects))
        #self.report({'INFO'}, info)
        #print(info)

        return {'FINISHED'}


class LatkVideoProperties(bpy.types.PropertyGroup):
    """Properties for Latk"""
    bl_idname = "GREASE_PENCIL_PT_LatkVideoProperties"

    bakeMesh: BoolProperty(
        name="Bake",
        description="Off: major speedup if you're staying in Blender. On: slower but keeps everything exportable",
        default=True
    )


class ExportLatkVideo(bpy.types.Operator, ExportHelper): # TODO combine into one class
    """Save a Latk Json File"""

    bake = BoolProperty(name="Bake Frames", description="Bake Keyframes to All Frames", default=False)
    #roundValues = BoolProperty(name="Limit Precision", description="Round Values to Reduce Filesize", default=False)    
    #numPlaces = IntProperty(name="Number Places", description="Number of Decimal Places", default=7)
    useScaleAndOffset = BoolProperty(name="Use Scale and Offset", description="Compensate scale for Blender viewport", default=True)

    bl_idname = "export_scene.latkjson"
    bl_label = 'Export Latk Json'
    bl_options = {'PRESET'}

    filename_ext = ".json"

    filter_glob = StringProperty(
            default="*.json",
            options={'HIDDEN'},
            )

    def execute(self, context):
        import latk_blender as la
        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "filter_glob", "split_mode", "check_existing", "bake", "useScaleAndOffset")) #, "roundValues", "numPlaces"))
        if bpy.data.is_saved:
            import os
        #~
        keywords["bake"] = self.bake
        #keywords["roundValues"] = self.roundValues
        #keywords["numPlaces"] = self.numPlaces
        keywords["useScaleAndOffset"] = self.useScaleAndOffset
        #~
        la.writeBrushStrokes(**keywords, zipped=False)
        return {'FINISHED'}


classes = (
    ExportLatkVideo,
    OBJECT_OT_latk_video_prefs,
    LatkVideoPreferences,
    LatkVideoProperties
)

def menu_func_export(self, context):
    self.layout.operator(ExportLatkVideo.bl_idname, text="Latk Video (.mp4)")

# * * * * * * * * * * * * * * * * * * * * * * * * * *
def register():
    for cls in classes:
        bpy.utils.register_class(cls)   

    bpy.types.Scene.latk_video_settings = bpy.props.PointerProperty(type=LatkVideoProperties)

    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

    del bpy.types.Scene.latk_video_settings

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
# * * * * * * * * * * * * * * * * * * * * * * * * * *
