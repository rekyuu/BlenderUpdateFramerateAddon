import bpy


MSGBUS_OWNER=object()


class UpdateFramerateProperties(bpy.types.PropertyGroup):
    original_framerate: bpy.props.IntProperty(name="Original Framerate", default=24, min=0)
    original_start_frame: bpy.props.IntProperty(name="Original Start Frame", default=1, min=0)
    original_end_frame: bpy.props.IntProperty(name="Original End Frame", default=250, min=0)


class UpdateFramerateOriginalsOperator(bpy.types.Operator):
    bl_idname = "render.update_framerate_originals"
    bl_label ="Update Framerate Originals"

    def execute(self, context):
        context.scene.update_framerate_properties.original_framerate = context.scene.render.fps
        context.scene.update_framerate_properties.original_start_frame = context.scene.frame_start
        context.scene.update_framerate_properties.original_end_frame = context.scene.frame_end

        return {'FINISHED'}


class UpdateFrameratePanel(bpy.types.Panel):
    bl_idname = "RENDER_PT_update_framerate"
    bl_label ="Update Framerate Settings"
    bl_context = "output"
    bl_icon = "NONE"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_parent_id = "RENDER_PT_format"
    # bl_options = { }

    def draw(self, context):
        layout = self.layout

        layout.operator("render.update_framerate_originals", text="Update to current")

        layout.prop(context.scene.update_framerate_properties, "original_framerate")
        layout.prop(context.scene.update_framerate_properties, "original_start_frame")
        layout.prop(context.scene.update_framerate_properties, "original_end_frame")


def on_fps_changed():
    scene = bpy.context.scene

    fps_ratio = scene.render.fps / scene.update_framerate_properties.original_framerate

    scene.frame_start = int(round(scene.update_framerate_properties.original_start_frame * fps_ratio))
    scene.frame_end = int(round(scene.update_framerate_properties.original_end_frame * fps_ratio))
    scene.render.frame_map_old = scene.update_framerate_properties.original_framerate
    scene.render.frame_map_new = scene.render.fps


def register():
    bpy.msgbus.clear_by_owner(MSGBUS_OWNER)

    bpy.msgbus.subscribe_rna(
        key=(bpy.types.RenderSettings, "fps"),
        owner=MSGBUS_OWNER,
        args=(),
        notify=on_fps_changed
    )

    bpy.utils.register_class(UpdateFramerateProperties)
    bpy.utils.register_class(UpdateFramerateOriginalsOperator)
    bpy.utils.register_class(UpdateFrameratePanel)
    bpy.types.Scene.update_framerate_properties = bpy.props.PointerProperty(type=UpdateFramerateProperties)


def unregister():
    bpy.msgbus.clear_by_owner(MSGBUS_OWNER)

    bpy.types.Scene.update_framerate_properties = None
    bpy.utils.unregister_class(UpdateFrameratePanel)
    bpy.utils.unregister_class(UpdateFramerateOriginalsOperator)
    bpy.utils.unregister_class(UpdateFramerateProperties)