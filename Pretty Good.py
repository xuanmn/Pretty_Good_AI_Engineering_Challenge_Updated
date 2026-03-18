from re import S
from dotenv import load_dotenv
from tracemalloc import start
from twilio.rest import Client
from flask import Flask, request, redirect
from flask_sock import Sock
from twilio.twiml.voice_response import Start, VoiceResponse, Gather
import os
import json
import base64
import audioop
import threading
import time
import wave

load_dotenv()

twilioID = os.getenv("TWILIO_ACCOUNT_SID")
twilioNumber = os.getenv("TWILIO_CALLER_ID")
twilioAuth = os.getenv("TWILIO_AUTH_TOKEN")
twilioURL = os.getenv("TWILIO_URL")
twilioDOMAIN = os.getenv("TWILIO_DOMAIN")
testNumber = os.getenv("TEST_NUMBER")

app = Flask(__name__)
sock = Sock(app)
client = Client(twilioID, twilioAuth)
buffer = b""
# model = whisper.load_model("base")


def print_buffer_periodically():
    global buffer
    while True:
        time.sleep(2)
        if buffer:
            print(f"Buffer length: {len(buffer)} bytes")
            print(buffer[:20])  # first few bytes as example
            buffer = b""  # reset after printing


threading.Thread(target=print_buffer_periodically, daemon=True).start()


@sock.route("/ws")
def websocket(ws):
    global buffer
    while True:
        message = ws.receive()
        if message is None:
            break
        data = json.loads(message)
        if data["event"] == "media":
            audioBytes = base64.b64decode(data["media"]["payload"])
            pcmAudio = audioop.ulaw2lin(audioBytes, 2)
            pcmAudi16k = audioop.ratecv(pcmAudio, 2, 1, 8000, 16000, None)[0]
            buffer += pcmAudi16k
            if len(buffer) >= 32000:  # Process every 2 seconds of audio
                print("Processing audio chunk...")


@app.route("/voice", methods=["POST"])
def voice():
    """Respond to incoming phone calls with a simple text message."""
    # Start our TwiML response
    resp = VoiceResponse()
    start = Start()
    start.stream(url=f"wss://{twilioDOMAIN}/ws")
    resp.append(start)
    resp.say("Start speaking")
    resp.pause(length=500)
    print("Voice webhook triggered")
    return str(resp)


@app.route("/errors", methods=["POST"])
def errors():
    """Handle any errors that occur during the call."""
    errorCode = request.form.get("ErrorCode")
    print(f"An error occurred: {errorCode}")
    return "Error received", 200


if __name__ == "__main__":
    call = client.calls.create(to=testNumber, from_=twilioNumber, url=twilioURL)
    app.run(port=5000)
