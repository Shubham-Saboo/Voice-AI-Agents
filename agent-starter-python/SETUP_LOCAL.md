# Local Python Agent Setup Guide

This guide will help you run the Python agent locally and connect it to your Next.js webapp.

## Prerequisites

- Python 3.9+ installed
- `uv` package manager installed (or use `pip` with a virtual environment)
- LiveKit Cloud account (or self-hosted LiveKit server)
- OpenAI API key (for voice models) OR configure a local OpenAI-compatible server

## Setup Steps

### 1. Environment Configuration

The `.env.local` file has been created with your LiveKit credentials. You need to add your OpenAI API key:

```bash
# Edit .env.local and add your OpenAI API key
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 2. For Local Voice Models (Optional)

If you want to use a local OpenAI-compatible server (like LocalAI):

1. Install and run LocalAI or another OpenAI-compatible server
2. Update `.env.local`:
   ```bash
   OPENAI_BASE_URL=http://localhost:8080/v1
   USE_OPENAI_REALTIME=true
   ```

### 3. Running the Agent

Start the agent in development mode:

```bash
cd /Users/shubhamsaboo/Voxology/agent-starter-python
uv run python src/agent.py dev
```

The agent will:
- Connect to your LiveKit server
- Listen for room connections
- Process voice interactions

### 4. Running the Webapp

In a separate terminal, start the Next.js webapp:

```bash
cd /Users/shubhamsaboo/Voxology/vox-takehome-test
pnpm dev
```

### 5. Testing the Connection

1. Open http://localhost:3000 in your browser
2. Click "Start call"
3. The webapp will create a room and the Python agent will automatically join
4. Start speaking - the agent should respond!

## Configuration Options

### Using OpenAI Realtime API (Recommended for Local)

Set in `.env.local`:
```bash
USE_OPENAI_REALTIME=true
OPENAI_API_KEY=your-key
OPENAI_REALTIME_VOICE=alloy  # Options: alloy, echo, fable, onyx, nova, shimmer
```

### Using LiveKit Inference (Cloud-based)

Set in `.env.local`:
```bash
USE_OPENAI_REALTIME=false
# Requires LiveKit Cloud API keys for inference models
```

### Voice Options for OpenAI Realtime

- `alloy` - Neutral, balanced voice
- `echo` - Warm, friendly voice
- `fable` - Expressive, animated voice
- `onyx` - Deep, authoritative voice
- `nova` - Bright, energetic voice
- `shimmer` - Soft, gentle voice

## Troubleshooting

### Agent not connecting to rooms

- Check that LiveKit credentials in `.env.local` are correct
- Ensure the agent is running in `dev` mode
- Check agent logs for connection errors

### No voice response

- Verify `OPENAI_API_KEY` is set correctly
- Check that `USE_OPENAI_REALTIME=true` if using OpenAI
- Review agent logs for API errors

### Webapp can't connect

- Ensure both webapp and agent are running
- Check that LiveKit URL format is correct (should start with `wss://`)
- Verify API keys match in both `.env.local` files

## Next Steps

- Add custom tools/functions to the agent (see commented examples in `src/agent.py`)
- Customize the agent's instructions/personality
- Integrate provider search functionality (for the takehome test)


