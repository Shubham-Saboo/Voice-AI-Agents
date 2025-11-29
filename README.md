# Healthcare Provider Voice Assistant

A voice-powered AI assistant that helps users find healthcare providers through natural conversation. Built with LiveKit Agents for real-time voice interaction and a Next.js frontend for a seamless user experience.

## 🎯 Overview

Voxology is an intelligent healthcare provider search system that allows users to find doctors, specialists, and healthcare professionals through voice commands. The system understands natural language queries like:

- *"Can you give me any 2 providers from Oklahoma City?"*
- *"Can you give me phone numbers of doctors in Milwaukee who do general surgery?"*
- *"Find cardiologists in Texas who accept Blue Cross insurance"*

The assistant uses advanced voice AI to understand user intent, searches a comprehensive provider database, and displays results in real-time.

## ✨ Features

### Voice Interaction
- **Real-time voice AI** powered by LiveKit Agents
- **Natural language understanding** for complex queries
- **Multi-turn conversations** with context awareness

### Provider Search
- **Intelligent search** by location (state, city, ZIP code)
- **Specialty filtering** with automatic medical term mapping
- **Language support** for multilingual providers

## 🏗️ Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌──────────────┐
│   Next.js Web   │◄───────►│   LiveKit Cloud   │◄───────►│ Python Agent │
│     Frontend    │  WebRTC │   (WebRTC Hub)    │  WebRTC │   (Voice AI) │
└─────────────────┘         └──────────────────┘         └──────┬───────┘
                                                                   │
                                                                   ▼
                                                          ┌─────────────────┐
                                                          │  SQLite Database│
                                                          │  (Providers DB) │
                                                          └─────────────────┘
```
## 📖 Usage Examples

### Example Queries

**Location-based search:**
- *"Find providers in Oklahoma City"*
- *"Show me doctors in ZIP code 73102"*
- *"Give me 3 providers from Texas"*

**Specialty search:**
- *"Find cardiologists in Milwaukee"*
- *"I need a general surgeon in California"*
- *"Show me radiologists"*

**Insurance and language:**
- *"Find doctors who accept Blue Cross in New York"*
- *"Show me Spanish-speaking providers in Florida"*
- *"Cardiologists in Texas who accept Aetna and speak Spanish"*

**Specific provider:**
- *"Find Dr. Smith"*
- *"Show me information about John Doe"*

**Combined queries:**
- *"Give me phone numbers of general surgeons in Milwaukee"*
- *"Find 2 cardiologists in Oklahoma City who are accepting new patients"*

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and **pnpm** (for frontend)
- **Python** 3.9+ and **uv** (for agent)
- **LiveKit Cloud** account ([sign up here](https://cloud.livekit.io/))
- **OpenAI API key** (optional, for local voice models)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Voxology
   ```

2. **Set up the Python Agent**
   ```bash
   cd agent-starter-python
   uv sync
   ```

3. **Set up the Frontend**
   ```bash
   cd ../vox-takehome-test
   pnpm install
   ```

4. **Configure Environment Variables**

   Create `agent-starter-python/.env.local`:
   ```env
   # LiveKit Configuration
   LIVEKIT_URL=wss://your-project.livekit.cloud
   LIVEKIT_API_KEY=your_api_key
   LIVEKIT_API_SECRET=your_api_secret

   # OpenAI Configuration (for voice models)
   USE_OPENAI_REALTIME=true
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_REALTIME_VOICE=alloy
   ```

   Create `vox-takehome-test/.env.local`:
   ```env
   LIVEKIT_URL=wss://your-project.livekit.cloud
   LIVEKIT_API_KEY=your_api_key
   LIVEKIT_API_SECRET=your_api_secret
   ```

5. **Initialize the Database**
   ```bash
   cd agent-starter-python
   uv run python src/migrate_data.py
   ```

6. **Download Required Models**
   ```bash
   uv run python src/agent.py download-files
   ```

### Running the Application

1. **Start the Python Agent** (Terminal 1)
   ```bash
   cd agent-starter-python
   uv run python src/agent.py dev
   ```
   
   Or use the convenience script:
   ```bash
   ./START_AGENT.sh
   ```

2. **Start the Frontend** (Terminal 2)
   ```bash
   cd vox-takehome-test
   pnpm dev
   ```

3. **Open the Application**
   - Navigate to http://localhost:3000
   - Click "Start Conversation"
   - Allow microphone permissions
   - Start speaking!



## 📄 License

See individual component licenses:
- Agent: MIT License (see `agent-starter-python/LICENSE`)
- Frontend: Based on LiveKit examples

---

**Built with ❤️ using LiveKit Agents**

