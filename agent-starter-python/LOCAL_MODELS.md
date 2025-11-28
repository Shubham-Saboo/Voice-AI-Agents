# Running Voice Models Locally

This guide explains how to run voice models (STT/TTS/LLM) locally on your machine instead of using cloud APIs.

## Understanding "Local" vs "Cloud"

- **Running the agent code locally**: ✅ You're already doing this when you run `uv run python src/agent.py dev`
- **Running voice models locally**: This means the STT/TTS/LLM models run on your machine, not in the cloud

## Current Setup Options

### Option 1: OpenAI Realtime API (Cloud - NOT Local)
When you use OpenAI Realtime API, the models run on OpenAI's servers:
```bash
USE_OPENAI_REALTIME=true
OPENAI_API_KEY=sk-your-key
# Models run on OpenAI's cloud servers
```

### Option 2: LocalAI (Local Models ✅)
Use LocalAI to run models locally on your machine:

1. **Install and run LocalAI**:
   ```bash
   # Using Docker (recommended)
   docker run -p 8080:8080 --name local-ai -ti localai/localai:latest-aio-cpu
   
   # Or install from source: https://github.com/mudler/LocalAI
   ```

2. **Configure the agent** to use LocalAI:
   ```bash
   # In agent-starter-python/.env.local
   USE_OPENAI_REALTIME=true
   OPENAI_BASE_URL=http://localhost:8080/v1
   OPENAI_API_KEY=dummy-key  # LocalAI doesn't require a real key
   OPENAI_REALTIME_VOICE=alloy
   ```

3. **Run the agent**:
   ```bash
   cd agent-starter-python
   uv run python src/agent.py dev
   ```

### Option 3: LiveKit Inference (Cloud - NOT Local)
The current non-realtime setup uses LiveKit Inference, which runs models in the cloud:
```bash
USE_OPENAI_REALTIME=false
# Uses assemblyai/universal-streaming (STT), openai/gpt-5-nano (LLM), cartesia/sonic-3 (TTS)
# All models run on LiveKit Cloud servers
```

## Answer to Your Question

**Q: Does "running the voicemodel locally" mean I cannot use OpenAI Realtime API?**

**A:** It depends on interpretation:

1. **If "locally" means running agent code locally**: ✅ Yes, you CAN use OpenAI Realtime API
   - The agent code runs on your machine
   - The models run on OpenAI's servers (cloud)

2. **If "locally" means running models on your machine**: ❌ No, you CANNOT use OpenAI Realtime API directly
   - You MUST use LocalAI or another local server
   - Point `OPENAI_BASE_URL` to your local server

## Recommended Setup for Truly Local Models

For the takehome test requirement of "running the voicemodel locally", use **LocalAI**:

```bash
# 1. Start LocalAI (in one terminal)
docker run -p 8080:8080 --name local-ai -ti localai/localai:latest-aio-cpu

# 2. Configure agent (in agent-starter-python/.env.local)
USE_OPENAI_REALTIME=true
OPENAI_BASE_URL=http://localhost:8080/v1
OPENAI_API_KEY=dummy-key
OPENAI_REALTIME_VOICE=alloy

# 3. Run agent (in another terminal)
cd agent-starter-python
uv run python src/agent.py dev

# 4. Run webapp (in a third terminal)
cd vox-takehome-test
pnpm dev
```

## About OpenAI Whisper API

**OpenAI Whisper API** is a cloud service (like Realtime API). If you want to use Whisper locally:

1. **Use LocalAI with Whisper**: LocalAI can run Whisper models locally
2. **Use OpenAI Whisper plugin**: The LiveKit OpenAI plugin supports Whisper, but it calls OpenAI's cloud API
3. **Custom implementation**: Implement a custom STT node using faster-whisper or whisper.cpp

For truly local Whisper, use LocalAI configured with Whisper models.

## Troubleshooting Local Models

### LocalAI not responding
- Check that LocalAI is running: `curl http://localhost:8080/v1/models`
- Check Docker logs: `docker logs local-ai`
- Ensure port 8080 is not in use

### Agent can't connect to LocalAI
- Verify `OPENAI_BASE_URL=http://localhost:8080/v1` in `.env.local`
- Check that LocalAI is accessible: `curl http://localhost:8080/health`

### Models not loading
- LocalAI needs models downloaded - check LocalAI documentation
- Some models require GPU - use CPU-compatible models for local development

