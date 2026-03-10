from twilio.rest import Client
from flask import Flask, request, redirect
from twilio.twiml.voice_response import VoiceResponse, Gather
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

twilioID = os.getenv("TWILIO_ACCOUNT_SID")
twilioNumber = os.getenv("TWILIO_PHONE_NUMBER")
twilioAuth = os.getenv("TWILIO_AUTH_TOKEN")
twilioURL = os.getenv("TWILIO_URL")

# testNumber = '18054398008'
testNumber = os.getenv("TEST_NUMBER")


client = Client(twilioID, twilioAuth)


@app.route("/voice", methods=["POST"])
def voice():
    """Respond to incoming phone calls with a simple text message."""
    # Start our TwiML response
    resp = VoiceResponse()
    gather = Gather(input="speech", action="/processSpeech", method="POST")
    resp.append(gather)

    print("Hello Voice got called")
    return str(resp)


@app.route("/processSpeech", methods=["POST"])
def processSpeech():
    """Process the caller's speech input."""
    speechText = request.form.get("SpeechResult")

    print(speechText)

    resp = VoiceResponse()
    resp.say(f"You said {speechText}")

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
