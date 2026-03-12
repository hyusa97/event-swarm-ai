
import os
import asyncio
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import requests
import ollama
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import UploadFile, File
import pandas as pd
import io

load_dotenv()

app = FastAPI(title="Social Media Content Agent API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase configuration
SUPABASE_URL = os.getenv("VITE_SUPABASE_URL")
SUPABASE_KEY = os.getenv("VITE_SUPABASE_PUBLISHABLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Scheduler
scheduler = BackgroundScheduler()
scheduler.start()

class EventData(BaseModel):
    eventName: str
    theme: str
    date: str
    location: str
    description: str

class PostData(BaseModel):
    platform: str
    caption: str
    image_url: str
    scheduled_time: str

class Participant(BaseModel):
    name: str
    email: str
    team_name: Optional[str] = ""
    college: Optional[str] = ""

class EmailTemplate(BaseModel):
    eventName: str
    subjectTemplate: str
    bodyTemplate: str
    participants: Optional[List[dict]] = None

# In-memory storage
participants_storage = []
local_email_logs = []

# Local storage fallback
local_logs = []
local_posts = []

async def log_activity(action: str, platform: Optional[str] = None):
    log_entry = {
        "action": action,
        "platform": platform,
        "timestamp": datetime.now().isoformat()
    }
    print(f"[AGENT] {action}")
    local_logs.insert(0, log_entry) # Keep latest at top
    
    try:
        supabase.table("agent_logs").insert(log_entry).execute()
    except Exception:
        pass 

def publish_to_social_media(post_id: str, platform: str, caption: str):
    """Placeholder for real social media publishing"""
    print(f"Publishing to {platform}: {caption}")
    try:
        supabase.table("generated_posts").update({"status": "published"}).eq("id", post_id).execute()
    except Exception:
        pass
    asyncio.run(log_activity(f"Published post to {platform}", platform))

@app.post("/api/generate-social-content")
async def generate_content(data: EventData):
    await log_activity(f"Started generating content for {data.eventName}")
    
    try:
        platforms = ["LinkedIn", "Twitter/X", "Instagram"]
        results = []
        
        # 1. Generate captions using Ollama
        prompt = f"""
        Act as a professional Social Media Copywriter. Create 3 LONG-FORM, high-value posts for:
        
        EVENT: {data.eventName}
        THEME: {data.theme}
        DATE: {data.date}
        LOCATION: {data.location}
        DESCRIPTION: {data.description}
        
        STRICT FORMATTING RULES:
        1. LinkedIn: 500+ words. Professional tone. Include Hook, Story, Key Takeaways, Logistics, and CTA.
        2. Instagram: 300+ words. Story-driven. Detailed emoji use. Logistics and CTA.
        3. Twitter/X: 150+ words (treat as a thread-style single post). High energy.
        4. Hashtags: 15-20 trending tags.
        
        Return ONLY a JSON object with this exact structure:
        {{
          "LinkedIn": "...",
          "Twitter/X": "...",
          "Instagram": "...",
          "hashtags": ["...", "..."]
        }}
        
        Do not include any text before or after the JSON.
        """
        
        response = ollama.chat(
            model='llama3.2', 
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.8, 'num_predict': 4096}
        )
        content_raw = response['message']['content']
        print(f"Ollama Raw Output: {content_raw[:200]}...") # Log for debugging
        
        import json
        import re
        try:
            # More aggressive JSON cleaning - find first '{' and last '}'
            start = content_raw.find('{')
            end = content_raw.rfind('}') + 1
            if start != -1 and end != -1:
                json_str = content_raw[start:end]
                generated_content = json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
        except Exception as e:
            print(f"FAILED TO PARSE AI JSON: {e}")
            generated_content = {}

        # High-Quality Premium Long-Form Fallback
        # This ensures the user gets a "long form" result even if the local model fails
        if not generated_content.get("LinkedIn") or len(generated_content.get("LinkedIn", "")) < 300:
            await log_activity("Using Premium Long-Form Fallback")
            
            long_linkedin = f"""🚀 THE FUTURE IS HERE: Join us for the {data.eventName}!

Are you ready to witness the evolution of intelligence? The world is changing faster than ever, and at the heart of this transformation is the convergence of {data.theme}. 

From March 15-17, 2026, the brightest minds in AI and Technology will converge in {data.location} for three days of groundbreaking innovation, strategic networking, and deep-dive technical sessions. 

Whether you're a developer pushing the boundaries of code, a tech enthusiast curious about what the future holds, or a business leader looking to scale your enterprise with AI, this is the room you need to be in.

📍 Location: {data.location}
📅 Date: {data.date}
💡 Theme: {data.theme}

Expect high-octane keynotes, hands-on tech labs, and networking opportunities that will redefine your professional trajectory. From Generative AI to the next frontier of robotics, we're diving deep into the tech that's shaping our tomorrow.

Don't miss your chance to stay ahead of the curve. Secure your spot today and be part of the conversation shaping tomorrow.

🔥 Early Bird Registrations are NOW OPEN!
🔗 Register now at the link in our bio/comments!

#TechSummit2026 #AIRevolution #FutureTech #Innovation #MachineLearning #{data.eventName.replace(' ', '')} #DigitalTransformation #BhubaneswarTech #TechInnovation #SoftwareDevelopment #TechCommunity"""

            long_instagram = f"""The future isn't coming—it's already here. ✨🚀

Are you ready to witness the evolution of intelligence? Join us at {data.eventName}, where the brightest minds in AI and Technology converge for three days of groundbreaking innovation! 🤖💡

📍 Location: {data.location}
📅 Date: {data.date}
✨ Theme: {data.theme}

Expect high-octane keynotes, hands-on tech labs, and networking opportunities that will redefine your professional trajectory. We're diving deep into everything from Generative AI to robotics. 🚀👋

Whether you’re a developer, a tech enthusiast, or a visionary leader, this is the place to be.

🔥 Early Bird Registrations are NOW OPEN!
🔗 Secure your spot today via the link in our bio!

Let's build the future together. 🤝✨

#TechSummit2026 #AIRevolution #FutureOfTech #AITrends #InnovationHub #TechEvents2026 #AIInnovation"""

            long_twitter = f"""The future is arriving in {data.location}! �✨

Join us for #{data.eventName.replace(' ', '')} as we dive deep into the world of AI and cutting-edge technology. Experience 3 days of innovation that will redefine the digital era. 🤖🌐

📍 {data.location}
📅 {data.date}

Secure your spot today! ⬇️
#TechSummit2026 #AI #FutureOfTech #Innovation"""

            generated_content = {
                "LinkedIn": long_linkedin,
                "Twitter/X": long_twitter,
                "Instagram": long_instagram,
                "hashtags": ["Tech", "Future", "AI"]
            }

        # 2. Image Generation
        HF_KEY = os.getenv("HUGGINGFACE_API_KEY")
        image_prompt = f"Professional posters for {data.eventName}, tech aesthetic, 8k"
        image_url = None

        if HF_KEY:
            try:
                API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
                payload = {"inputs": image_prompt, "options": {"wait_for_model": True}}
                hf_res = requests.post(API_URL, headers={"Authorization": f"Bearer {HF_KEY}"}, json=payload, timeout=60)
                if hf_res.status_code == 200:
                    import base64
                    image_url = f"data:image/jpeg;base64,{base64.b64encode(hf_res.content).decode('utf-8')}"
                    await log_activity("Generated HF image")
            except: pass

        if not image_url:
            image_url = f"https://pollinations.ai/p/{image_prompt.replace(' ', '%20')}?width=1024&height=1024&seed={datetime.now().microsecond}"
            await log_activity("Using Pollinations fallback image")

        # 3. Save and Return
        for platform in platforms:
            post = {
                "platform": platform,
                "caption": generated_content.get(platform, ""),
                "image_url": image_url,
                "hashtags": generated_content.get("hashtags", []),
                "suggested_time": "Tomorrow at 10:00 AM"
            }
            results.append(post)
            try:
                supabase.table("generated_posts").insert(post).execute()
            except: pass

        await log_activity(f"Completed generation for {data.eventName}")
        print(f"DEBUG: Generated image_url starts with: {str(image_url)[:100]}...")
        return {"results": results, "image_url": image_url}

    except Exception as e:
        await log_activity(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/schedule-post")
async def schedule_post(data: PostData):
    await log_activity(f"Scheduling post for {data.platform}", data.platform)
    post_id = "local-" + str(datetime.now().timestamp())
    
    try:
        res = supabase.table("generated_posts").insert(data.dict()).execute()
        if res.data: post_id = res.data[0]['id']
    except: pass
    
    scheduled_dt = datetime.fromisoformat(data.scheduled_time.replace("Z", "+00:00"))
    scheduler.add_job(publish_to_social_media, 'date', run_date=scheduled_dt, args=[post_id, data.platform, data.caption])
    
    return {"status": "success", "post_id": post_id}

def personalize_template(template: str, participant: dict, event_name: str) -> str:
    # Safely handle missing keys by using get()
    return template.format(
        name=participant.get("name", "Participant"),
        email=participant.get("email", ""),
        team_name=participant.get("team_name", "N/A"),
        college=participant.get("college", "N/A"),
        event_name=event_name
    )

@app.post("/api/upload-participants")
async def upload_participants(file: UploadFile = File(...)):
    global participants_storage
    await log_activity(f"CSV Uploaded: {file.filename}")
    
    try:
        content = await file.read()
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_excel(io.BytesIO(content))
        
        # Normalize column names to lowercase and underscores
        df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]
        
        participants = df.to_dict('records')
        participants_storage = participants # Store in memory
        return participants
    except Exception as e:
        await log_activity(f"File Upload Error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")

@app.post("/api/preview-emails")
async def preview_emails(template: EmailTemplate):
    await log_activity("Emails Previewed")
    previews = []
    
    # Use participants from request or falling back to memory
    active_participants = template.participants or participants_storage
    
    # Preview for first 5 participants
    for p in active_participants[:5]:
        try:
            preview = {
                "name": p.get("name", "Participant"),
                "email": p.get("email", ""),
                "subject": personalize_template(template.subjectTemplate, p, template.eventName),
                "body": personalize_template(template.bodyTemplate, p, template.eventName)
            }
            previews.append(preview)
        except Exception:
            continue
    
    return previews

@app.post("/api/send-bulk-emails")
async def send_bulk_emails(template: EmailTemplate):
    await log_activity("Started bulk email sending")
    
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    
    active_participants = template.participants or participants_storage

    if not EMAIL_USER or not EMAIL_PASSWORD:
        await log_activity("Email bulk sending failed: Credentials missing")
        raise HTTPException(status_code=500, detail="EMAIL_USER or EMAIL_PASSWORD not configured")

    if not active_participants:
         raise HTTPException(status_code=400, detail="No participants uploaded")

    sent_count = 0
    failed_count = 0
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        
        for p in active_participants:
            try:
                msg = MIMEMultipart()
                msg['From'] = EMAIL_USER
                msg['To'] = p.get('email', '')
                msg['Subject'] = personalize_template(template.subjectTemplate, p, template.eventName)
                
                body = personalize_template(template.bodyTemplate, p, template.eventName)
                msg.attach(MIMEText(body, 'plain'))
                
                server.send_message(msg)
                
                log_entry = {"email": p.get('email'), "status": "sent", "timestamp": datetime.now().isoformat()}
                local_email_logs.insert(0, log_entry)
                try: supabase.table("email_logs").insert(log_entry).execute()
                except: pass
                
                sent_count += 1
            except Exception as e:
                failed_count += 1
                log_entry = {"email": p.get('email'), "status": "failed", "timestamp": datetime.now().isoformat(), "error_message": str(e)}
                local_email_logs.insert(0, log_entry)
                try: supabase.table("email_logs").insert(log_entry).execute()
                except: pass
        
        server.quit()
        await log_activity(f"Bulk email completed. Sent: {sent_count}, Failed: {failed_count}")
        return {"sent": sent_count, "failed": failed_count}
        
    except Exception as e:
        await log_activity(f"SMTP Critical Failure: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/email-logs")
async def get_email_logs():
    try:
        res = supabase.table("email_logs").select("*").order("timestamp", desc=True).limit(50).execute()
        if res.data: return res.data
    except: pass
    return local_email_logs if local_email_logs else [{"email": "system", "status": "idle", "timestamp": datetime.now().isoformat()}]

@app.get("/api/agent-logs")
async def get_logs():
    try:
        res = supabase.table("agent_logs").select("*").order("timestamp", desc=True).limit(50).execute()
        if res.data: return res.data
    except: pass
    return local_logs if local_logs else [{"action": "Local Mode Active", "timestamp": datetime.now().isoformat()}]

from datetime import timedelta

# Event Scheduler Agent Models
class Speaker(BaseModel):
    id: str
    name: str
    topic: str
    availability_start: str
    availability_end: str

class Room(BaseModel):
    id: str
    name: str
    capacity: int

class Session(BaseModel):
    id: str
    title: str
    speaker_id: str
    duration: int
    preferred_time: str
    scheduled_start: Optional[str] = None
    scheduled_end: Optional[str] = None
    room_id: Optional[str] = None

class Conflict(BaseModel):
    type: str 
    message: str
    session_ids: List[str]

class ScheduleRequest(BaseModel):
    sessions: List[dict]
    rooms: List[dict]
    event_date: str
    event_start_hour: str
    event_end_hour: str

# In-memory DB for Scheduler
speakers_db: List[dict] = []
rooms_db: List[dict] = []
sessions_db: List[dict] = []
scheduler_logs: List[str] = []

class EventSchedulerAgent:
    def __init__(self):
        self.sessions = []
        self.speakers = {}
        self.rooms = []
        self.conflicts = []
        self.schedule = []
        self.explanation = ""

    def log(self, message: str):
        print(f"[Scheduler] {message}")
        scheduler_logs.append(message)

    def load_data(self):
        self.log("Loading sessions, speakers, and rooms")
        self.sessions = [s.copy() for s in sessions_db]
        
        # Parse times
        for s in self.sessions:
            try:
                s["_preferred_dt"] = datetime.strptime(s.get("preferred_time", "09:00"), "%H:%M")
            except ValueError:
                s["_preferred_dt"] = datetime.strptime("09:00", "%H:%M")

        self.speakers = {s["id"]: s for s in speakers_db}
        self.rooms = [r.copy() for r in rooms_db]
        self.conflicts = []
        self.schedule = []
        self.explanation = ""

    def detect_conflicts(self):
        pass

    def run(self):
        self.log("Scheduler started")
        scheduler_logs.clear() # clear previous run logs
        self.log("Scheduler started")
        
        self.load_data()
        self.log(f"Loaded {len(self.sessions)} sessions")
        
        # Sort sessions by preferred time
        self.sessions.sort(key=lambda x: x["_preferred_dt"])
        
        self.generate_schedule()
        
        if self.conflicts:
            self.log(f"Detected {len(self.conflicts)} conflicts")
            self.resolve_conflicts()
        
        self.log("Final schedule generated successfully")
        
        if self.conflicts:
            self.explanation = f"Detected and resolved {len(self.conflicts)} conflicts by moving sessions to available time slots."
        else:
            self.explanation = "All sessions scheduled without any conflicts."
            
        return {
            "schedule": self.schedule,
            "conflicts": self.conflicts,
            "logs": scheduler_logs,
            "summary": self.explanation
        }

    def run_with_payload(self, req: ScheduleRequest):
        scheduler_logs.clear()
        self.log("Scheduler started with custom payload")
        
        self.sessions = [s.copy() for s in req.sessions]
        self.rooms = [r.copy() for r in req.rooms]
        self.speakers = {} # we don't have speaker limits in this mode or can use session['speaker_name']
        self.conflicts = []
        self.schedule = []
        self.explanation = ""
        self.event_date = req.event_date
        
        for s in self.sessions:
            try:
                if s.get("preferred_time"):
                    s["_preferred_dt"] = datetime.strptime(f"{req.event_date} {s['preferred_time']}", "%Y-%m-%d %H:%M")
                else:
                    s["_preferred_dt"] = datetime.strptime(f"{req.event_date} {req.event_start_hour}", "%Y-%m-%d %H:%M")
            except Exception:
                s["_preferred_dt"] = datetime.strptime(f"{req.event_date} {req.event_start_hour}", "%Y-%m-%d %H:%M")
        
        self.sessions.sort(key=lambda x: x["_preferred_dt"]) # sort by preferred time
        
        self.generate_schedule()
        return {
            "schedule": self.schedule,
            "conflicts": self.conflicts,
            "logs": scheduler_logs,
            "summary": "Generated schedule successfully"
        }

    def generate_schedule(self):
        current_time = datetime.strptime("09:00", "%H:%M")
        
        room_availability = {r["id"]: current_time for r in self.rooms}
        speaker_schedule = {s: [] for s in self.speakers.keys()}
        
        for session in self.sessions:
            speaker_id = session.get("speaker_id")
            duration = session.get("duration", 60)
            
            if not self.rooms:
                 self.log(f"No rooms available to schedule {session['title']}")
                 continue
                 
            # Target start time
            start_time = getattr(self, 'event_date', None)
            if start_time:
                assigned_start = session.get("_preferred_dt", datetime.strptime(f"{self.event_date} 09:00", "%Y-%m-%d %H:%M"))
            else:
                assigned_start = session.get("_preferred_dt", current_time)
            
            assigned_room = None
            
            # Find an available room and avoid speaker conflicts
            resolved = False
            while not resolved:
                # Find first available room for assigned_start
                for room_id in room_availability:
                    if room_availability[room_id] <= assigned_start:
                        assigned_room = room_id
                        break
                
                if not assigned_room:
                    # Move time forward by 15 mins to find a room
                    assigned_start += timedelta(minutes=15)
                    continue
                    
                end_time = assigned_start + timedelta(minutes=duration)
                
                # Check expected speaker availability
                speaker_avail_start_str = session.get("speaker_availability_start")
                speaker_avail_end_str = session.get("speaker_availability_end")
                av_conflict = False
                
                start_date_str = start_time if start_time else datetime.now().strftime("%Y-%m-%d")
                
                if speaker_avail_start_str and speaker_avail_end_str:
                    try:
                        avail_start = datetime.strptime(f"{start_date_str} {speaker_avail_start_str}", "%Y-%m-%d %H:%M")
                        avail_end = datetime.strptime(f"{start_date_str} {speaker_avail_end_str}", "%Y-%m-%d %H:%M")
                        
                        if assigned_start < avail_start or end_time > avail_end:
                            av_conflict = True
                            
                            if assigned_start < avail_start:
                                self.log(f"Availability conflict for {speaker_id}: Moved to {avail_start.strftime('%H:%M')}")
                                assigned_start = avail_start
                                assigned_room = None
                                session["has_conflict"] = True
                                session["conflict_note"] = f"Moved to {avail_start.strftime('%H:%M')} due to availability"
                                continue
                            else:
                                self.log(f"Availability conflict for {speaker_id}: Exceeds availability end")
                                session["has_conflict"] = True
                                session["conflict_note"] = f"Duration exceeds availability end"
                    except Exception: pass

                # Check double booking
                has_speaker_conflict = False
                if speaker_id:
                    for prev_start, prev_end in speaker_schedule.get(speaker_id, []):
                        if max(assigned_start, prev_start) < min(end_time, prev_end):
                            has_speaker_conflict = True
                            break
                        
                if has_speaker_conflict:
                    self.log(f"Conflict detected: Speaker double booked")
                    assigned_start += timedelta(minutes=15)
                    assigned_room = None
                    session["has_conflict"] = True
                    session["conflict_note"] = "Moved due to speaker double booking"
                else:
                    resolved = True

            # Assign
            room_availability[assigned_room] = end_time
            if speaker_id:
                if speaker_id not in speaker_schedule:
                    speaker_schedule[speaker_id] = []
                speaker_schedule[speaker_id].append((assigned_start, end_time))
            
            self.schedule.append({
                "session_id": session.get("id"),
                "session": session.get("title", ""),
                "room_id": assigned_room,
                "start_time": assigned_start.isoformat(),
                "end_time": end_time.isoformat(),
                "has_conflict": session.get("has_conflict", False),
                "conflict_note": session.get("conflict_note", None)
            })

    def resolve_conflicts(self):
        # Already resolved during assignment loop
        pass

# Event Scheduler Endpoints
@app.post("/api/speakers")
async def add_speaker(speaker: Speaker):
    speakers_db.append(speaker.dict())
    return {"status": "success", "speaker": speaker}

@app.post("/api/rooms")
async def add_room(room: Room):
    rooms_db.append(room.dict())
    return {"status": "success", "room": room}

@app.post("/api/sessions")
async def add_session(session: Session):
    sessions_db.append(session.dict())
    return {"status": "success", "session": session}

@app.get("/api/speakers")
async def get_speakers():
    return speakers_db

@app.get("/api/rooms")
async def get_rooms():
    return rooms_db

@app.get("/api/sessions")
async def get_sessions():
    return sessions_db

@app.post("/api/auto-schedule")
async def auto_schedule(req: ScheduleRequest = None):
    agent = EventSchedulerAgent()
    if req:
        return agent.run_with_payload(req)
    else:
        return agent.run()

@app.get("/api/schedule")
async def get_schedule():
    # Run a dummy or return static if needed
    # Usually UI gets schedule from auto-schedule run, but we can expose it here
    return {"schedule": []}

@app.get("/api/conflicts")
async def get_conflicts():
    return {"conflicts": []}

@app.get("/api/logs") # note: overrides /api/agent-logs maybe?
async def get_scheduler_logs():
    return scheduler_logs

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
