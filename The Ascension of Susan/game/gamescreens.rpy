# Изображение в рамке
screen framed_image(pic_path, arg_xalign=None, arg_yalign=None, arg_xpos=None, arg_ypos=None, arg_xmax=None, arg_ymax=None, arg_xsize=None, arg_ysize=None):
    frame:
        style "frame_empty"
        xalign arg_xalign
        yalign arg_yalign
        python:
            arg_xpadding = 16
            arg_ypadding = 16
            if arg_xmax is None and arg_xsize is None:
                pic_xsize = 150
            elif arg_xmax is not None:
                arg_xsize = None
                pic_xsize = arg_xmax-arg_xpadding
            else:
                pic_xsize = arg_xsize-arg_xpadding
            if arg_ymax is None and arg_ysize is None:
                pic_ysize = 300
            elif arg_ymax is not None:
                arg_ysize = None
                pic_ysize = arg_ymax-arg_ypadding
            else:
                pic_ysize = arg_ysize-arg_ypadding
        frame:
            xpos arg_xpos
            ypos arg_ypos
            xmaximum arg_xmax
            ymaximum arg_ymax
            xsize arg_xsize
            ysize arg_ysize
            padding (arg_xpadding, arg_ypadding)
            foreground Frame("gui/frame_corner_background.png", 68, 68, 68, 68, tile=True)
            background None
            image Transform(pic_path, fit='contain', xysize = (pic_xsize,pic_ysize))

screen infobox(info='default', orientation='down'):
    frame:
        style "frame_thin_line"
        pos renpy.get_mouse_pos()
        if orientation == 'up':
            anchor (0.0, 1.0)
        elif orientation == 'down':
            anchor (0.0, 0.0)
        text "[info]"

screen resource_ui:
    frame:
        has hbox
        add "gold_image"
        text " [g_base.gold] "
        textbutton "Меню" action ui.callsinnewcontext("test_menu_label")
