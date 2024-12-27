# Realtime-Spectrogram
Realtime recording and create spectrogram software. PyAudio(Recording), SciPy(FFT), Matplotlib(Plot)
See this site for detail explanation.
https://watlab-blog.com/2024/07/14/realtime-spectrogram/

The spectrogram created in this project looks like the image below.
![STFT](https://watlab-blog.com/wp-content/uploads/2019/10/spectrogram-a.png)
Spectrograms can be drawn in real time.
<iframe width="600" height="400" src="https://www.youtube.com/embed/YJsKM3-JJLA" frameborder="0" allowfullscreen></iframe>



## About Spectrogram
Spectrograms use a calculation called STFT (Short Time Fourie Transform), which performs Fast Fourie Transform (FFT) in a short time.
![STFT](https://watlab-blog.com/wp-content/uploads/2019/05/explain_stft.png)

The STFT calculation method and how to create a spectrogram have already been explained on the WATLAB blog, so please refer to the following article.
https://watlab-blog.com/2019/05/19/python-spectrogram/

## How to use
Clone this project and pip install the necessary libraries to use it.
