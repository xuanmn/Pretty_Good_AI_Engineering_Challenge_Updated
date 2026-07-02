# Pretty Good AI - Patient Simulator Bot

An automated voice testing framework designed to simulate caller behavior, stress-test IVR (Interactive Voice Response) routing systems, and audit AI receptionist capabilities. 

Built using **Python**, **Flask**, **Twilio Voice API**, and **OpenAI's GPT-4o-mini**, this bot acts as a synthetic "patient" to call clinic lines, run multi-turn conversational scenarios, and automatically log transcripts and recordings.

---

## 🌟 Key Features

* **LLM-Driven Conversational Agents:** Leverages `gpt-4o-mini` to simulate human callers responding dynamically to receptionist prompts in real time.
* **Telephony Automation:** Initiates outbound calls via the Twilio API and manages the audio stream statefully via Flask webhook endpoints.
* **Persona-Based Scenario Engine:** Pre-configured with 5 distinct testing scenarios to validate clinic response accuracy, scheduling logic, and resilience to user distractions.
* **Auto-Archiving & Auditing:** Automatically fetches call records, exports text transcripts upon call termination, and downloads call audio (`.mp3`) from Twilio's secure storage.

---

## 🏗️ Architecture

```
                 +-------------------+
                 |    Clinic IVR     |
                 | (Target Reception) |
                 +---------+---------+
                           |
               Outbound Call / Speech
                           |
                           v
  +---------+      TwiML / Webhook       +-----------------------+
  |  Twilio | <========================> |      Flask Server     |
  | Gateway |     Speech Transcript      | (Local Webhook Host)  |
  +---------+                            +-----------+-----------+
                                                     |
                                            Prompt & Context
                                                     |
                                                     v
                                         +-----------+-----------+
                                         |    OpenAI API         |
                                         |  (gpt-4o-mini LLM)    |
                                         +-----------------------+
```

1. **Initiation:** Running the script fires an outbound call from your Twilio number to the target receptionist number.
2. **Audio Gateway:** Twilio streams the speech to its Automatic Speech Recognition (ASR) engine using the `<Gather>` verb.
3. **Response Hook:** The transcribed speech is posted to our Flask backend's `/processSpeech` route.
4. **Context & LLM:** Flask retrieves the conversation history mapping to the unique `CallSid`, prompts OpenAI with the active patient persona, and generates a natural conversational reply.
5. **Speech Synthesis:** Flask responds with TwiML `<Say>` to voice the patient's reply and loops back to `<Gather>` for the receptionist's response.
6. **Archival:** Upon call hangup, the `/status` and `/recording` webhooks log the final text transcript and download the call audio locally.

---

## 🧪 Testing Scenarios

The simulator includes five pre-configured prompt scenarios in `Pretty Good.py` to evaluate different aspects of the clinic's reception flow:

1. **Simple Appointment Scheduling:** Simulates a patient seeking a morning appointment.
2. **Canceling an Appointment:** Evaluates the agent's ability to handle cancellation requests and stubborn refusal to reschedule.
3. **Medication Refill Request:** Tests intent classification for prescription refills and location routing (e.g., pharmacy preference).
4. **Distracted Caller Simulation:** Tests system resilience against human quirks by injecting conversational noise ("wait, hold on", barking dogs) and request repetitions.
5. **General Clinic Inquiries:** Asks about insurance policy compatibility (e.g., Blue Cross Blue Shield), hours of operation, and clinic location.

---

## 💡 Key Engineering Insight: Caller Identity Match

Through iterative testing with different system prompts, a critical IVR verification behavior was discovered:
> [!IMPORTANT]
> **Caller Authentication Constraint:** The target clinic agent matches the caller's phone number with the initial name and Date of Birth (DOB) provided in the call. If the system prompt is changed to a name/DOB not mapped to the testing phone number (e.g., simulating John Doe, born July 4th, 2000), the clinic agent hangs up immediately after the DOB step. To successfully pass verification and test downstream routing, the bot must present the registered identity (**Jamie Smith, DOB March 12, 1990**).

---

## ⚙️ Setup & Execution

### 1. Clone & Install Dependencies
This project uses [uv](https://github.com/astral-sh/uv) for fast, reliable dependency management.
```bash
# Sync dependencies in a virtual environment
uv sync
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and fill in the details:
```bash
cp .env.example .env
```
Ensure you set:
* `TWILIO_ACCOUNT_SID` & `TWILIO_AUTH_TOKEN`
* `TWILIO_NUMBER` (Your outbound line)
* `TEST_NUMBER` (The target clinic receptionist line)
* `TWILIO_URL_VOICE` (Your public ngrok forwarding webhook)
* `OPENAI_API_KEY`
* `FLASK_SECRET_KEY`

### 3. Start ngrok Tunnel
Expose local port `5000` to the internet to receive Twilio's webhooks:
```bash
ngrok http 5000
```
Update the `TWILIO_URL_VOICE` variable in your `.env` with the HTTPS ngrok forwarding URL.

### 4. Run the Simulator
Start the Flask app and trigger the outbound dial with:
```bash
uv run python "Pretty Good.py"
```
Once the call completes, look in the project root for newly generated `transcript_*.txt` and `recording_*.mp3` files.
