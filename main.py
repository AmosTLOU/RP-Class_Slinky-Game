import sys
import os
import math
import random
import pygame as pg
# from moviepy.editor import VideoFileClip
import utils
import algebra as alg

# global variables
GameReady = [True]
GameOver = [False]
GameWin = [False]
Instances_platform = []
Instances_interactable = []
Origin_Local = []
main_dir = os.path.split(os.path.abspath(__file__))[0]

# see if we can load more than standard BMP
if not pg.image.get_extended():
    raise SystemExit("Sorry, extended image module required")

# Variables for Controlling GamePlay
FPS = 60
Size_Screen = [1080, 720]
SCREENRECT = pg.Rect(0, 0, Size_Screen[0], Size_Screen[1])
Size_PlayerImage = [160, 160]
Size_ChaserImage = [200, 200]
Size_GameStatusImage = [450, 200]
Size_LongBackground = [2424, 480]

PlayIntro = False
if len(sys.argv) > 1:
    str_cmd = sys.argv[1]
    PlayIntro = True if str_cmd == "True" or str_cmd == "true" or str_cmd == "T" or str_cmd == "t" else False
Len_StaticSlinky = 45           # the distance from top to bottom of the static slink
Longest_StretchDst = 118        # better not changed, or the movement would look anti-intuitive
LeastDst_DragPlayer = 35        
LeastDst_LandPlayer = 30
Speed_Camera = 7                # pixels per frame
Time_ChaserMove = 0.05          # how long cat should wait for next move
Step_ChaserForward = 5          
Step_ChaserBackward = 30        # when cat bounces off the obstacle, how many pixels does it back off
Time_ChaserFramePlay = 0.1      # how long one chaser frame would play
Time_Chaser_Frozen = 2          # how long chaser would be frozen
Time_Player_Stuck = 2           # how long player would be stuck
Time_PlayerGetPower = 5         # how long player get power

ImgName_bg = "transparent.png"
MusicName_bg = "nervous.mp3"
Imagefiles_item = ["1.gif", "2.gif", "3.gif", "4.gif", "5.gif", "6.gif", "7.gif", "Hitbox_Car_Roof.png", "Hitbox_Car_Hood.png" , "Hitbox_Wrench.png" , "Hitbox_Drill.png" , "Hitbox_Pliers.png" , "Hitbox_L_Curtain.png" , "Hitbox_Top_Curtain.png" , "Hitbox_R_Curtain.png" , "Hitbox_Bed.png"]

Names_Platform =     [  "2.gif",         "2.gif",        "2.gif",   "Hitbox_Car_Roof.png" ,    "Hitbox_Car_Hood.png",     "2.gif",       "2.gif",      "2.gif" ,   "Hitbox_Wrench.png" ,        "4.gif" ,      "Hitbox_Drill.png" , "Hitbox_Pliers.png" ,       "4.gif" ,        "1.gif"  ,         "6.gif" ,       "6.gif" ,       "3.gif" ,        "3.gif" ,    "Hitbox_L_Curtain.png" , "Hitbox_Top_Curtain.png" , "Hitbox_R_Curtain.png" , "Hitbox_Top_Curtain.png" , "7.gif" ,     "4.gif" ,       "4.gif" ,       "7.gif" ,        "7.gif" ,           "6.gif" ,       "6.gif" ,       "6.gif" ,      "5.gif" ,       "3.gif" ,       "3.gif" ,       "1.gif" ,  "Hitbox_Bed.png"]
Positions_Platform = [  [-115, 391],  [-31, 391],        [-15, 328] ,     [80, 318]  ,                [253, 372],           [380, 391],  [401, 327],  [375, 267],    [72, 129] ,             [412, 99] ,            [150, 148] ,         [304, 141] ,           [618, 99]  ,  [594, 266] ,          [618, 329] ,      [618, 393] ,   [746, 329] ,  [746, 393] ,      [853, 146] ,           [853, 136] ,               [1097, 146] ,                [853, 336] ,         [1260, 176] , [1388, 35] , [1624, 35] ,        [1752, 176] ,    [1816, 176] ,       [1420, 328] , [1420, 392] , [1752, 392] ,      [1420, 266] ,     [1356, 328] , [1356, 393] ,   [1989, 391] , [2056, 352] ]

