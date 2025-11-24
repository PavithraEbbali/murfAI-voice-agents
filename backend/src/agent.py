import logging
import os
import json
from datetime import datetime

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    RoomInputOptions,
    WorkerOptions,
    cli,
    metrics,
    tokenize,
    function_tool,
    RunContext,
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")
load_dotenv(".env.local")

# --- 1. Helper Functions for Memory (JSON) ---
LOG_FILE = "wellness_log.json"

def load_last_entry():
    """Reads the last check-in to give context."""
    if not os.path.exists(LOG_FILE):
        return None
    try:
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
            return data[-1] if data and isinstance(data, list) else None
    except Exception:
        return None

def append_entry(entry_data):
    """Saves the new check-in to the file."""
    history = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                history = json.load(f)
        except:
            history = []
    
    history.append(entry_data)
    with open(LOG_FILE, "w") as f:
        json.dump(history, f, indent=2)

# --- 2. The Wellness Agent Class ---
class Assistant(Agent):
    def __init__(self, history_context: str) -> None:
        # We inject the history into the system prompt here
        super().__init__(
            instructions=f"""
            You are 'Aura', a supportive health & wellness companion.
            
            YOUR GOAL: Conduct a short daily check-in with the user.
            
            CONTEXT FROM PAST:
            {history_context}
            
            STEPS:
            1. **Check-in**: Ask how they are feeling mentally/physically. (Reference the past if available).
            2. **Intentions**: Ask for 1-3 small, realistic goals for today.
            3. **Advice**: Offer ONE piece of simple, grounded advice (e.g., "Drink water", "Take a walk").
            4. **Recap & Save**: Summarize their mood and goals. THEN, call the 'log_checkin' tool to save it.
            
            TONE: Warm, calm, and supportive. Do NOT give medical advice.
            """,
        )

    @function_tool
    async def log_checkin(self, context: RunContext, mood: str, intentions: str, summary: str):
        """
        Call this tool when the user confirms their details to save the session.
        """
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mood": mood,
            "intentions": intentions,
            "summary": summary
        }
        append_entry(entry)
        return "I've saved your wellness log for today. Have a wonderful day!"

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}

    # --- 3. Load Memory BEFORE starting the agent ---
    last_session = load_last_entry()
    history_text = "This is your first meeting."
    start_message = "Hello! I'm Willow, your wellness companion. How are you feeling today?"

    if last_session:
        history_text = f"Last time ({last_session['timestamp']}), you felt: {last_session['mood']}. Your goal was: {last_session['intentions']}."
        start_message = f"Welcome back! Last time you mentioned you were {last_session['mood']}. How are you feeling today?"

    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        
        # --- 4. CRITICAL UPDATE: Use Murf Falcon ---
        tts=murf.TTS(
            model="en-US-falcon",  # REQUIRED for the challenge
            # voice="en-US-matthew" -> We removed this because Falcon uses 'model'
        ),
        
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        logger.info(f"Usage: {usage_collector.get_summary()}")

    ctx.add_shutdown_callback(log_usage)

    # Initialize Agent with the History Context
    await session.start(
        agent=Assistant(history_context=history_text),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await ctx.connect()

    # Agent speaks the dynamic start message
    await session.say(start_message, allow_interruptions=True)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))