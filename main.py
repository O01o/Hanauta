import enum
from kivy.app import App
from kivy.lang import Builder

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.behaviors import ToggleButtonBehavior

from kivy.core.audio import SoundLoader

from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty, ListProperty, NumericProperty, BooleanProperty
from kivy.factory import Factory
from kivy.uix.popup import Popup

from kivy.clock import Clock

from kivy.core.window import Window

from kivy.config import Config
from kivy.utils import DEPRECATED_CALLERS
Config.set("graphics", "resizable", False)
Config.set("graphics", "width", 600)
Config.set("graphics", "height", 480)

import time
from concurrent.futures import ThreadPoolExecutor

import threading

import os

import pyaudio
import subprocess
import wave
import sys
sys.path

import librosa

import mido
from mido import Message, MidiFile, MidiTrack, MetaMessage


# Audio Recording Init Instance
# --------------------------------------------------------
audio = pyaudio.PyAudio()
stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
frames = []
filepath_wav = 'wavfiles'

if not os.path.isdir(filepath_wav):
    os.mkdir(filepath_wav)

FILE_NAME = './test.wav'  # 保存するファイル名
sample_rate = 44100  # サンプリング周波数

Window.size = [360,640]

# --------------------------------------------------------

# Create both screens. Please note the root.manager.current: this is how
# you can control the ScreenManager from kv. Each screen has by default a
# property manager that gives you the instance of the ScreenManager used.
Builder.load_file('ui.kv')

# Declare both screens
class MenuScreen(Screen):
    pass

class RecordingScreen(Screen):
    flag = False
    text = StringProperty()
    color = ListProperty([0.5, 0.5, 0.5, 1.0])

    def __init__(self, **kwargs):
        super(RecordingScreen, self).__init__(**kwargs)
        self.text = '録音する'

    def onClickRecordingButton(self):
        self.flag = not self.flag
        print('Toggle Changed to', self.flag,'!')
        if self.flag == True:
            self.text = '録音中'
            self.color = [1.0, 0.3, 0.3, 1.0]

            # マルチスレッドを展開して、
            # 録音の状態を無限ループでストリーミングする処理をここに記述する
            rs_thread = threading.Thread(target=self.recordStreaming, args=("rs",))
            rs_thread.start()

        else:
            self.text = 'もう一度録音する'
            self.color = [0.5, 0.5, 0.5, 1.0]

            # サブスレッド内の無限ループを終了。.wavファイルとして保存。
            # ダイアログを展開する。(選択肢)⇒ 録音をやり直す(wavファイルの破棄), 
            # メニューに戻る, 続行する
            # なお、このダイアログ発生時に自分の声を聞き取れるボタンを用意する。
    
    def recordStreaming(self):
        while self.flag:
            data = stream.read(1024)
            frames.append(data)
            print("getting")

        stream.stop_stream()
        stream.close()
        audio.terminate()

        # wavファイルのパスが無い場合にディレクトリを作成する
        # if True:
        #     os.mkdir(filepath_wav)

        sound_file = wave.open("Recorded.wav", "wb")
        sound_file.setnchannels(1)
        sound_file.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        sound_file.setframerate(16000)
        sound_file.writeframes(b''.join(frames))
        sound_file.close()
        print("file writed!")


class WavListScreen(Screen):
    flag = True
    flag2 = True
    filetext = StringProperty()
    playtext = StringProperty()
    freq = NumericProperty()
    disabled = BooleanProperty()
    
    color = ListProperty([0.5, 0.5, 0.5, 1.0])
    color2 = ListProperty([0.5, 0.5, 0.5, 1.0])

    sound = SoundLoader.load('')
    tik = SoundLoader.load('clock_cut.wav')

    def __init__(self, **kwargs):
        super(WavListScreen, self).__init__(**kwargs)
        self.filetext = 'wavfile?'
        self.playtext = 'play'
        self.freq = 80
        self.disabled = False

    def selected(self, filename):
        self.sound = SoundLoader.load(filename[0])
        self.filetext = filename[0]

    def onClickPlayButton(self):
        print('PlayToggle Changed to', self.flag,'!')

        if self.flag == True:
            if self.sound:
                self.playtext = 'stop'
                self.color = [1.0, 0.3, 0.3, 1.0]
                self.sound.play()
            else:
                self.playtext = 'file not found...'
                self.flag = not self.flag
        else:
            self.playtext = 'play'
            self.color = [0.5, 0.5, 0.5, 1.0]
            if self.sound:
                self.sound.stop()

        self.flag = not self.flag
        
    
    def tiktak(self, *args):
        if self.tik:
            self.tik.play()
        
        
    def onClickClockButton(self):
        print('PlayToggle Changed to', self.flag,'!')

        if self.flag2 == True:
            self.color2 = [1.0, 0.3, 0.3, 1.0]
            self.event = Clock.schedule_interval(self.tiktak, 60/self.freq)
        else:
            self.color2 = [0.5, 0.5, 0.5, 1.0]
            self.event.cancel()
            
        # self.disabled = not self.disabled
        self.flag2 = not self.flag2
        
    
    def onClickConvertButton(self):
        if self.sound:
            '''
            Convert Wave to Chromagram with Librosa
            '''
            
            
            '''
            Save Midi with Mido
            '''
            mid = MidiFile()
            track = MidiTrack()
            mid.tracks.append(track)
            track.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(120)))
            track.append(Message('note_on', note=64, velocity=127, time=0))
            track.append(Message('note_off', note=64, time=480))

            mid.save('new_song.mid')
            
        else:
            self.playtext = 'file not found...'




class MidiListScreen(Screen):
    pass



class Wav2MidiScreen(Screen):
    is_velocity = False
    tempo_list = [45, 60, 80, 100, 120, 135, 150, 180]
    division_list = [8, 12, 16, 24, 32]
    clockdelay_list = [32, 24, 16, 12, 8]
    




class TestApp(App):

    def build(self):
        # Create the screen manager
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(RecordingScreen(name='recording'))
        sm.add_widget(WavListScreen(name='wav_list'))
        sm.add_widget(MidiListScreen(name='midi_list'))
        sm.add_widget(Wav2MidiScreen(name='wav2midi'))

        return sm


if __name__ == '__main__':
    TestApp().run()