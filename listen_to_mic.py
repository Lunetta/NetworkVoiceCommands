import os
import json
from argparse import ArgumentParser

import pyaudio
from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource
from threading import Thread
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

try:
    from Queue import Queue, Full
except ImportError:
    from queue import Queue, Full

# Parameters needed for recording
CHUNK = 1024
BUF_MAX_SIZE = CHUNK * 10
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100


def listen_to_mic(api_key, service_url):
    q = Queue(maxsize=int(round(BUF_MAX_SIZE / CHUNK)))
    audio_source = AudioSource(q, is_recording=True, is_buffer=True)

    # Prepare Speech to Text Service

    # initialize speech to text service
    authenticator = IAMAuthenticator(apikey=api_key)
    speech_to_text = SpeechToTextV1(authenticator=authenticator)
    speech_to_text.set_service_url(service_url)

    # define callback for the speech to text service
    class MyRecognizeCallback(RecognizeCallback):
        def __init__(self):
            RecognizeCallback.__init__(self)

        def on_transcription(self, transcript):
            print(transcript[0]['transcript'])

        def on_connected(self):
            print('Connection was successful')

        def on_error(self, error):
            print('Error received: {}'.format(error))

        def on_inactivity_timeout(self, error):
            print('Inactivity timeout: {}'.format(error))

        def on_listening(self):
            print('Service is listening')

        def on_hypothesis(self, hypothesis):
            pass
            # print(hypothesis)

        def on_data(self, data):
            pass
            # print(data)

        def on_close(self):
            print("Connection closed")

    # this function will initiate the recognize service and pass in the AudioSource
    def recognize_using_websocket(*args):
        mycallback = MyRecognizeCallback()
        if FORMAT == pyaudio.paInt16:
            content_type = f"audio/l16; rate={RATE}"
        else:
            raise NotImplementedError("only pyaudio.paInt16 format is supported")

        speech_to_text.recognize_using_websocket(audio=audio_source,
                                                 content_type=content_type,
                                                 recognize_callback=mycallback,
                                                 interim_results=True)

    # Prepare the for recording using Pyaudio

    # define callback for pyaudio to store the recording in queue
    def pyaudio_callback(in_data, frame_count, time_info, status):
        try:
            q.put(in_data)
        except Full:
            pass  # discard
        return None, pyaudio.paContinue

    # instantiate pyaudio
    audio = pyaudio.PyAudio()

    # open stream using callback
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        output=False,
        frames_per_buffer=CHUNK,
        stream_callback=pyaudio_callback,
        start=False
    )

    # Start the recording and start service to recognize the stream
    print("Enter CTRL+C to end recording...")

    stream.start_stream()

    try:
        recognize_thread = Thread(target=recognize_using_websocket, args=())
        recognize_thread.start()

        while True:
            pass
    except KeyboardInterrupt:
        # stop recording
        stream.stop_stream()
        stream.close()
        audio.terminate()
        audio_source.completed_recording()


if __name__ == "__main__":
    arg_parser = ArgumentParser()
    arg_parser.add_argument("--authentication_file", default="auth.json", type=str,
                            help="Json file containing api_key and service_url")
    arg_parser.add_argument("--api_key", type=str, help="api_key to access the IBM Watson APIs")
    arg_parser.add_argument("--service_url", type=str, help="URL serving the IBM Watson APIs")
    args = arg_parser.parse_args()

    api_key = service_url = None
    if os.path.exists(args.authentication_file):
        with open(args.authentication_file, 'r') as fp:
            auth = json.load(fp)

        api_key = auth['api_key'] if 'api_key' in auth else None
        service_url = auth['service_url'] if 'service_url' in auth else None

    if args.api_key:
        api_key = args.api_key

    if args.service_url:
        service_url = args.service_url

    assert api_key and service_url, "You need to specify api_key and service_url, either specifying a json file " \
                                    "in --authentication_file, or by setting --api_key and --service_url"

    listen_to_mic(api_key, service_url)
