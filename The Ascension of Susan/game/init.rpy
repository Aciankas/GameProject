init:
    image gold_image = ("images/icons/gold.png")
    image red_light_night_bg = Transform("images/locations/scene_red_light_night.jpg", fit='contain', xsize = 1920, ysize = 1080)
    image nothing_bg = Transform("gui/Empty.png", fit='contain', xsize = 1920, ysize = 1080)
    transform revealer(img, x_pos = 0, y_pos = 0, x_size = 1, y_size = 1, pauser = 0.0):
        Transform(Crop((x_pos, y_pos, x_size, y_size), img), xpos = x_pos, ypos = y_pos)
        pause pauser
        "nothing_bg" with Dissolve(0.2)