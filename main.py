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

import math
import numpy as np
import scipy as sp
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

SAMPLE_RATE = 8000


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
    converttext = StringProperty()
    hop_length = NumericProperty() # 1フレーム出力あたりに必要なサンプル量
    disabled = BooleanProperty()
    # tempo_list = [30, 36, 40, 45, 50, 60, 72, 75, 90, 100, 120, 125, 150, 180, 200, 225, 300]
    tempo = NumericProperty() # 音のテンポ
    # tempo_index = NumericProperty(64) # old: 100
    tempo_index = NumericProperty(100)
    # 30 < tempo < 250
    # x0, 1, 2, 3, 4, 5, 6, 7, 8, 9
    tempo_index_list = np.array([
        # 0,   1,   2,   3,   4,   5,   6,   7,   8,   9
        250,242, 234, 227, 221, 214, 208, 203, 197, 192,
        188, 183, 179, 174, 170, 167, 163, 160, 156, 153,
        150, 147, 144, 142, 139, 136, 134, 132, 129, 127,
        125, 123, 121, 119, 117, 115, 114, 112, 110, 109,
        
        107, 105, 103, 101,100,98,97,96,95,
        94,93,92,91,90,89,87,86,85,84,83,82,81,80,
        79,78,77,76,75,74,73,72,71,70,
        69,68,67,66,65,64,63,62,61,60,
        59,58,57,56,55,54,53,52,51,50,
        49,48,47,46,45,44,43,42,41,40,
        39,38,37,36,35,34,33,32,31,30
    ])
    print("tempos_index_list length:", len(tempo_index_list))
    print("index list type:", type(tempo_index_list[40]))
    print(type(hop_length))
    
    color = ListProperty([0.5, 0.5, 0.5, 1.0])
    color2 = ListProperty([0.5, 0.5, 0.5, 1.0])
    color3 = ListProperty([0.5, 0.5, 0.5, 1.0])

    sound = SoundLoader.load('')
    tik = SoundLoader.load('clock_cut.wav')

    def __init__(self, **kwargs):
        super(WavListScreen, self).__init__(**kwargs)
        self.filetext = 'wavfile?'
        self.playtext = 'play'
        self.converttext = 'WAV2MIDI変換'
        # self.hop_length = 16 * self.tempo_index_list[self.tempo_index]
        self.hop_length = 16 * self.tempo_index
        self.tempo = round(abs(SAMPLE_RATE * 15 / self.hop_length), 2)
        self.disabled = False
        
        

    def selected(self, filename):
        try:
            self.sound = SoundLoader.load(filename[0])
            self.filetext = filename[0]
        except IndexError:
            pass
    
    def onClickPlusMinusButton(self, num):          
        self.tempo_index -= num
        # self.hop_length = 16 * self.tempo_index_list[self.tempo_index]
        self.hop_length = 16 * self.tempo_index
        self.tempo = round(abs(SAMPLE_RATE * 15 / self.hop_length), 2)
        # print(self.tempo_index, self.tempo_index_list[self.tempo], self.tempo)
        print(self.tempo_index, self.tempo_index_list[self.tempo_index], self.tempo)

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
            self.event = Clock.schedule_interval(self.tiktak, 60/self.tempo)
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
            # 変換中はボタンの色とテキストを変換させておく
            self.converttext = '変換中'
            self.color3 = [0.3, 1.0, 0.3, 1.0]
            
            y, sr = librosa.load(self.filetext, sr=SAMPLE_RATE)
            # 各パラメータの値の設定
            # hop_length は5オクターブの場合だと16の整数倍である必要があるらしいです！
            hop_length = self.hop_length # CQTのサンプル数(ここがクロックの速さに応じて可変になる)(デフォルト値は512)(計算方法は紙の計算式にて)           
            fmin = librosa.note_to_hz('C1') # 最低音階
            bins_per_octave = 12 # 1オクターブ12音階
            octaves = 5 # オクターブ数
            n_bins = bins_per_octave * octaves # 音階の個数
            window = 'hamming' # 窓関数のモデル(今回はハミング窓。ハン窓('hann')や三角窓('triang')もあり
            print('hop_length: ', hop_length)
            
            chroma_cqt = np.abs(librosa.cqt(
                y, sr=sr, hop_length=hop_length, fmin=fmin, n_bins=n_bins, 
                bins_per_octave=bins_per_octave, window=window))
            
            # 歯擦音の軽減をするために最後のオクターブを10dBほど軽減する
            # (アンプの状態では0.3倍するだけでおおよそ近くなる)
            for num in range(n_bins - (2*bins_per_octave), n_bins):
                chroma_cqt[num] *= 0.3
            
            pitch_list = [] # 各フレームごとの音階
            midi_list = [] # 音階の長さリスト
            tmp_pitch = 0 # 一時的に保存する音階
            count = 1 # 音階の長さ
            print(type(chroma_cqt), len(chroma_cqt))
            chroma_cqt_T = chroma_cqt.T
            for x in chroma_cqt_T:
                # フレームごとの音階をリスト化する
                pitch_list.append(np.argmax(x))
                
                # 音階化したリストについて、音階の長さを調べ、
                # 音階が続けば長さを加え、違う音程になれば出力する
                if np.argmax(x) == tmp_pitch:
                    count += 1
                else:
                    midi_list.append([tmp_pitch, count])
                    tmp_pitch = np.argmax(x)
                    count = 1
            # 最後の音階を出力する
            midi_list.append([tmp_pitch, count])
            # 最初の音階は高さ0なので排外する
            midi_list.remove(midi_list[0])
            
            
            print('len(pitch_list): ', len(pitch_list))
            print('pitch_list: ', pitch_list)
            print('len(midi_list): ', len(midi_list))
            print('midi_list: ', midi_list)
            print('Convert Done!!!')
            
            
            '''
            Save Midi with Mido
            '''
            
            mid = MidiFile()
            track = MidiTrack()
            mid.tracks.append(track)
            track.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(120)))
            for note in midi_list:
                track.append(Message('note_on', note=note[0]+36, velocity=127, time=0))
                track.append(Message('note_off', note=note[0]+36, time=120*note[1]))

            mid.save(self.filetext+'.mid') # 元の音声ファイル名+.mid
            
            # 変換後にボタンの色とテキストを元に戻しておく
            self.converttext = 'WAV2MIDI変換'
            self.color3 = [0.5, 0.5, 0.5, 1.0]
            
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