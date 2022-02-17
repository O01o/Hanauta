# Hanauta
Kivyを使用して、WavファイルをMIDIファイルに変換します。

## 使用パッケージ
kivy
mido
pyaudio (現在未使用状態)

## 実装部分
- Wav→MIDI変換機能

## 未実装部分
- 録音機能
- MIDI再生機能

## Wav2MIDIの実装方法
### 音声ファイル読み込み
<pre>
y, sr = librosa.load(self.filetext, sr=SAMPLE_RATE)
</pre>
yはサンプリングされたデータ、srはサンプリング周波数を返り値として受け取ります。
lobrosa.load関数の第一引数は、FileChooserで選択されたファイルのパス、第二引数はサンプリングレートです。
Wavファイルにおいても、ファイルごとに出力されるサンプリングレートは異なっております。
16000,44100,48000等と様々です。それをlibrosa.loadの第二引数にて8000に落とすことで、扱うデータ量を統一させるのです。

### 波形の状態を、各音階ごとの音圧に変換(Chroma-CQT)
<pre>
# 各パラメータの値の設定
hop_length = self.hop_length # CQTのサンプル数(ここがクロックの速さに応じて可変になる)(デフォルト値は512)(計算方法は紙の計算式にて)           
fmin = librosa.note_to_hz('C1') # 最低音階
bins_per_octave = 12 # 1オクターブ12音階
octaves = 5 # オクターブ数
n_bins = bins_per_octave * octaves # 音階の個数
window = 'hamming' # 窓関数のモデル(今回はハミング窓。ハン窓('hann')や三角窓('triang')もあり
print('hop_length: ', hop_length)
            
chroma_cqt = np.abs(librosa.cqt(y, sr=sr, hop_length=hop_length, fmin=fmin, n_bins=n_bins, bins_per_octave=bins_per_octave, window=window))
</pre>
データの可視化については公式ドキュメントを参考にしてください。
https://librosa.org/doc/main/generated/librosa.cqt.html#librosa.cqt
カラオケの採点システムでは、マイクで読み取った音声から最も近似する音階を読み出し、曲の高さと一致することで加点するシステムになっております。
その裏で動作しているのが、このChroma-CQTアルゴリズムと呼ばれるものです。
元々波形データというものは一元配列になっておりますが、それを時間軸ごとに音の高さを調べるには、時間軸と周波数軸で二元配列化する必要があります。
それを、音響工学においては、FFTという技術によって達成しています。
波形データはサンプリングされたものですので、当然ながら離散値です。そこから高さを調べるには、
一秒ごとに8000個流されるサンプルの中から、決まった量を抽出し、高速フーリエ変換を行う必要があるのです。
その変数がhop_lengthであり、値は16の整数倍である必要があります。これは、出力する音域が5オクターブと設定されているためです。なお、その設定ができる変数が、fmin, bins_per-octave, n_binsです。
window変数は窓関数のモデルの定義です。まず、FFTという方法では、音の高さは音階ごとにではなく、周波数ごとに音圧を出力してしまいます。そこで、音階の基本周波数を中心に、重み付き窓関数で音階ごとに音圧を調べることで、変換できるのです。なお、Chroma-CQT以外にも、Chroma-STFTと呼ばれる手法がありますが、前者の方が性能が良いことが知られているため、僕はこちらを参考にしました。

窓関数のモデル一覧は、scipyのドキュメントにて掲示されています。
https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.get_window.html#scipy.signal.get_window

