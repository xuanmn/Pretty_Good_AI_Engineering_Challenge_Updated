# Pretty Good AI - Patient Simulator Bot

This repository contains a voice bot that acts as a "patient" to call the Pretty Good AI test line, evaluating quality and stress-testing edge cases. The bot uses Twilio for telephony and OpenAI's `gpt-4o-mini` for conversational intelligence.

## Setup Instructions

1. **Clone the repository and install dependencies**:
   This project uses `uv` for dependency management.
   ```bash
   uv sync
   ```

2. **Configure Environment Variables**:
   Copy the example environment file and fill in your details:
   ```bash
   cp .env.example .env
   ```
   Required variables in `.env`:
   - `TWILIO_ACCOUNT_SID`: Your Twilio Account SID
   - `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token
   - `TWILIO_NUMBER`: Your Twilio phone number
   - `TEST_NUMBER`: The test line number (e.g., `+1-805-439-8008`)
   - `TWILIO_URL_VOICE`: Your webhook URL (e.g., `https://your-ngrok-url.ngrok-free.dev/voice`)
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `FLASK_SECRET_KEY`: A random secret for Flask sessions

3. **Start ngrok**:
   Since Twilio needs a public URL to send webhooks to your local server, start ngrok on port 5000:
   ```bash
   ngrok http 5000
   ```
   *Make sure to update `TWILIO_URL_VOICE` in your `.env` file with the forwarding URL provided by ngrok.*

## Run Instructions

Once your `.env` is configured and ngrok is running, you can start the bot with a single command:

```bash
uv run python "Pretty Good.py"
```

This will instantly initiate a phone call to the `TEST_NUMBER` and start the local Flask server to handle the webhook responses.

## Architecture

**How it works:**
The system is built on a lightweight Flask backend that acts as a webhook receiver for Twilio. When the script is run, it uses the Twilio REST API to initiate an outbound call. Once connected, Twilio makes a POST request to the Flask `/voice` endpoint, which responds with TwiML instructions. The core interaction loop relies on Twilio's `<Gather>` verb to capture the human agent's speech, which is transcribed by Twilio and sent to the `/processSpeech` endpoint. The transcribed text is appended to a conversation history and sent to OpenAI's API. The LLM generates the patient's reply, which is sent back to Twilio via the `<Say>` verb, followed by another `<Gather>` to continue the conversation seamlessly.

**Design Choices:**
- **Flask**: Chosen for its simplicity and speed in spinning up webhook endpoints, allowing rapid iteration.
- **Twilio `<Gather>`**: By leveraging Twilio's native speech-to-text (ASR) via `<Gather>`, we avoid the latency and complexity of streaming raw audio via WebSockets or dealing with external ASR services.
- **OpenAI (`gpt-4o-mini`)**: Provides excellent reasoning, adherence to system prompts (simulating the patient persona), and very low latency response times, which is critical for maintaining natural conversational flow over the phone.
- **State Management**: An in-memory dictionary mapped to Twilio's unique `CallSid` is used to maintain the conversation history for each unique call. This ensures the LLM has full context of the interaction without needing a dedicated database, and allows background webhooks (like recording downloads) to access the state reliably.
