# Running the Voice Agent Locally

This guide explains how to run both the Next.js webapp and the Python agent locally.

## Quick Start

### Step 1: Start the Python Agent

Open a terminal and run:

```bash
cd /Users/shubhamsaboo/Voxology/agent-starter-python
./START_AGENT.sh
```

Or manually:
```bash
cd /Users/shubhamsaboo/Voxology/agent-starter-python
uv run python src/agent.py dev
```

### Step 2: Start the Webapp

Open a **new terminal** and run:

```bash
cd /Users/shubhamsaboo/Voxology/vox-takehome-test
pnpm dev
```

### Step 3: Test the Connection

1. Open http://localhost:3000 in your browser
2. Click "Start call"
3. Allow microphone permissions when prompted
4. Start speaking - the agent should respond!

## Configuration

### Python Agent Configuration

Edit `/Users/shubhamsaboo/Voxology/agent-starter-python/.env.local`:

```bash
# LiveKit Configuration (already set)
LIVEKIT_URL=wss://voxology-ny1u6qkj.livekit.cloud
LIVEKIT_API_KEY=APImB2N5gdEWkdh
LIVEKIT_API_SECRET=Hc1WkhXLh5ptXnIlxLcaAPzwbEq36ZX0UvYDE9aWIrD

# OpenAI Configuration (for local voice models)
USE_OPENAI_REALTIME=true
OPENAI_API_KEY=your_openai_api_key_here

# Optional: For local OpenAI-compatible server (e.g., LocalAI)
# OPENAI_BASE_URL=http://localhost:8080/v1

# Optional: Choose voice (alloy, echo, fable, onyx, nova, shimmer)
OPENAI_REALTIME_VOICE=alloy
```

### Webapp Configuration

The webapp is already configured in `/Users/shubhamsaboo/Voxology/vox-takehome-test/.env.local`:

```bash
LIVEKIT_API_KEY=APImB2N5gdEWkdh
LIVEKIT_API_SECRET=Hc1WkhXLh5ptXnIlxLcaAPzwbEq36ZX0UvYDE9aWIrD
LIVEKIT_URL=wss://voxology-ny1u6qkj.livekit.cloud
```

## How It Works

1. **Webapp** creates a LiveKit room when you click "Start call"
2. **Python Agent** (running in `dev` mode) automatically connects to the room
3. **Voice Pipeline** processes your speech and generates responses
4. **Real-time Communication** happens through LiveKit's WebRTC infrastructure

## Using Local Voice Models

### Option 1: OpenAI API (Recommended)

1. Get an OpenAI API key from https://platform.openai.com/api-keys
2. Add it to `agent-starter-python/.env.local`:
   ```bash
   OPENAI_API_KEY=sk-your-key-here
   USE_OPENAI_REALTIME=true
   ```

### Option 2: Local OpenAI-Compatible Server (LocalAI)

1. Install and run LocalAI: https://github.com/mudler/LocalAI
2. Update `agent-starter-python/.env.local`:
   ```bash
   OPENAI_BASE_URL=http://localhost:8080/v1
   USE_OPENAI_REALTIME=true
   OPENAI_API_KEY=dummy-key  # LocalAI doesn't require real key
   ```

### Option 3: LiveKit Inference (Cloud)

If you don't set `OPENAI_API_KEY`, the agent will use LiveKit Inference models (requires LiveKit Cloud).

## Troubleshooting

### Agent not connecting

- ✅ Check that the agent is running (`uv run python src/agent.py dev`)
- ✅ Verify LiveKit credentials in `.env.local` are correct
- ✅ Check agent terminal for error messages

### No voice response

- ✅ Verify `OPENAI_API_KEY` is set in `agent-starter-python/.env.local`
- ✅ Check that `USE_OPENAI_REALTIME=true` if using OpenAI
- ✅ Review agent logs for API errors

### Webapp shows connection error

- ✅ Ensure both webapp and agent are running
- ✅ Check browser console for errors
- ✅ Verify LiveKit URL format (should start with `wss://`)

### Microphone not working

- ✅ Check browser permissions (allow microphone access)
- ✅ Test microphone in other applications
- ✅ Check browser console for permission errors

## Next Steps

Now that you have the agent running locally, you can:

1. **Customize the agent** - Edit `agent-starter-python/src/agent.py` to change instructions or add tools
2. **Add provider search** - Implement the provider search functionality for the takehome test
3. **Test voice interactions** - Try different questions and see how the agent responds

## Files Reference

- **Python Agent**: `/Users/shubhamsaboo/Voxology/agent-starter-python/`
- **Webapp**: `/Users/shubhamsaboo/Voxology/vox-takehome-test/`
- **Agent Config**: `agent-starter-python/.env.local`
- **Webapp Config**: `vox-takehome-test/.env.local`
- **Start Script**: `/Users/shubhamsaboo/Voxology/START_AGENT.sh`


