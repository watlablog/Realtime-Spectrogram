import numpy as np
import queue
import threading
import pyaudio
import matplotlib.pyplot as plt
from scipy import fftpack
import soundfile as sf

# キュー
data_queue = queue.Queue()

def record_thread(index, samplerate, frames_per_buffer):
    """リアルタイムに音声を録音するスレッド"""

    # PyAudioインスタンスの生成とストリーム開始
    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paInt16, channels=1, rate=samplerate,
                     input=True, input_device_index=index, frames_per_buffer=frames_per_buffer)
    # リアルタイム録音
    try:
        while True:
            data = stream.read(frames_per_buffer, exception_on_overflow=False)
            data = np.frombuffer(data, dtype="int16") / float((np.power(2, 16) / 2) - 1)
            data_queue.put(data)
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()
        
        
def get_mic_index():
    ''' マイクチャンネルのindexをリストで取得する '''
 
    # 最大入力チャンネル数が0でない項目をマイクチャンネルとしてリストに追加
    pa = pyaudio.PyAudio()
    mic_list = []
    for i in range(pa.get_device_count()):
        num_of_input_ch = pa.get_device_info_by_index(i)['maxInputChannels']
 
        if num_of_input_ch != 0:
            mic_list.append(pa.get_device_info_by_index(i)['index'])
 
    return mic_list[0]


def calc_fft(data, samplerate):
    """FFTを計算する関数"""
    
    spectrum = fftpack.fft(data)
    amp = np.sqrt((spectrum.real ** 2) + (spectrum.imag ** 2))
    amp = amp / (len(data) / 2)
    phase = np.arctan2(spectrum.imag, spectrum.real)
    phase = np.degrees(phase)
    freq = np.linspace(0, samplerate, len(data))

    return spectrum, amp, phase, freq

def plot_waveform(samplerate, frames_per_buffer):
    """波形をプロットする関数"""
    
    # 最大保持時間
    max_chart_time = 10

    # プロットの設定
    plt.rcParams['font.size'] = 14
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_xlabel('Time [s]')
    ax.set_ylabel('Frequency [Hz]')
    
    # スペクトログラムの初期データ
    initial_data = np.zeros((frames_per_buffer // 2, int(samplerate * max_chart_time / frames_per_buffer)))
    im = ax.imshow(initial_data, aspect='auto', extent=[0, max_chart_time, 0, samplerate // 2], cmap='jet', vmin=0, vmax=60)
    cbar = fig.colorbar(im)
    cbar.set_label('Noise level[dB]')

    # スペクトログラムチャートデータ（初期値は2次元の0配列）
    history_amp = initial_data
    
    # wavファイル保存用のチャートデータ（初期値は空)
    history_data = np.array([])

    # プロットループ
    while plt.fignum_exists(fig.number):
        if not data_queue.empty():
            # デキュー
            data = data_queue.get()
            
            # チャート波形作成(wav保存用)
            history_data = np.concatenate((history_data, data))
            # max_chart_timeを超えたら古いデータを削除
            if len(history_data) / samplerate > max_chart_time:
                history_data = history_data[frames_per_buffer:]
            
            # FFTを実行して振幅を計算
            spectrum, amp, phase, freq = calc_fft(data, samplerate)
            new_amp = amp[:frames_per_buffer // 2][::-1]

            # データの時間長が最大保持時間を超えた場合、古いデータから削除
            if history_amp.shape[1] > int(samplerate * max_chart_time / frames_per_buffer):
                history_amp = history_amp[:, -int(samplerate * max_chart_time / frames_per_buffer):]

            history_amp = np.hstack((history_amp, new_amp.reshape(-1, 1)))

            # 振幅データをdBに変換してプロット
            im.set_array(20 * np.log10(history_amp / 2e-5))
            ax.set_xlim(0, max_chart_time)
            ax.set_ylim(0, 3000)
            fig.tight_layout()
            plt.pause(0.01)
    
    return history_data

if __name__ == '__main__':
    """メイン文"""
    
    # サンプリングレートとフレームサイズ、マイクチャンネルを設定
    samplerate = 12800
    frames_per_buffer = 2048
    index = get_mic_index()

    # 録音関数を並列化実行
    threading.Thread(target=record_thread, args=(index, samplerate, frames_per_buffer), daemon=True).start()
    
    # プロット関数を実行
    waveform = plot_waveform(samplerate, frames_per_buffer)
    
    # wavファイルの保存(波形の絶対値の最大値を1にして最大限の音量に正規化)
    #max_value = np.max(np.abs(waveform))
    #normalized_waveform = waveform / max_value
    #sf.write('recorded.wav', waveform, samplerate)
    #print(f'waveform length = {len(waveform) / samplerate}[s]')