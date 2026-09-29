import sqlite3
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "krishisetu.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize SQLite database for field and crop analyses."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS field_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_type TEXT NOT NULL, -- 'crop' or 'field'
                timestamp TEXT NOT NULL,
                crop_name TEXT,
                variety TEXT,
                growth_stage TEXT,
                overall_health TEXT,
                health_score INTEGER,
                health_confidence TEXT,
                primary_issue TEXT,
                severity TEXT,
                issue_confidence INTEGER,
                symptoms TEXT, -- JSON array
                causes TEXT, -- JSON array
                recommendations TEXT, -- JSON array
                soil_condition TEXT, -- JSON object
                weather_context TEXT, -- JSON object
                satellite_context TEXT, -- JSON object
                field_name TEXT,
                gps_lat REAL,
                gps_lon REAL,
                image_count INTEGER DEFAULT 1,
                quality_passed INTEGER DEFAULT 1,
                quality_notes TEXT
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                phone TEXT,
                location TEXT,
                crop TEXT,
                created_at TEXT NOT NULL
            );
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_email
            ON users(email);
        """)
        conn.commit()

# Initialize tables on import
init_db()

def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new registered farmer user in the database."""
    now = datetime.now().isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (name, email, password, phone, location, crop, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_data.get("name", "").strip(),
            user_data.get("email", "").strip().lower(),
            user_data.get("password", ""),
            user_data.get("phone", ""),
            user_data.get("location", ""),
            user_data.get("crop", ""),
            now
        ))
        conn.commit()
        user_id = cursor.lastrowid
        return {
            "id": user_id,
            "name": user_data.get("name", "").strip(),
            "email": user_data.get("email", "").strip().lower(),
            "phone": user_data.get("phone", ""),
            "location": user_data.get("location", ""),
            "crop": user_data.get("crop", "")
        }

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Retrieve user record by email address."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE LOWER(email) = ?", (email.strip().lower(),))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

def _safe_json(val: Optional[str], default: Any) -> Any:
    if not val:
        return default
    try:
        return json.loads(val)
    except Exception:
        return default

def save_analysis_record(data: Dict[str, Any]) -> int:
    """Save an analysis report to the database."""
    now = datetime.now().isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO field_analyses (
                analysis_type, timestamp, crop_name, variety, growth_stage,
                overall_health, health_score, health_confidence,
                primary_issue, severity, issue_confidence,
                symptoms, causes, recommendations,
                soil_condition, weather_context, satellite_context,
                field_name, gps_lat, gps_lon, image_count, quality_passed, quality_notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("analysis_type", "crop"),
            data.get("timestamp", now),
            data.get("crop_name", "Unknown Crop"),
            data.get("variety", ""),
            data.get("growth_stage", ""),
            data.get("overall_health_status") or data.get("overall_health", "Healthy"),
            data.get("overall_health_score") or data.get("field_health_score") or data.get("health_score", 80),
            data.get("health_confidence") or data.get("confidence_level", "MEDIUM"),
            data.get("primary_issue") or data.get("overall_field_status", "None"),
            data.get("severity", "Low"),
            data.get("issue_confidence", 85),
            json.dumps(data.get("symptoms", [])),
            json.dumps(data.get("possible_causes") or data.get("causes", [])),
            json.dumps(data.get("recommended_actions") or data.get("recommendations", [])),
            json.dumps(data.get("visual_field_estimations") or data.get("soil_condition", {})),
            json.dumps(data.get("weather_summary") or data.get("weather_context", {})),
            json.dumps(data.get("satellite_summary") or data.get("satellite_context", {})),
            data.get("field_name", "My Field"),
            data.get("gps_lat"),
            data.get("gps_lon"),
            data.get("image_count", 1),
            1 if data.get("quality_passed", True) else 0,
            data.get("quality_notes", "")
        ))
        conn.commit()
        return cursor.lastrowid

def get_recent_analyses(limit: int = 15) -> List[Dict[str, Any]]:
    """Fetch recent field and crop analysis history with rich normalized fields."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM field_analyses
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            symptoms = _safe_json(row["symptoms"], [])
            causes = _safe_json(row["causes"], [])
            recommendations = _safe_json(row["recommendations"], [])
            soil = _safe_json(row["soil_condition"], {})
            weather = _safe_json(row["weather_context"], {})
            satellite = _safe_json(row["satellite_context"], {})

            score = row["health_score"] or 80
            health_status = row["overall_health"] or "Normal"
            confidence = row["health_confidence"] or "HIGH"
            issue = row["primary_issue"] or "General Assessment"

            results.append({
                "id": row["id"],
                "analysis_type": row["analysis_type"],
                "timestamp": row["timestamp"],
                "crop_name": row["crop_name"],
                "variety": row["variety"] or "",
                "growth_stage": row["growth_stage"] or "",
                "overall_health": health_status,
                "overall_health_status": health_status,
                "health_score": score,
                "overall_health_score": score,
                "field_health_score": score,
                "health_confidence": confidence,
                "confidence_level": confidence,
                "primary_issue": issue,
                "overall_field_status": issue,
                "severity": row["severity"] or "Low",
                "issue_confidence": row["issue_confidence"] or 85,
                "symptoms": symptoms,
                "risk_factors": symptoms,
                "causes": causes,
                "possible_causes": causes,
                "recommendations": recommendations,
                "recommended_actions": recommendations,
                "visual_field_estimations": soil if isinstance(soil, dict) else {},
                "soil_condition": soil,
                "weather_summary": weather if isinstance(weather, dict) else {},
                "weather_context": weather,
                "satellite_summary": satellite if isinstance(satellite, dict) else {},
                "satellite_context": satellite,
                "field_name": row["field_name"] or "My Field",
                "gps_lat": row["gps_lat"],
                "gps_lon": row["gps_lon"],
                "image_count": row["image_count"] or 1,
                "quality_passed": bool(row["quality_passed"])
            })
        return results

def delete_analysis_record(record_id: int) -> bool:
    """Delete a single analysis record by ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM field_analyses WHERE id = ?", (record_id,))
        conn.commit()
        return cursor.rowcount > 0

def clear_all_analyses() -> bool:
    """Clear all analysis records."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM field_analyses")
        conn.commit()
        return True

def get_latest_analysis() -> Optional[Dict[str, Any]]:
    """Retrieve the most recent analysis report to serve as AI chatbot context."""
    records = get_recent_analyses(limit=1)
    return records[0] if records else None

