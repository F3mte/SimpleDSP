import PySimpleGUI as sg
import os
import librosa
import soundfile as sf
from pydub import AudioSegment
from pydub.generators import WhiteNoise
from pydub.effects import low_pass_filter
from pydub.effects import high_pass_filter

sg.theme('DarkAmber')

bar = f'--------------------------------------------------------------------------------------------------\
----------------------------------------------------------------------------------------------------------'

layout = [
    [sg.Text(f'Welcome! What would You like to do?', size=(50, 1), k='-OUT-')],
    [sg.Text(f'{bar}', size=(63, 1))],
    [sg.Button(f'Load File'), sg.Text(f'Enter wav file name (with extension):'), sg.Input(k='-IN-', size=30)],
    [sg.Text(f'Name of the chosen wav file:'), sg.Text(f'', size=(40, 1), k='-OUT2-')],
    [sg.Button(f'Save as'), sg.Text(f'Enter file name (without extension):'), sg.Input(k='-Save-', size=32)],
    [sg.Text(f'{bar}', size=(63, 1))],
    [sg.Button(f'Low-pass filtering'), sg.Text(f'Enter cut-off frequency:'), sg.Input(k='-Low-', size=34)],
    [sg.Button(f'High-pass filtering'), sg.Text(f'Enter cut-off frequency:'), sg.Input(k='-High-', size=33)],
    [sg.Button(f'White Noise'), sg.Text(f'No need for any additional values')],
    [sg.Button(f'Speed Change'), sg.Text(f'Choose desired speed:'), sg.Input(k='-Speed-', size=36)],
    [sg.Button(f'Volume Change'), sg.Text(f'Change volume in decibels:'), sg.Input(k='-Vol-', size=31)],
    [sg.Button(f'Pitch Change'), sg.Text(f'Set by how many half steps pitch will be shifted:'),
     sg.Input(k='-Pitch-', size=16)],
    [sg.Button(f'Nightcore remix'), sg.Text(f'This option will perform speed-up and pitch raise')],
    [sg.Text(f'{bar}', size=(63, 1))],
    [sg.Button(f'Exit'), sg.Text(f'Remember to save file before you exit!')]
]

window = sg.Window('DSP Simple App', layout)

while True:
    event, values = window.read(timeout=1)
    global wav_file, name

    if event == 'Exit' or event == sg.WIN_CLOSED:
        break

    if event == 'Load File':

        try:
            f = open(values['-IN-'], 'r')
            f.close()
        except FileNotFoundError:
            print('File not found, please try again')

        try:
            wav_file = AudioSegment.from_file(values['-IN-'])
            name = values['-IN-']
            window['-OUT-'].update(f'Program successfully loaded a file!')
            window['-OUT2-'].update(values['-IN-'])
        except NameError:
            window['-OUT-'].update(f'Can\'t load the file, please choose a file with .wav extension!')

    if event == 'Save as':
        try:
            wav_file.export(values['-Save-'] + '.wav', format="wav")
            window['-OUT-'].update(f'Audio successfully saved as ' + values['-Save-'] + '.wav')
        except NameError:
            window['-OUT-'].update(f'Can\'t save the file, name is incorrect, please try another!')

    if event == 'Low-pass filtering':
        window['-OUT-'].update(f'Program is currently processing Your file, please be patient!')
        try:
            wav_file = low_pass_filter(wav_file,  int(values['-Low-']))
            window['-OUT-'].update(f'Program successfully performed low-pass filtering!')
        except ValueError:
            window['-OUT-'].update(f'Please choose integer value for filtering!')
        except ZeroDivisionError:
            window['-OUT-'].update(f'Please choose value that is not zero!')

    if event == 'High-pass filtering':
        window['-OUT-'].update(f'Program is currently processing Your file, please be patient!')
        try:
            wav_file = high_pass_filter(wav_file, int(values['-High-']))
            window['-OUT-'].update(f'Program successfully performed high-pass filtering!')
        except ValueError:
            window['-OUT-'].update(f'Please choose integer value for filtering!')
        except ZeroDivisionError:
            window['-OUT-'].update(f'Please choose value that is not zero!')

    if event == 'White Noise':
        window['-OUT-'].update(f'Program is currently processing Your file, please be patient!')
        try:
            noise = WhiteNoise().to_audio_segment(duration=len(wav_file))
            wav_file = wav_file.overlay(noise)
            window['-OUT-'].update(f'Program successfully created an audio with noise!')
        except EnvironmentError:
            window['-OUT-'].update(f'That error should never happen,something \
            wrong with program code, blame the author!')

    if event == 'Speed Change':
        window['-OUT-'].update(f'Program is currently processing Your file, please be patient!')
        try:
            speed = float(values['-Speed-'])
            wav_file_2 = wav_file._spawn(wav_file.raw_data, overrides={"frame_rate": int(wav_file.frame_rate * speed)})
            wav_file = wav_file_2.set_frame_rate(wav_file.frame_rate)
            window['-OUT-'].update(f'Program successfully changed speed!')
        except ValueError:
            window['-OUT-'].update(f'Please choose float value for speed change! ')
        except ZeroDivisionError:
            window['-OUT-'].update(f'Please choose value that is not zero!')

    if event == 'Volume Change':
        window['-OUT-'].update(f'Program is currently processing Your file, please be patient!')
        try:
            wav_file = wav_file + values['-Vol-']
            window['-OUT-'].update(f'Program successfully changed volume!')
        except ValueError:
            window['-OUT-'].update(f'Please choose integer value for volume change!')

    if event == 'Pitch Change':
        window['-OUT-'].update(f'Program is currently processing Your file, please be patient!')
        try:
            y, sr = librosa.load(name, sr=wav_file.frame_rate)
            wav_file_2 = librosa.effects.pitch_shift(y, sr, n_steps=float(values['-Pitch-']))
            sf.write(f'{name[:-4]}_pitch_shifted.wav', wav_file_2, wav_file.frame_rate)
            wav_file = AudioSegment.from_file(f'{name[:-4]}_pitch_shifted.wav')
            os.remove(f'{name[:-4]}_pitch_shifted.wav')
            window['-OUT-'].update(f'Program successfully changed pitch of an audio!')
        except ValueError:
            window['-OUT-'].update(f'Please choose integer value for pitch change!')

    if event == 'Nightcore remix':
        window['-OUT-'].update(f'Program is currently processing Your file, please be patient!')
        try:
            y, sr = librosa.load(f'{name}', sr=wav_file.frame_rate)
            wav_file_2 = librosa.effects.pitch_shift(y, sr, n_steps=2.0)
            sf.write(f'{name[:-4]}_for_work.wav', wav_file_2, wav_file.frame_rate)
            wav_file = AudioSegment.from_file(f'{name[:-4]}_for_work.wav')
            os.remove(f'{name[:-4]}_for_work.wav')
            wav_file_2 = wav_file._spawn(wav_file.raw_data, overrides={"frame_rate": int(wav_file.frame_rate * 1.25)})
            wav_file = wav_file_2.set_frame_rate(wav_file.frame_rate)
            window['-OUT-'].update(f'Program successfully created a remix!')
        except EnvironmentError:
            window['-OUT-'].update(f'That error should never happen,something \
                        wrong with program code, blame the author!')

window.close()
