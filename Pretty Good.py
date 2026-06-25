from twilio.rest import Client
from flask import Flask, request, redirect
from twilio.twiml.voice_response import VoiceResponse, Gather
import os

app = Flask(__name__)

twilio_sid = os.environ.get("TWILIO_ACCOUNT_SID")
twilio_auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
twilioNumber ='+15092603929'
# testNumber = '18054398008'
testNumber = '14255821282'
twilioURL = 'https://jangly-jacquie-partially.ngrok-free.dev/voice'

client = Client(twilio_sid, twilio_auth_token)

@app.route("/voice", methods=['POST'])

def voice():
    """Respond to incoming phone calls with a simple text message."""
    # Start our TwiML response
    resp = VoiceResponse()
    gather = Gather(input='speech', action ='/processSpeech', method='POST')
    resp.append(gather)

    print("Hello Voice got called")
    return str(resp)

@app.route("/processSpeech", methods=['POST'])

def processSpeech():
    """Process the caller's speech input."""
    speechText = request.form.get('SpeechResult')

    print(speechText)

    resp = VoiceResponse()
    resp.say(f"You said {speechText}")

    return str(resp)

@app.route("/errors", methods=['POST'])

def errors():
    """Handle any errors that occur during the call."""
    errorCode = request.form.get('ErrorCode')
    print(f"An error occurred: {errorCode}")
    return "Error received", 200

if __name__ == "__main__":
    call = client.calls.create(
        to = testNumber,
        from_ = twilioNumber,
        url = twilioURL
    )
    app.run(port=5000)
