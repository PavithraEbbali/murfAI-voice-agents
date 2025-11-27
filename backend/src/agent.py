<<<<<<< HEAD
# ======================================================
# 🏦 DAY 6: BANK FRAUD ALERT AGENT (SQLite DB variant)
# ======================================================

import logging
import os
import sqlite3
from datetime import datetime
from typing import Annotated, Optional
from dataclasses import dataclass

print("\n" + "🛡️" * 50)
print("🚀 BANK FRAUD AGENT (SQLite) - INITIALIZED")
print("📚 TASKS: Verify Identity -> Check Transaction -> Update DB")
print("🛡️" * 50 + "\n")

from dotenv import load_dotenv
from pydantic import Field
=======
import logging
import os
import json
from datetime import datetime

from dotenv import load_dotenv
>>>>>>> 63103095ec4bcecf3e2d2ad74d1051a7efa801d6
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
<<<<<<< HEAD
    RoomInputOptions,
    WorkerOptions,
    cli,
    function_tool,
    RunContext,
)

=======
    MetricsCollectedEvent,
    RoomInputOptions,
    WorkerOptions,
    cli,
    metrics,
    tokenize,
    function_tool,
    RunContext,
)
>>>>>>> 63103095ec4bcecf3e2d2ad74d1051a7efa801d6
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")
<<<<<<< HEAD
load_dotenv()

# ======================================================
# 💾 1. DATABASE SETUP (SQLite)
# ======================================================

DB_FILE = "fraudlist_db.sqlite"

@dataclass
class FraudCase:
    userName: str
    securityIdentifier: str
    cardEnding: str
    transactionName: str
    transactionAmount: str
    transactionTime: str
    transactionSource: str
    case_status: str = "pending_review"
    notes: str = ""


def get_db_path():
    return os.path.join(os.path.dirname(__file__), DB_FILE)


def get_conn():
    path = get_db_path()
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def seed_database():
    """Create SQLite DB and insert sample rows if empty."""
    conn = get_conn()
    cur = conn.cursor()

    # ✅ FIXED SQL — CLEAN, NO BROKEN LINES
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS fraud_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userName TEXT NOT NULL,
            securityIdentifier TEXT,
            cardEnding TEXT,
            transactionName TEXT,
            transactionAmount TEXT,
            transactionTime TEXT,
            transactionSource TEXT,
            case_status TEXT DEFAULT 'pending_review',
            notes TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
        """
    )

    cur.execute("SELECT COUNT(1) FROM fraud_cases")
    if cur.fetchone()[0] == 0:
        sample_data = [
            (
                "John", "12345", "4242",
                "XYZ Technologies", "₹45,969.00", "2:30 AM EST", "helpful.com",
                "pending_review", "Automated flag: High value transaction."
            ),
            (
                "Charlie", "99887", "1199",
                "Unknown Crypto Exchange", "₹52,100.00", "4:15 AM PST", "online_transfer",
                "pending_review", "Automated flag: Unusual location."
            )
        ]
        cur.executemany(
            """
            INSERT INTO fraud_cases (
                userName, securityIdentifier, cardEnding, transactionName,
                transactionAmount, transactionTime, transactionSource, case_status, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            sample_data,
        )
        conn.commit()
        print(f"✅ SQLite DB seeded at {DB_FILE}")

    conn.close()


# Initialize DB on load
seed_database()

# ======================================================
# 🧠 2. STATE MANAGEMENT
# ======================================================

@dataclass
class Userdata:
    active_case: Optional[FraudCase] = None

# ======================================================
# 🛠️ 3. FRAUD AGENT TOOLS (SQLite-backed)
# ======================================================

@function_tool
async def lookup_customer(
    ctx: RunContext[Userdata],
    name: Annotated[str, Field(description="The name the user provides")],
) -> str:
    """Lookup a customer in SQLite DB."""
    print(f"🔎 LOOKING UP: {name}")
    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM fraud_cases WHERE LOWER(userName) = LOWER(?) LIMIT 1",
            (name,),
        )
        row = cur.fetchone()
        conn.close()

        if not row:
            return "User not found in the fraud database. Please repeat the name."

        record = dict(row)
        ctx.userdata.active_case = FraudCase(
            userName=record["userName"],
            securityIdentifier=record["securityIdentifier"],
            cardEnding=record["cardEnding"],
            transactionName=record["transactionName"],
            transactionAmount=record["transactionAmount"],
            transactionTime=record["transactionTime"],
            transactionSource=record["transactionSource"],
            case_status=record["case_status"],
            notes=record["notes"],
        )

        return (
            f"Record Found.\n"
            f"User: {record['userName']}\n"
            f"Security ID (Expected): {record['securityIdentifier']}\n"
            f"Transaction: {record['transactionAmount']} at {record['transactionName']} ({record['transactionSource']})\n"
            f"Ask user for their Security Identifier now."
        )

    except Exception as e:
        return f"Database error: {str(e)}"


