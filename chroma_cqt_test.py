import librosa
import librosa.display
import argparse
import urllib.request
import pathlib
import numpy as np
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url',
                        default='http://makotomurakami.com/blog/wp-content/uploads/2020/06/piano_ccddeffggaabc3.wav')
    parser.add_argument('-s', '--save_file_name', default='piano_ccddeffggaabc3.wav')
    arguments = parser.parse_args()

    if not pathlib.Path(arguments.save_file_name).exists():
        print('Downloading ...', end=' ')
        urllib.request.urlretrieve(arguments.url, filename=arguments.save_file_name)
        print('Done.')

    # y, sr = librosa.load(arguments.save_file_name)
    y, sr = librosa.load('wavfiles/asano.wav')
    y, index = librosa.effects.trim(y)

    hop_length = 512
    window = 'hann'
    bins_per_octave = 12
    n_octaves = 7
    n_bins = bins_per_octave * n_octaves
    cqt = librosa.cqt(y, sr=sr, hop_length=hop_length, fmin=librosa.note_to_hz('C1'), n_bins=n_bins,
                      bins_per_octave=bins_per_octave, window=window)
    cqt_amplitude = np.abs(cqt)

    fig = plt.figure(figsize=(6.4*2, 4.8))

    ax = fig.add_subplot(1, 2, 1)
    librosa.display.specshow(librosa.amplitude_to_db(cqt_amplitude, ref=np.max), sr=sr, x_axis='time', y_axis='cqt_hz')
    plt.colorbar(format='%+2.0f dB')
    ax.set_title('constant-Q power spectrum (frequency)')

    ax = fig.add_subplot(1, 2, 2)
    librosa.display.specshow(librosa.amplitude_to_db(cqt_amplitude, ref=np.max), sr=sr, x_axis='time', y_axis='cqt_note')
    plt.colorbar(format='%+2.0f dB')
    ax.set_title('constant-Q power spectrum (note)')

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()