Names_Interactable =  [  "StopWatch",       "HoneyTrap",    "ToyChest"      ]
Positions_Interactable = [   [130, 260],  [665, 290],    [2185, 260]     ]

StartPos_Player = [-190, 445]  # pos of the slinky's bottom midpoint
Pos_GameStatus = [320, 200]
Origin_Local[:] = [StartPos_Player[0]-Size_Screen[0]//2, StartPos_Player[1]-3*Size_Screen[1]//4]
StartPos_Chaser = [Origin_Local[0] + 250, Origin_Local[1] + 250]



def globalToLocal(coord_global):
    return [coord_global[0] - Origin_Local[0], coord_global[1] - Origin_Local[1]]


def localToGlobal(coord_local):
    return [coord_local[0] + Origin_Local[0], coord_local[1] + Origin_Local[1]]




class PureImage(pg.sprite.Sprite):
    images = []

    def __init__(self):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.pos = [0, 0]
        self.type = 0

    def update(self):
        if self.type != 0:
            local_coord = globalToLocal(self.pos)
            self.rect = pg.Rect(local_coord[0], local_coord[1], self.rect[2], self.rect[3])


class Platform(pg.sprite.Sprite):
    images = []
    imagesGetHIt = []

    def __init__(self):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.imageGetHit = self.imagesGetHit[0]
        self.rect = self.image.get_rect()
        self.pos = [0, 0]
        self.size = [0, 0]
        self.box = []
        self.boxes = []
        self.angle_boxes = []
        self.health_max = 4
        self.health_cur = self.health_max

    def setPos(self, left, top):
        self.pos[0], self.pos[1] = left, top
        self.rect = self.image.get_rect()
        self.size[:] = self.rect[2:4]

    def setBoxes(self):
        l = self.pos[0]
        t = self.pos[1]
        w = self.size[0]
        h = self.size[1]
        thickness = 10
        self.box = [[l, t], [l+w, t+h]]
        self.boxes.append([[l, t-thickness], [l+w, t]])
        self.boxes.append([[l, t+h], [l+w, t+h+thickness]])
        self.boxes.append([[l-thickness, t], [l, t+h]])
        self.boxes.append([[l+w, t], [l+w+thickness, t+h]])
        self.angle_boxes = [0, 180, 90, 270]        
    
    def getHit(self):
        self.health_cur -= 1
        if self.health_cur == self.health_max // 2:
            self.image = self.imageGetHit
        if self.health_cur == 0:
            self.image = pg.transform.scale(utils.load_image("fire.png"), self.size)

    def update(self):
        if self.health_cur <= 0 and random.random() > 0.75:
            self.image = pg.transform.flip(self.image, 1, 0)
        local_coord = globalToLocal(self.pos)
        self.rect = pg.Rect(local_coord[0], local_coord[1], self.size[0], self.size[1])
    


class Interactable(pg.sprite.Sprite):
    images = []
    player = None
    chaser = None
    
    def __init__(self, ind_reaction_):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.image_backup = None
        self.transparent = False
        self.rect = self.image.get_rect()
        self.pos = [0, 0]
        self.size = [self.rect[2], self.rect[3]]
        self.box = []
        self.ind_reaction = ind_reaction_
        self.life_time = None
        self.enable = False
    
    def react(self):  # 0 honey 1 honey_ 2 stopwatch 3 destination
        # TODO play some sound effect
        self.enable = True
        self.image_backup = self.image
        if self.ind_reaction == 0 or self.ind_reaction == 1:
            self.life_time = FPS * Time_Player_Stuck
            self.player.beingStuck = True
        elif self.ind_reaction == 2:
            self.life_time = FPS * Time_Chaser_Frozen
            self.chaser.frozen = True
        elif self.ind_reaction == 3:
            self.life_time = 9999999999999
            self.player.pos_top = [self.pos[0] + 32, self.pos[1]+32]
            GameWin[0] = True

    def setPos(self, left, top):
        self.pos[0], self.pos[1] = left, top
        self.rect = self.image.get_rect()
        self.size[:] = self.rect[2:4]
        self.setBox()

    def setBox(self):
        l = self.pos[0]
        t = self.pos[1]
        w = self.size[0]
        h = self.size[1]  
        self.box = [[l, t], [l+w, t+h]]        
    
    def update(self):
        if self.enable:
            self.life_time -= 1
            if self.ind_reaction == 2 and self.life_time % 10 == 0:
                self.image = self.image_backup if not self.transparent else self.images[4]
                self.transparent = not self.transparent
            if self.life_time <= 0:
                self.enable = False
                self.kill()
        local_coord = globalToLocal(self.pos)
        self.rect = pg.Rect(local_coord[0], local_coord[1], self.size[0], self.size[1])


class Player(pg.sprite.Sprite):   
    images = []  # class static variable
    sfx = []

    def __init__(self):   # instance variable!
        pg.sprite.Sprite.__init__(self, self.containers)
        self.angle = 0
        self.image = self.assignImage(self.images[0])
        self.rect = self.image.get_rect()
        self.size = [self.image.get_rect().width, self.image.get_rect().height]
        self.pos_bottom = [StartPos_Player[0], StartPos_Player[1]]
        self.pos_top = [self.pos_bottom[0], self.pos_bottom[1]-Len_StaticSlinky]
        self.markPoint = None
        self.shift_dst = [0, 0]
        self.shift_dir = [1, 1]
        self.beingHold = False
        self.beingStuck = False
        self.stuck_frame = 0
        # self.getPower = False
        # self.power_frame = 0
        self.platform = None
    
    def getTop(self):
        x = 0
        y = Len_StaticSlinky
        cos_theta = round(math.cos(self.angle * alg.Multiplier_AngleToRad))
        sin_theta = round(math.sin(self.angle * alg.Multiplier_AngleToRad))
        x_ =  cos_theta * x - sin_theta * y
        y_ =  sin_theta * x + cos_theta * y
        return [self.pos_bottom[0] + x_, self.pos_bottom[1] - y_]

    def getStandardXY(self, x, y):        
        if self.angle < 0 or self.angle > 360:
            print("Error: angele out of range")
            exit()
        cos_theta = round(math.cos(self.angle * alg.Multiplier_AngleToRad))
        sin_theta = round(math.sin(self.angle * alg.Multiplier_AngleToRad))
        x_ =  cos_theta * x + sin_theta * y
        y_ =  -sin_theta * x + cos_theta * y
        return x_, y_

    def assignImage(self, image):
        return pg.transform.rotate(image, self.angle)

    def release(self, land=False):
        if not land and not self.beingStuck:
            self.sfx[0].play()
        self.image = self.assignImage(self.images[0])
        self.pos_top = self.getTop()
        self.markPoint.pos = self.pos_top[:]
        self.markPoint.adjustImage(self.angle)
        self.beingHold = False

    def drag(self, coord_mouse): 
        coord_mouse = localToGlobal(coord_mouse)
        if self.beingStuck or alg.e_dst(self.pos_top, coord_mouse) > LeastDst_DragPlayer :  # if the mouse was too far from the top-end, then the slinky couldn't be dragged
            return
        if not self.beingHold:  # if it was the first mouse click on slinky and the mouse was in the range of any collider box, then do nothing
            for p in Instances_platform:
                for box in p.boxes:
                    if alg.intersected_PointBox(coord_mouse, box):
                        self.release()
                        return
        x, y = self.getStandardXY(coord_mouse[0] - self.pos_bottom[0],  -coord_mouse[1] + self.pos_bottom[1])
        euler_distance = math.sqrt(abs(x)**2 + abs(y)**2)
        if euler_distance > Longest_StretchDst:  # get the top-end back
            self.release()
        else:
            self.beingHold = True
            self.pos_top = coord_mouse[:] 
            # TODO Apply the image according to (x, y)   which is the relative distance
            x_to_scale = round(abs(x)//3)
            # y_to_scale = round(abs(y)//8)
            # img = self.images[min(19+y_to_scale, 24)] if y < 0 else self.images[min(x_to_scale, 18)]
            img = self.images[min(x_to_scale, 16)]
            if x > 0:
                dir_markPoint = 1
                self.image = self.assignImage(img)
            else:
                dir_markPoint = 0
                self.image = self.assignImage(pg.transform.flip(img, 1, 0))
            self.markPoint.pos = self.pos_top[:]
            self.markPoint.adjustImage(self.angle, dir_markPoint)
            for item in Instances_interactable:
                if alg.intersected_PointBox(self.pos_top, item.box):
                    item.react()
                    Instances_interactable.remove(item)
            for p in Instances_platform:
                for i in range(len(p.boxes)):
                    if alg.intersected_PointBox(self.pos_top, p.boxes[i]):
                        if p.health_cur <= 0:
                            GameOver[0] = True
                            return
                        if alg.e_dst(self.pos_bottom, self.pos_top) < LeastDst_LandPlayer:  # if landpoint too close to bottom, then don't move
                            self.release()
                            return
                        self.platform = p
                        self.angle = p.angle_boxes[i]
                        self.land()
                        return
            
        
    def land(self):
        # print("Slinky lands on a new point!")
        self.sfx[1].play()
        bias = 5
        if self.angle == 0:
            self.pos_top[1] += bias
        elif self.angle == 180:
            self.pos_top[1] -= bias
        elif self.angle == 90:
            self.pos_top[0] += bias
        elif self.angle == 270:
            self.pos_top[0] -= bias
        self.shift_dst[0], self.shift_dst[1] = abs(self.pos_top[0] - self.pos_bottom[0]), abs(self.pos_top[1] - self.pos_bottom[1])
        self.shift_dir[0] = 1 if (self.pos_top[0] - self.pos_bottom[0]) > 0 else -1
        self.shift_dir[1] = 1 if (self.pos_top[1] - self.pos_bottom[1]) > 0 else -1
        self.pos_bottom = self.pos_top[:]
        self.release(land=True)

    def getStuck(self):
        self.markPoint.inTrouble = True
        f = round(Time_Player_Stuck * FPS)
        self.stuck_frame += 1
        if f == self.stuck_frame:
            self.release()
            self.stuck_frame = 0
            self.beingStuck = False
            self.markPoint.inTrouble = False
    
    # def PowerCountDown(self):
    #     self.power_frame += 1
    #     f = round(Time_PlayerGetPower * FPS)
    #     if f == self.power_frame:
    #         self.power_frame = 0
    #         self.getPower = False


    def update(self):
        if GameWin[0]:
            self.pos_bottom = self.pos_top[:]
        if self.platform != None and self.platform.health_cur <= 0:
            GameOver[0] = True
        if self.shift_dst[0] > 0 or self.shift_dst[1] > 0:
            for i in range(2):
                s = Speed_Camera if self.shift_dst[i] > Speed_Camera else self.shift_dst[i]
                Origin_Local[i] += s if self.shift_dir[i] > 0 else -s
                self.shift_dst[i] -= s
        if self.beingStuck:
            self.getStuck()
        # if self.getPower:
        #     self.PowerCountDown()
        self.markPoint.pos = self.pos_top[:]
        local_coord = globalToLocal(self.pos_bottom)
        self.rect = pg.Rect(local_coord[0]-self.size[0]//2, local_coord[1]-self.size[1]//2, self.rect[2], self.rect[3])
        

class MarkPoint(pg.sprite.Sprite):
    images = []
    imagesStuck = []

    def __init__(self):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.pos = [0, 0]
        self.size = [self.rect[2], self.rect[3]]
        self.cycle_stuck = 2
        self.ind_cycle_stuck = 0
        self.cnt_stuck = 0
        self.inTrouble = False

    def adjustImage(self, angle, dir=0):
        self.image = pg.transform.rotate(pg.transform.flip(self.images[0], dir, 0), angle)

    def getIntoTrouble(self):
        self.cnt_stuck += 1
        if self.cnt_stuck == 5:
            self.cnt_stuck = 0
            self.ind_cycle_stuck = (self.ind_cycle_stuck + 1) % self.cycle_stuck
            self.image = self.imagesStuck[self.ind_cycle_stuck]
        
    def update(self):
        local_coord = globalToLocal(self.pos)
        if GameWin[0]:
            self.image = pg.transform.scale(utils.load_image("happy face.png"), [70, 70])
        if GameOver[0] or self.inTrouble:
            self.getIntoTrouble()
            self.rect = pg.Rect(local_coord[0]-70, local_coord[1]-70, self.rect[2], self.rect[3])
        else:
            self.rect = pg.Rect(local_coord[0]-self.size[0]//2, local_coord[1]-self.size[1]//2, self.rect[2], self.rect[3])


class Chaser(pg.sprite.Sprite):
    images = []
    
    def __init__(self):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.pos = StartPos_Chaser[:]
        self.size = [self.rect[2], self.rect[3]]
        self.cycle = len(self.images)
        self.index_in_cycle = 0
        self.frame_cnt = 0
        self.prey = None
        self.just_hit_platform = False
        self.frozen = False
        self.frozen_frame = 0

    def chase(self):
        if GameOver[0] or GameReady[0] or GameWin[0]:
            return
        potential_move = [0, 0]
        for i in range(2):
            if self.prey.pos_bottom[i] - self.pos[i] > 0:
                potential_move[i] = Step_ChaserForward
            elif self.prey.pos_bottom[i] - self.pos[i] < 0:
                potential_move[i] = -Step_ChaserForward
        if self.just_hit_platform:
            self.pos[0] -= Step_ChaserBackward * 1 if potential_move[0] > 0 else -1
            self.pos[1] -= Step_ChaserBackward * 1 if potential_move[1] > 0 else -1
            self.just_hit_platform = False
        else:
            f = round(Time_ChaserMove * FPS)
            if self.frame_cnt % f == 0: 
                self.pos[0] += potential_move[0]
                self.pos[1] += potential_move[1]
            edge_shortened = 20
            box = [[self.pos[0]-self.size[0]//2+edge_shortened, self.pos[1]-self.size[1]//2+edge_shortened], 
                   [self.pos[0]+self.size[0]//2-edge_shortened, self.pos[1]+self.size[1]//2-edge_shortened]]
            if alg.intersected_PointBox(self.prey.pos_bottom, box) or alg.intersected_PointBox(self.prey.pos_top, box):
                GameOver[0] = True
            for p in Instances_platform:
                if p.health_cur > 0 and alg.intersected_BoxBox(box, p.box):
                    self.just_hit_platform = True
                    p.getHit()
                    return
            for item in Instances_interactable:
                if alg.intersected_BoxBox(box, item.box):
                    item.kill()

    def getFrozen(self):
        self.image = pg.transform.scale(utils.load_image("cat_frozen.png"), Size_ChaserImage)
        f = round(Time_Chaser_Frozen * FPS)
        self.frozen_frame += 1
        if f == self.frozen_frame:
            self.frozen_frame = 0
            self.frozen = False
            
    def update(self):
        if not self.frozen:
            self.frame_cnt += 1
            f = round(Time_ChaserFramePlay * FPS)
            if self.frame_cnt % f == 0:
                self.index_in_cycle = (self.index_in_cycle + 1) % 3
                self.image = self.images[self.index_in_cycle]
            self.chase()
        else:
            self.getFrozen()
        local_coord = globalToLocal(self.pos)
        self.rect = pg.Rect(local_coord[0]-self.size[0]//2, local_coord[1]-self.size[1]//2, self.rect[2], self.rect[3])


# class Timer():
#     player = None

#     def __init__(self):
#         self.frame_count = 0
#         self.minutes = 0
#         self.seconds = 0
#         self.total_seconds = 0
#         # initialize fonts
#         self.font = pg.font.Font(None, 50)
#         # self.font = None

#     def timerDisplay(self):
#         self.minutes = self.total_seconds // 60
#         self.seconds = self.total_seconds % 60
#         output_string = "Time: {0:02}:{1:02}".format(self.minutes, self.seconds)
#         score_output_string = "Score: {0:04}".format(round(self.total_seconds*5 + alg.e_dst(self.player.pos_bottom, StartPos_Player)//10))
#         text = self.font.render(output_string, True, (255, 51, 51))
#         score_text = self.font.render(score_output_string, True, (51, 51, 255))
#         # return text
#         screen.blit(text, (50, 50))
#         screen.blit(score_text, (750, 50))

#     def timerUpdate(self):
#         self.total_seconds = self.frame_count // FPS
#         self.frame_count += 1


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
    if pg.mixer and not pg.mixer.get_init():
        print("Warning, no sound")
        pg.mixer = None

    fullscreen = False
    # Set the display mode
    winstyle = 0  # |FULLSCREEN
    bestdepth = pg.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pg.display.set_mode(SCREENRECT.size, winstyle, bestdepth)

    # Load images, assign to sprite classes
    # (do this before the classes are used, after screen setup)
    PureImage.images = [utils.load_image(im) for im in ["ready.png", "over.png", "win.png", "transparent.png"]]
    for i in range(len(PureImage.images)):
        PureImage.images[i] = pg.transform.scale(PureImage.images[i], Size_GameStatusImage)
    PureImage.images.append(pg.transform.scale(utils.load_image("Final_Background.png"), Size_LongBackground))

    filesToBeLoaded = []
    for ind in range(1, 18):
        filesToBeLoaded.append("slinky (" + str(ind) + ").png")
    Player.images = [utils.load_image(im) for im in filesToBeLoaded]
    for i in range(len(Player.images)):
        Player.images[i] = pg.transform.scale(Player.images[i], Size_PlayerImage)
    
    filesToBeLoaded = []
    for i in range(len(Imagefiles_item)):
        filesToBeLoaded.append(Imagefiles_item[i])
    Platform.images = [utils.load_image(im) for im in filesToBeLoaded]
    Platform.imagesGetHit = [utils.load_image(str(im) + "_.png") for im in range(1, 8)]

    MarkPoint.images = [utils.load_image("eyes.png")]
    MarkPoint.imagesStuck = [utils.load_image("eyes_0.png"), utils.load_image("eyes_1.png")]

    Chaser.images = [utils.load_image(im) for im in ["cat (1).png", "cat (2).png", "cat (3).png"]]
    for i in range(len(Chaser.images)):
        Chaser.images[i] = pg.transform.scale(Chaser.images[i], Size_ChaserImage)

    Interactable.images = [utils.load_image(im) for im in ["honeytrap.png", "honeytrap_.png", "stopwatch.png", "toy chest.png", "transparent.png"]]
    Interactable.images[0] = pg.transform.scale(Interactable.images[0], [100, 70])
    Interactable.images[1] = pg.transform.scale(Interactable.images[1], [70, 100])
    Interactable.images[2] = pg.transform.scale(Interactable.images[2], [64, 64])
    Interactable.images[3] = pg.transform.scale(Interactable.images[3], [90, 90])
    
    # decorate the game window
    icon = pg.transform.scale(utils.load_image("icon.jpg"), (32, 32))
    pg.display.set_icon(icon)
    pg.display.set_caption("Slinky Game")
    
    # if PlayIntro:
    #     clip = VideoFileClip(main_dir + "\\data\\SLINKY INTRO.wmv")
    #     clip.preview()
    
    # create the background, tile the bgd image
    bgdtile = utils.load_image(ImgName_bg)
    background = pg.Surface(SCREENRECT.size)
    for y in range(0, SCREENRECT.height, bgdtile.get_height()):
        for x in range(y, SCREENRECT.width, bgdtile.get_width()):
            background.blit(bgdtile, (x, 0))
    screen.blit(background, (0, 0))
    pg.display.flip()

    # load the sound effects
    if pg.mixer:
        music_file = os.path.join(main_dir, "data",  MusicName_bg)
        pg.mixer.music.load(music_file)
        pg.mixer.music.play(-1)
    sfx_player = [utils.load_sound("slinky_back.wav"), utils.load_sound("slinky_land.wav")]

    # Initialize Game Groups
    # all = pg.sprite.RenderUpdates()
    all = pg.sprite.OrderedUpdates()
    
    # assign default groups to each sprite class
    PureImage.containers = all
    Platform.containers = all
    Player.containers = all
    MarkPoint.containers = all
    Chaser.containers = all
    Interactable.containers = all

    # Create Some Starting Values
    clock = pg.time.Clock()

    # Initialize Instances
    dct = {}
    index = 0
    for name in Imagefiles_item:
        dct[name] = index
        index += 1
    dct["HoneyTrap"] = 0
    dct["HoneyTrap_"] = 1
    dct["StopWatch"] = 2
    dct["ToyChest"] = 3
        
    for round in range(100):
        long_background = PureImage()
        long_background.type = 1
        long_background.image = PureImage.images[4]
        long_background.rect = long_background.image.get_rect()
        flag = True
        player = Player()
        # timer = Timer()
        # timer.player = player
        player.sfx = sfx_player
        for i in range(len(Names_Platform)):
            Instances_platform.append(Platform()) 
            ind = dct[Names_Platform[i]]
            Instances_platform[i].image = Platform.images[ind]
            if ind < len(Platform.imagesGetHit):
                Instances_platform[i].imageGetHit = Platform.imagesGetHit[ind]
            else:
                Instances_platform[i].imageGetHit = Instances_platform[i].image
            Instances_platform[i].setPos(Positions_Platform[i][0], Positions_Platform[i][1])
            Instances_platform[i].setBoxes()       

        for i in range(len(Names_Interactable)):
            ind = dct[Names_Interactable[i]]
            Instances_interactable.append(Interactable(ind))        
            Instances_interactable[i].image = Interactable.images[ind]
            Instances_interactable[i].setPos(Positions_Interactable[i][0], Positions_Interactable[i][1]) 
        
        markPoint = MarkPoint()
        player.markPoint = markPoint

        cat = Chaser()
        cat.prey = player

        gameStatusDisplay = PureImage()
        gameStatusDisplay.rect = pg.Rect(Pos_GameStatus[0], Pos_GameStatus[1], Size_GameStatusImage[0], Size_GameStatusImage[1])
        Interactable.player = player
        Interactable.chaser = cat

        # Run our main loop whilst the player is alive.
        while flag and player.alive():
            for event in pg.event.get():
                if GameReady[0]:
                    gameStatusDisplay.image = PureImage.images[0]
                    if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                        GameReady[0] = False
                        gameStatusDisplay.image = PureImage.images[3]
                    break
                if GameOver[0] or GameWin[0]:
                    gameStatusDisplay.image = PureImage.images[1] if GameOver[0] else PureImage.images[2]
                    if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                        GameReady[0] = True
                        GameOver[0] = False
                        GameWin[0] = False
                        Origin_Local[:] = [StartPos_Player[0]-Size_Screen[0]//2, StartPos_Player[1]-3*Size_Screen[1]//4]
                        player.kill()
                        markPoint.kill()
                        cat.kill()
                        for p in Instances_platform:
                            p.kill()
                        Instances_platform.clear()
                        for item in Instances_interactable:
                            item.kill()
                        Instances_interactable.clear()
                        gameStatusDisplay.kill()
                        flag = False
                    break

                # get mouse input:
                mouse_1_hold = pg.mouse.get_pressed(3)[0]
                if mouse_1_hold:
                    player.drag(pg.mouse.get_pos())
                elif player.beingHold and not player.beingStuck:
                    player.release()

                # get key input
                if event.type == pg.QUIT:
                    return
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    return

            # clear/erase the last drawn sprites
            all.clear(screen, background)

            # update all the sprites
            all.update()

            # draw the scene
            # if not GameReady[0] and not GameOver[0] and not GameWin[0]:
            #     timer.timerUpdate()
            screen.blit(background, (0,0))
            dirty = all.draw(screen)  # can't be deleted!
            # timer.timerDisplay()
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