@function_tool
async def resolve_fraud_case(
    ctx: RunContext[Userdata],
    status: Annotated[str, Field(description="confirmed_safe or confirmed_fraud")],
    notes: Annotated[str, Field(description="Notes on the user's confirmation")],
) -> str:

    if not ctx.userdata.active_case:
        return "Error: No active case selected."

    case = ctx.userdata.active_case
    case.case_status = status
    case.notes = notes

    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute(
            """
            UPDATE fraud_cases
            SET case_status = ?, notes = ?, updated_at = datetime('now')
            WHERE userName = ?
            """,
            (case.case_status, case.notes, case.userName),
        )
        conn.commit()

        # Confirm updated row
        cur.execute("SELECT * FROM fraud_cases WHERE userName = ?", (case.userName,))
        updated_row = dict(cur.fetchone())
        conn.close()

        print(f"✅ CASE UPDATED: {case.userName} -> {status}")

        if status == "confirmed_fraud":
            return (
                f"Fraud confirmed. Card ending {case.cardEnding} is now BLOCKED. "
                f"A replacement card will be issued.\n"
                f"DB Updated At: {updated_row['updated_at']}"
            )
        else:
            return (
                f"Transaction marked SAFE. Restrictions lifted.\n"
                f"DB Updated At: {updated_row['updated_at']}"
            )

    except Exception as e:
        return f"Error saving to DB: {e}"

# ======================================================
# 🤖 4. AGENT DEFINITION
# ======================================================

class FraudAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
            You are 'Alex', a Fraud Detection Specialist at State Bank Of India Bank.
            Follow strict security protocol:

            1. Greeting + ask for first name.
            2. Immediately call lookup_customer(name).
            3. Ask for Security Identifier.
            4. If correct → continue. If incorrect → end call politely.
            5. Explain suspicious transaction.
            6. Ask: Did you make this transaction?
               - YES → resolve_fraud_case('confirmed_safe')
               - NO → resolve_fraud_case('confirmed_fraud')
            7. Close professionally.
            """,
            tools=[lookup_customer, resolve_fraud_case],
        )

# ======================================================
# 🎬 ENTRYPOINT
# ======================================================
=======
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
>>>>>>> 63103095ec4bcecf3e2d2ad74d1051a7efa801d6

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

<<<<<<< HEAD

async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}

    print("\n" + "💼" * 25)
    print("🚀 STARTING FRAUD ALERT SESSION (SQLite)")

    userdata = Userdata()
=======
async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}

    # --- 3. Load Memory BEFORE starting the agent ---
    last_session = load_last_entry()
    history_text = "This is your first meeting."
    start_message = "Hello! I'm Willow, your wellness companion. How are you feeling today?"

    if last_session:
        history_text = f"Last time ({last_session['timestamp']}), you felt: {last_session['mood']}. Your goal was: {last_session['intentions']}."
        start_message = f"Welcome back! Last time you mentioned you were {last_session['mood']}. How are you feeling today?"
>>>>>>> 63103095ec4bcecf3e2d2ad74d1051a7efa801d6

    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
<<<<<<< HEAD
        tts=murf.TTS(
            voice="en-US-marcus",
            style="Conversational",
            text_pacing=True,
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        userdata=userdata,
    )

    await session.start(
        agent=FraudAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(noise_cancellation=noise_cancellation.BVC()),
=======
        
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
>>>>>>> 63103095ec4bcecf3e2d2ad74d1051a7efa801d6
    )

    await ctx.connect()

<<<<<<< HEAD
=======
    # Agent speaks the dynamic start message
    await session.say(start_message, allow_interruptions=True)
>>>>>>> 63103095ec4bcecf3e2d2ad74d1051a7efa801d6

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))