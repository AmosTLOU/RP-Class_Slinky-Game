import random
import os
import math
import pygame as pg

PI = 3.1415926
Multiplier_AngleToRad = PI / 180

START_TIME = 120


# see if we can load more than standard BMP
if not pg.image.get_extended():
    raise SystemExit("Sorry, extended image module required")

FPS = 60
Size_Screen = [1080, 720]
SCREENRECT = pg.Rect(0, 0, Size_Screen[0], Size_Screen[1])
Size_PlayerImage = [160, 160]


StartPos_Player = [1220, 1190]  # pos of the slinky's bottom midpoint
Origin_Local = [StartPos_Player[0]-Size_Screen[0] //
                2, StartPos_Player[1]-3*Size_Screen[1]//4]
Len_StaticSlinky = 45  # the distance from top to bottom when stationary
Instances_platform = []
main_dir = os.path.split(os.path.abspath(__file__))[0]


def load_image(file):
    file = os.path.join(main_dir, "data", file)
    try:
        surface = pg.image.load(file)
    except pg.error:
        raise SystemExit('Could not load image "%s" %s' %
                         (file, pg.get_error()))
    return surface.convert_alpha()


def load_sound(file):
    if not pg.mixer:
        return None
    file = os.path.join(main_dir, "data\Music", file)
    try:
        sound = pg.mixer.Sound(file)
        return sound
    except pg.error:
        print("Warning, unable to load, %s" % file)
    return None


def e_dst(coord_a, coord_b):
    return math.sqrt((coord_a[0] - coord_b[0])**2 + (coord_a[1] - coord_b[1])**2)


def globalToLocal(coord_global):
    return [coord_global[0] - Origin_Local[0], coord_global[1] - Origin_Local[1]]


def localToGlobal(coord_local):
    return [coord_local[0] + Origin_Local[0], coord_local[1] + Origin_Local[1]]


def touched(coord, box):
    return True if box[0][0] <= coord[0] and coord[0] <= box[1][0] and box[0][1] <= coord[1] and coord[1] <= box[1][1] else False


class Player(pg.sprite.Sprite):
    images = []  # class static variable!
    music = None

    def __init__(self):   # instance variable!
        pg.sprite.Sprite.__init__(self, self.containers)
        self.angle = 0  # 0 upwards    1 to left    2 downwards    3 to right
        self.image = self.assignImage(self.images[0])
        self.rect = self.image.get_rect()
        self.size = [self.image.get_rect().width, self.image.get_rect().height]
        self.pos_bottom = [StartPos_Player[0], StartPos_Player[1]]
        self.pos_top = [self.pos_bottom[0],
                        self.pos_bottom[1]-Len_StaticSlinky]
        self.markPoint = None
        self.shift_dst = [0, 0]
        self.shift_dir = [1, 1]
        self.beingHold = False

    def getTop(self):
        x = 0
        y = Len_StaticSlinky
        cos_theta = round(math.cos(self.angle * Multiplier_AngleToRad))
        sin_theta = round(math.sin(self.angle * Multiplier_AngleToRad))
        x_ = cos_theta * x - sin_theta * y
        y_ = sin_theta * x + cos_theta * y
        return [self.pos_bottom[0] + x_, self.pos_bottom[1] - y_]

    def getStandardXY(self, x, y):
        if self.angle < 0 or self.angle > 360:
            print("Error: angele out of range")
            exit()
        cos_theta = round(math.cos(self.angle * Multiplier_AngleToRad))
        sin_theta = round(math.sin(self.angle * Multiplier_AngleToRad))
        x_ = cos_theta * x + sin_theta * y
        y_ = -sin_theta * x + cos_theta * y
        return x_, y_

    def assignImage(self, image):
        return pg.transform.rotate(image, self.angle)

    def release(self, land=False):
        if not land:
            self.music.play(0)
        self.image = self.assignImage(self.images[0])
        self.pos_top = self.getTop()
        self.markPoint.pos = self.pos_top[:]
        self.markPoint.adjustImage(self.angle)
        self.beingHold = False

    def drag(self, coord_mouse):
        coord_mouse = localToGlobal(coord_mouse)
        # if the mouse was too far from the top-end, then the slinky couldn't be dragged
        if e_dst(self.pos_top, coord_mouse) > 20:
            return
        if not self.beingHold:  # if it was the first mouse click on slinky and the mouse was in the range of any collider box, then do nothing
            for p in Instances_platform:
                for box in p.boxes:
                    if touched(coord_mouse, box):
                        self.release()
                        return
        x, y = self.getStandardXY(
            coord_mouse[0] - self.pos_bottom[0],  -coord_mouse[1] + self.pos_bottom[1])
        relative_distance = abs(x) + abs(y)
        if relative_distance > 150:  # get the top-end back
            self.release()
        else:
            self.beingHold = True
            self.pos_top = coord_mouse[:]
            # TODO Apply the image according to (x, y)   which is the relative distance
            measure = abs(x)
            if x > 0:
                self.image = self.assignImage(self.images[min(measure//3, 16)])
                dir_markPoint = 1
            else:
                self.image = self.assignImage(pg.transform.flip(
                    self.images[min(measure//3, 16)], 1, 0))
                dir_markPoint = 0
            self.markPoint.pos = self.pos_top[:]
            self.markPoint.adjustImage(self.angle, dir_markPoint)
            for p in Instances_platform:
                for i in range(len(p.boxes)):
                    if touched(self.pos_top, p.boxes[i]):
                        # if landpoint too close to bottom, then don't move
                        if e_dst(self.pos_bottom, self.pos_top) < 30:
                            self.release()
                            return
                        self.angle = p.angle_boxes[i]
                        self.land()
                        return

    def land(self):
        print("Slinky lands on a new point!")
        self.music.play(1)
        self.shift_dst[0], self.shift_dst[1] = abs(
            self.pos_top[0] - self.pos_bottom[0]), abs(self.pos_top[1] - self.pos_bottom[1])
        self.shift_axis_further = 0 if self.shift_dst[0] >= self.shift_dst[1] else 1
        self.shift_dir[0] = 1 if (
            self.pos_top[0] - self.pos_bottom[0]) > 0 else -1
        self.shift_dir[1] = 1 if (
            self.pos_top[1] - self.pos_bottom[1]) > 0 else -1
        self.pos_bottom = self.pos_top[:]
        self.release(land=True)

    def update(self):
        speed = 7
        if self.shift_dst[0] > 0 or self.shift_dst[1] > 0:
            for i in range(2):
                s = speed if self.shift_dst[i] > speed else self.shift_dst[i]
                Origin_Local[i] += s if self.shift_dir[i] > 0 else -s
                self.shift_dst[i] -= s
        self.markPoint.pos = self.pos_top[:]
        local_coord = globalToLocal(self.pos_bottom)
        self.rect = pg.Rect(
            local_coord[0]-self.size[0]//2, local_coord[1]-self.size[1]//2, self.rect[2], self.rect[3])


class Platform(pg.sprite.Sprite):
    images = []

    def __init__(self):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.pos = [0, 0]
        self.size = [0, 0]
        self.boxes = []
        self.angle_boxes = []  # 0 upwards    1 to left    2 downwards    3 to right
        # self.rect.move_ip(random.randrange(100, 400), random.randrange(100, 400))

    def setPos(self, left, top):
        self.pos[0], self.pos[1] = left, top

    def setSize(self, width, height):
        self.size[0], self.size[1] = width, height

    def setPosAndSize(self, left, top, width, height):
        self.pos[0], self.pos[1] = left, top
        self.size[0], self.size[1] = width, height

    def setColliderBoxes(self, thickness):
        l = self.pos[0]
        t = self.pos[1]
        w = self.size[0]
        h = self.size[1]
        self.boxes.append([[l, t], [l+w, t+thickness]])
        self.boxes.append([[l, t+h], [l+w, t+h+thickness]])
        self.boxes.append([[l, t], [l+thickness, t+h]])
        self.boxes.append([[l+w, t], [l+w+thickness, t+h]])
        self.angle_boxes = [0, 180, 90, 270]

    def update(self):
        local_coord = globalToLocal(self.pos)
        self.rect = pg.Rect(
            local_coord[0], local_coord[1], self.size[0], self.size[1])


class MarkPoint(pg.sprite.Sprite):
    images = []

    def __init__(self):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.pos = [0, 0]
        self.size = [self.rect[2], self.rect[3]]

    def adjustImage(self, angle, dir=0):
        self.image = pg.transform.rotate(
            pg.transform.flip(self.images[0], dir, 0), angle)

    def update(self):
        local_coord = globalToLocal(self.pos)
        self.rect = pg.Rect(
            local_coord[0]-self.size[0]//2, local_coord[1]-self.size[1]//2, self.rect[2], self.rect[3])


class Music():
    def __init__(self):
        self.sfx = [load_sound("slinky_back.wav"),
                    load_sound("slinky_land.wav")]
        self.music_mixer = pg.mixer

    def play(self, ind):
        self.sfx[ind].play()


class Timer():
    def __init__(self):
        self.frame_count = 0
        # self.total_seconds = self.start_time - (self.frame_count // FPS)
        self.minutes = 0
        self.seconds = 0
        # initialize fonts
        self.font = pg.font.Font(None, 50)

    def timerDisplay(self):
        self.minutes = self.total_seconds // 60
        self.seconds = self.total_seconds % 60
        output_string = "Time: {0:02}:{1:02}".format(
            self.minutes, self.seconds)
        print(output_string)
        text = self.font.render(output_string, True, (0, 0, 0))
        # return text
        screen.blit(text, (50, 50))

    def timerUpdate(self):
        self.total_seconds = START_TIME - (self.frame_count // FPS)
        if self.total_seconds < 0:
            self.total_seconds = 0
        self.frame_count += 1


pg.init()
# Set the display mode
winstyle = 0  # |FULLSCREEN
bestdepth = pg.display.mode_ok(SCREENRECT.size, winstyle, 32)
screen = pg.display.set_mode(SCREENRECT.size, winstyle, bestdepth)


def main(winstyle=0):
    # Initialize pygame
    if pg.get_sdl_version()[0] == 2:
        pg.mixer.pre_init(44100, 32, 2, 1024)
    pg.init()
    music = Music()
    if music.music_mixer and not music.music_mixer.get_init():
        print("Warning, no sound")
        pg.mixer = None

    fullscreen = False
    # Set the display mode
    winstyle = 0  # |FULLSCREEN
    bestdepth = pg.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pg.display.set_mode(SCREENRECT.size, winstyle, bestdepth)

    # Load images, assign to sprite classes
    # (do this before the classes are used, after screen setup)
    imagefiles_slinky = []
    for ind in range(1, 18):
        imagefiles_slinky.append("Slinky_17\slinky (" + str(ind) + ").png")
    Player.images = [load_image(im) for im in imagefiles_slinky]
    for i in range(len(Player.images)):
        Player.images[i] = pg.transform.scale(
            Player.images[i], Size_PlayerImage)

    imagefiles_items = []
    for ind in range(1, 7):
        imagefiles_items.append("item\\" + str(ind) + ".gif")
    Platform.images = [load_image(im) for im in imagefiles_items]

    MarkPoint.images = [load_image("eyes_.png")]

    # decorate the game window
    icon = pg.transform.scale(load_image("icon.jpg"), (32, 32))
    pg.display.set_icon(icon)
    pg.display.set_caption("Slinky Game")

    # create the background, tile the bgd image
    bgdtile = load_image("background.jpg")
    background = pg.Surface(SCREENRECT.size)
    for x in range(0, SCREENRECT.width, bgdtile.get_width()):
        background.blit(bgdtile, (x, 0))
    screen.blit(background, (0, 0))
    pg.display.flip()

    # load the sound effects
    if music.music_mixer:
        music_file = os.path.join(main_dir, "data", "music\\nervous.mp3")
        music.music_mixer.music.load(music_file)
        music.music_mixer.music.play(-1)

    Player.music = music

    # Initialize Game Groups
    platforms = pg.sprite.Group()
    # all = pg.sprite.RenderUpdates()
    all = pg.sprite.OrderedUpdates()

    # assign default groups to each sprite class
    Platform.containers = platforms, all

    Player.containers = all
    MarkPoint.containers = all

    # Create Some Starting Values
    clock = pg.time.Clock()

    # initialize our starting sprites
    player = Player()
    markPoint = MarkPoint()
    player.markPoint = markPoint

    num_p = 15
    for _ in range(num_p):
        Instances_platform.append(Platform())
    # TODO set the pos manually
    thickness = 10
    Instances_platform[0].setPosAndSize(1180, 1195, 128, 64)
    Instances_platform[0].image = Platform.images[5]
    Instances_platform[5].setPosAndSize(1308, 1195, 128, 64)
    Instances_platform[5].image = Platform.images[5]
    Instances_platform[1].setPosAndSize(1090, 940, 64, 64)
    Instances_platform[1].image = Platform.images[2]
    Instances_platform[2].setPosAndSize(1060, 1004, 64, 64)
    Instances_platform[2].image = Platform.images[2]
    Instances_platform[3].setPosAndSize(1080, 1068, 64, 64)
    Instances_platform[3].image = Platform.images[2]
    Instances_platform[4].setPosAndSize(1100, 1132, 64, 64)
    Instances_platform[4].image = Platform.images[2]
    Instances_platform[6].setPosAndSize(1190, 850, 128, 64)
    Instances_platform[6].image = Platform.images[3]
    Instances_platform[7].setPosAndSize(1500, 1250, 128, 64)
    Instances_platform[7].image = Platform.images[4]
    Instances_platform[8].setPosAndSize(1650, 1150, 64, 64)
    Instances_platform[8].image = Platform.images[0]
    Instances_platform[9].setPosAndSize(1750, 1050, 64, 64)
    Instances_platform[9].image = Platform.images[1]
    Instances_platform[10].setPosAndSize(1820, 1000, 64, 64)
    Instances_platform[10].image = Platform.images[1]
    Instances_platform[11].setPosAndSize(1890, 1050, 64, 64)
    Instances_platform[11].image = Platform.images[1]
    Instances_platform[12].setPosAndSize(1960, 1100, 64, 64)
    Instances_platform[12].image = Platform.images[1]
    for i in range(num_p):
        Instances_platform[i].setColliderBoxes(thickness)

    # timer
    timer = Timer()

    # Run our main loop whilst the player is alive.
    while player.alive():
        for event in pg.event.get():
            # get mouse input:
            mouse_1_hold = pg.mouse.get_pressed(3)[0]
            if mouse_1_hold:
                player.drag(pg.mouse.get_pos())
            elif player.beingHold:
                player.release()

            # get keys input:
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_f:
                    if not fullscreen:
                        print("Changing to FULLSCREEN")
                        screen_backup = screen.copy()
                        screen = pg.display.set_mode(
                            SCREENRECT.size, winstyle | pg.FULLSCREEN, bestdepth
                        )
                        screen.blit(screen_backup, (0, 0))
                    else:
                        print("Changing to windowed mode")
                        screen_backup = screen.copy()
                        screen = pg.display.set_mode(
                            SCREENRECT.size, winstyle, bestdepth
                        )
                        screen.blit(screen_backup, (0, 0))
                    pg.display.flip()
                    fullscreen = not fullscreen

        # timer
        timer.timerUpdate()

        keystate = pg.key.get_pressed()

        # clear/erase the last drawn sprites
        all.clear(screen, background)

        # update all the sprites
        all.update()

        # Detect collisions between player and platforms.
        # for platform in pg.sprite.spritecollide(player, platforms, 1):
        #     if pg.mixer:
        #         boom_sound.play()
        #     player.land(platform.rect)

        # draw the scene
        screen.blit(background, (0,0))
        timer.timerDisplay()
        dirty = all.draw(screen)
        # pg.display.update(dirty)
        pg.display.update()

        # set the framerate
        clock.tick(FPS)

    if pg.mixer:
        pg.mixer.music.fadeout(1000)
    pg.time.wait(1000)
    pg.quit()


# call the "main" function if running this script
if __name__ == "__main__":
    main()
