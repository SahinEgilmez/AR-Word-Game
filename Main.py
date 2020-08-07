#!/usr/bin/env python
# coding: utf8
'''
    Author: Şahin Eğilmez <segilmez@outlook.com>
'''

from Game import *  # Import game and faces
from Library import *  # Import constants, helper functions and using libraries

from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.lang import Builder
from kivy.uix.camera import Camera
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics.texture import Texture
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.graphics import Rectangle


class MenuScreen(Screen):  # menu screen of game
    def pressBoxes1(self, btn, player, box):  # choose player numaber of team
        ARCamera.game.setPlayer(player)
        btn.line_width = 5
        for child in box.children:
            if btn.name is not child.name:
                child.line_width = 0.1

    def pressBoxes2(self, btn, minute, box):  # choose game time
        print(minute*60)
        ARCamera.game.time = minute*60
        btn.line_width = 5
        for child in box.children:
            if btn.name is not child.name:
                child.line_width = 0.1

    def pressPlay(self):  # press play button and show game screen
        ARApp.sm.current = 'gamescreen'


class ARCamera(Image):  # main class for rendering frame by frame
    game = Game()  # onky one game object all time
    current_time = 0
    img = None
    order_true_counter = 30

    def __init__(self, capture,  fps, **kwargs):
        super(ARCamera, self).__init__(**kwargs)
        self.capture = capture
        self.game.setCapture(self.capture)
        self.current_time = time.time()

    def update(self, dt):  # render each frame
        if(self.game.time <= 0):
            self.dispose()
            self.game_over()
            return
        if(time.time() - self.current_time >= 1):
            self.game.time += -1
            self.current_time = time.time()
        if(self.game.ORDER_FLAG is True):
            if(self.order_true_counter > 0):
                self.order_true_counter -= 1
                self.img = self.game.drawQuestion("BRAVO DOĞRU BİLDİNİZ :)", HEIGHT, WIDTH)
            else:
                self.game.ORDER_FLAG = False
                self.order_true_counter = 30
        else:
            self.img = self.game.render()
        # convert it to texture
        self.img = cv2.resize(self.img, (Window.width, Window.height))
        buf1 = cv2.flip(self.img, 0)
        buf = buf1.tostring()
        image_texture = Texture.create(
            size=(self.img.shape[1], self.img.shape[0]), colorfmt='bgr')
        image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        # display image from the texture
        self.texture = image_texture
        ARApp.sm.current_screen.canvas.get_group('rect')[0].texture = self.texture

    def dispose(self):  # dispose object for exit
        Clock.unschedule(self.update)
        self.capture.release()
        self.game.dispose()

    def game_over(self):  # game over state and show result screen
        ARApp.sm.current = 'resultscreen'
        ARApp.sm.get_screen('resultscreen').printScore()


class GameScreen(Screen):  # game screen
    capture = cv2.VideoCapture(0)  # video capture from webcam

    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        if(not self.capture.isOpened()):
            self.capture = cv2.VideoCapture(0)
        self.my_camera = ARCamera(self.capture, 20)

    def on_enter(self):  # schedule ARCamera.update function for 30 fps
        Clock.schedule_interval(self.my_camera.update, 1.0 / 30)
        return self.my_camera

    def on_stop(self):  # stop and dispose ARCamera
        # without this, app will not exit even if the window is closed
        self.my_camera.dispose()


class ResultScreen(Screen):  # show results
    score = 0

    def __init__(self, **kwargs):
        super(ResultScreen, self).__init__(**kwargs)

    def printScore(self):  # print score to screen
        self.score_label.text = str("TAM %d SORU BİLDİNİZ" % (int(ARApp.sm.get_screen('gamescreen').my_camera.game.LEVEL) - 1))

    def back_to_menu(self):  # press 'MENÜYE DÖN' button and show menu screen again
        ARApp.sm.current = 'menuscreen'
        ARApp.sm.remove_widget(ARApp.sm.get_screen(name='gamescreen'))
        ARApp.sm.remove_widget(ARApp.sm.get_screen(name='resultscreen'))
        ARApp.sm.add_widget(GameScreen(name='gamescreen'))
        ARApp.sm.add_widget(ResultScreen(name='resultscreen'))
        ARCamera.game.time = 60

    def exit_game(self):  # press 'OYUNU KAPAT' button and close the game
        App.get_running_app().stop()


class ARApp(App):  # kivy App for game. Also sync to ar.kv file
    sm = ScreenManager(transition=FadeTransition())
    score = 0

    def build(self):  # create screen and return screen manager
        self.sm.add_widget(MenuScreen(name='menuscreen'))
        self.sm.add_widget(GameScreen(name='gamescreen'))
        self.sm.add_widget(ResultScreen(name='resultscreen'))
        self.score = 0
        self.sm.current = 'menuscreen'
        setattr(Window, 'fullscreen', "auto")
        return self.sm


if __name__ == '__main__':  # main function
    Builder.load_file('./assets/ar.kv')
    ARApp().run()
