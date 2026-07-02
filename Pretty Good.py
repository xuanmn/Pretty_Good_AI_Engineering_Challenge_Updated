from twilio.rest import Client
from flask import Flask, request, redirect, session
from twilio.twiml.voice_response import VoiceResponse, Gather
import os
import urllib.request
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
    "You are simulating a new patient calling a doctor's clinic for the first time. "
    "Your goal is to schedule a general check-up because you recently moved to the area. "
    "You want an appointment sometime next week, preferably in the morning. "
    "You are speaking on a phone call with an AI receptionist. "
    "Keep your responses short, conversational, and extremely natural for a voice call (typically 1-2 sentences maximum). "
    "Do not output markdown, lists, bullet points, or special characters. Speak directly as the patient."
)


# Dictionary to hold conversation histories by CallSid
call_histories = {}

@app.route("/voice", methods=['POST'])
def voice():
    """Respond to incoming phone calls and start the gathering loop."""
    call_sid = request.form.get('CallSid')
    
    # Reset conversation history for the new call session
    call_histories[call_sid] = []
    
    resp = VoiceResponse()
    # Gather speech from the agent who answers
    gather = Gather(input='speech', action='/processSpeech', method='POST', timeout=5)
    resp.append(gather)

    print("Call connected. Waiting for agent to speak...")
    return str(resp)

@app.route("/processSpeech", methods=['POST'])
def processSpeech():
    """Process the caller's speech input and generate an LLM response."""
    call_sid = request.form.get('CallSid')
    speechText = request.form.get('SpeechResult')
    resp = VoiceResponse()

    if not speechText:
        # If we didn't hear anything, try listening again
        gather = Gather(input='speech', action='/processSpeech', method='POST', timeout=5)
        resp.append(gather)
        return str(resp)

    print(f"Clinic Agent said: {speechText}")

    # Retrieve and update conversation history
    history = call_histories.get(call_sid, [])
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
        call_histories[call_sid] = history

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

@app.route("/status", methods=['POST'])
def status():
    """Save the transcript when the call completes."""
    call_sid = request.form.get('CallSid')
    call_status = request.form.get('CallStatus')
    
    if call_status in ['completed', 'failed', 'busy', 'no-answer', 'canceled']:
        history = call_histories.get(call_sid, [])
        if history:
            filename = f"transcript_{call_sid}.txt"
            with open(filename, "w") as f:
                for msg in history:
                    role = "Clinic Agent" if msg["role"] == "user" else "Patient (Bot)"
                    f.write(f"{role}:\n{msg['content']}\n\n")
            print(f"\n✅ Saved transcript to {filename}")
            
    return "OK", 200

@app.route("/recording", methods=['POST'])
def recording():
    """Download the MP3 recording when it becomes available."""
    call_sid = request.form.get('CallSid')
    recording_url = request.form.get('RecordingUrl')
    
    if recording_url:
        # Twilio recordings can be downloaded as mp3 by appending .mp3
        mp3_url = f"{recording_url}.mp3"
        filename = f"recording_{call_sid}.mp3"
        print(f"\n⬇️ Downloading recording to {filename}...")
        try:
            urllib.request.urlretrieve(mp3_url, filename)
            print(f"✅ Successfully saved {filename}")
        except Exception as e:
            print(f"❌ Failed to download recording: {e}")
            
    return "OK", 200

if __name__ == "__main__":
    base_url = twilioURLVoice.rsplit('/', 1)[0]  # Gets the domain from the webhook URL
    call = client.calls.create(
        to=testNumber,
        from_=twilioNumber,
        url=twilioURLVoice,
        status_callback=f"{base_url}/status",
        status_callback_event=['completed'],
        recording_status_callback=f"{base_url}/recording",
        recording_status_callback_event=['completed'],
        record=True
    )
    app.run(port=5000)

