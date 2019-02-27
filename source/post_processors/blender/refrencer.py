
import bpy
import os
import sys

asurt_path = r'C:\Users\khaled.ghobashy\Desktop\Khaled Ghobashy\Mathematical Models\asurt_cdt_symbolic'
if asurt_path not in sys.path:
    sys.path.append(asurt_path)

def read_some_data(context, filepath, use_some_setting):
    print("Reading Python Script...")
    full_path = filepath.split(os.path.sep)
    d = full_path.index('asurt_cdt_symbolic')
    imports  = full_path[d+1:]
    script_name  = imports[-1].split('.')[0]
    del imports[-1]
    imports_str  = '.'.join(imports)
    exec('from %s import %s'%(imports_str,script_name))
    return {'FINISHED'}


# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

from bpy.props import CollectionProperty

class ImportScript(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_test.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "ImportScript"
    
    # ImportHelper mixin class uses this
    filename_ext = ".py"
    files = CollectionProperty(type=bpy.types.PropertyGroup)

    filter_glob = StringProperty(
            default="*.py",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    use_setting = BoolProperty(
            name="Example Boolean",
            description="Example Tooltip",
            default=True,
            )

    type = EnumProperty(
            name="Example Enum",
            description="Choose between two items",
            items=(('OPT_A', "First Option", "Description one"),
                   ('OPT_B', "Second Option", "Description two")),
            default='OPT_A',
            )

    def execute(self, context):
        return read_some_data(context, self.filepath, self.use_setting)


# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportScript.bl_idname, text="Import .py file")


def register():
    bpy.utils.register_class(ImportScript)
    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportScript)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
    bpy.ops.import_test.some_data('INVOKE_DEFAULT')

