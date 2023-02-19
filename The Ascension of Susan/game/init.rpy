init:
    image gold_image = ("images/icons/gold.png")
    image red_light_night_bg = Transform("images/locations/scene_red_light_night.jpg", fit='contain', xsize = 1920, ysize = 1080)
    image nothing_bg = Transform("gui/Empty.png", fit='contain', xsize = 1920, ysize = 1080)
    #image line_high_transparent_frame = Frame("gui/frame_edge_line_high_transparent.png")
    transform revealer(img, pauser = 0.0, to_img = "nothing_bg"):
        img
        pause pauser
        to_img with Dissolve(0.2)
    
    transform re_revealer(img, pauser = 0.0, re_pauser = 0.1, to_img = "nothing_bg"):
        revealer(img, pauser, to_img)
        pause re_pauser-pauser
        img with Dissolve(0.2)

    transform crop_revealer(img, x_pos = 0, y_pos = 0, x_size = 1, y_size = 1, pauser = 0.0, to_img = "nothing_bg"):
        revealer(img = Transform(Crop((x_pos, y_pos, x_size, y_size), img), xpos = x_pos, ypos = y_pos), pauser = pauser, to_img = Transform(Crop((x_pos, y_pos, x_size, y_size), to_img), xpos = x_pos, ypos = y_pos))

    transform re_crop_revealer(img, x_pos = 0, y_pos = 0, x_size = 1, y_size = 1, pauser = 0.0, re_pauser = 0.1, to_img = "nothing_bg"):
        crop_revealer(img, x_pos, y_pos, x_size, y_size, pauser, to_img)
        pause re_pauser-pauser
        Transform(Crop((x_pos, y_pos, x_size, y_size), img), xpos = x_pos, ypos = y_pos) with Dissolve(0.2)