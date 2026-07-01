from twilio.rest import Client
from flask import Flask, request, redirect, session
from twilio.twiml.voice_response import VoiceResponse, Gather
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "pretty_good_secret_key_123")

twilio_sid = os.environ.get("TWILIO_ACCOUNT_SID")
twilio_auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
twilioNumber = os.environ.get("TWILIO_NUMBER")
testNumber = os.environ.get("TEST_NUMBER")
twilioURLVoice = os.environ.get("TWILIO_URL_VOICE")
client = Client(twilio_sid, twilio_auth_token)
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

SYSTEM_PROMPT = (
    "You are simulating a patient named Alex Rivera (Date of Birth: October 12, 1988) calling your doctor's clinic. "
    "Your goal is to reschedule your existing appointment from next Thursday at 2 PM to any time on Friday morning. "
    "You are speaking on a phone call with an AI receptionist. "
    "Keep your responses short, conversational, and extremely natural for a voice call (typically 1-2 sentences maximum). "
    "Do not output markdown, lists, bullet points, or special characters. Speak directly as the patient."
)

@app.route("/voice", methods=['POST'])
def voice():
    """Respond to incoming phone calls and start the gathering loop."""
    # Reset conversation history for the new call session
    session['history'] = []
    
    resp = VoiceResponse()
    # Gather speech from the agent who answers
    gather = Gather(input='speech', action='/processSpeech', method='POST', timeout=5)
    resp.append(gather)

    print("Call connected. Waiting for agent to speak...")
    return str(resp)

@app.route("/processSpeech", methods=['POST'])
def processSpeech():
    """Process the caller's speech input and generate an LLM response."""
    speechText = request.form.get('SpeechResult')
    resp = VoiceResponse()

    if not speechText:
        # If we didn't hear anything, try listening again
        gather = Gather(input='speech', action='/processSpeech', method='POST', timeout=5)
        resp.append(gather)
        return str(resp)

    print(f"Clinic Agent said: {speechText}")

    # Retrieve and update conversation history
    history = session.get('history', [])
    history.append({"role": "user", "content": speechText})

    try:
        # Call OpenAI Chat Completion
        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT}
            ] + history
        )
        patient_response = completion.choices[0].message.content.strip()
        print(f"Patient Simulator (us) response: {patient_response}")

        # Save our response to history
        history.append({"role": "assistant", "content": patient_response})
        session['history'] = history

        # Speak response and gather next input
        resp.say(patient_response)
        gather = Gather(input='speech', action='/processSpeech', method='POST', timeout=5)
        resp.append(gather)

    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        resp.say("Excuse me, could you repeat that?")
        gather = Gather(input='speech', action='/processSpeech', method='POST', timeout=5)
        resp.append(gather)

    return str(resp)

@app.route("/errors", methods=['POST'])
def errors():
    """Handle any errors that occur during the call."""
    errorCode = request.form.get('ErrorCode')
    print(f"An error occurred: {errorCode}")
    return "Error received", 200

if __name__ == "__main__":
    call = client.calls.create(
        to=testNumber,
        from_=twilioNumber,
        url=twilioURLVoice,
        record=True
    )
    app.run(port=5000)

