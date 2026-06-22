# -*- coding: utf-8 -*-
"""
Optimus Price — Shared Database Layer
SQLite backend connecting admin, client, and monitoring modules
Enables data ingestion for ML retraining
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import contextmanager

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DB_PATH = os.path.join(DB_DIR, "optimus_price.db")


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_db() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT DEFAULT (datetime('now')),
                nombre TEXT, email TEXT, telefono TEXT,
                documento TEXT, nacionalidad TEXT,
                tipo_cliente TEXT DEFAULT 'Normal',
                fecha_llegada TEXT, fecha_salida TEXT,
                noches INTEGER, tipo_habitacion TEXT,
                huespedes INTEGER, plan_comidas TEXT,
                solicitudes_especiales TEXT,
                estacionamiento INTEGER DEFAULT 0,
                precio_noche REAL, precio_total REAL,
                lead_time INTEGER, temporada TEXT,
                override_modifier REAL DEFAULT 0,
                precio_final REAL,
                source TEXT DEFAULT 'customer_portal'
            );

            CREATE TABLE IF NOT EXISTS price_queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT DEFAULT (datetime('now')),
                session_id TEXT,
                total_guests INTEGER, total_nights INTEGER,
                lead_time INTEGER, arrival_month INTEGER,
                room_type TEXT, meal_plan TEXT,
                predicted_price REAL,
                market_adjustment REAL DEFAULT 0,
                final_price REAL,
                competitor_prices TEXT DEFAULT '{}',
                source TEXT DEFAULT 'customer_portal'
            );

            CREATE TABLE IF NOT EXISTS price_overrides (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT DEFAULT (datetime('now')),
                admin_user TEXT,
                modifier_percent REAL,
                reason TEXT,
                active INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS competitor_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT DEFAULT (datetime('now')),
                hotel_id TEXT,
                ota TEXT,
                price REAL,
                currency TEXT DEFAULT 'EUR',
                raw_response TEXT
            );

            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT DEFAULT (datetime('now')),
                session_id TEXT,
                query_id INTEGER,
                rating INTEGER,
                comment TEXT,
                accepted_price INTEGER DEFAULT 0
            );

            CREATE INDEX IF NOT EXISTS idx_queries_date ON price_queries(created_at);
            CREATE INDEX IF NOT EXISTS idx_reservations_date ON reservations(created_at);
            CREATE INDEX IF NOT EXISTS idx_competitor_hotel ON competitor_snapshots(hotel_id);
        """)


class OptimusDB:
    """Shared database for Optimus Price platform"""

    def __init__(self):
        os.makedirs(DB_DIR, exist_ok=True)
        init_db()

    # ---- Reservations ----
    def save_reservation(self, data: Dict) -> int:
        with get_db() as db:
            cur = db.execute("""
                INSERT INTO reservations (
                    nombre, email, telefono, documento, nacionalidad,
                    tipo_cliente, fecha_llegada, fecha_salida,
                    noches, tipo_habitacion, huespedes, plan_comidas,
                    solicitudes_especiales, estacionamiento,
                    precio_noche, precio_total, lead_time, temporada,
                    override_modifier, precio_final, source
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                data.get("nombre"), data.get("email"), data.get("telefono"),
                data.get("documento"), data.get("nacionalidad", "Española"),
                data.get("tipo_cliente", "Normal"),
                data.get("fecha_llegada"), data.get("fecha_salida"),
                data.get("noches"), data.get("tipo_habitacion"),
                data.get("huespedes"), data.get("plan_comidas"),
                data.get("solicitudes_especiales", ""),
                int(data.get("estacionamiento", False)),
                data.get("precio_noche", 0), data.get("precio_total", 0),
                data.get("lead_time", 0), data.get("temporada", ""),
                data.get("override_modifier", 0),
                data.get("precio_final", data.get("precio_total", 0)),
                data.get("source", "customer_portal")
            ))
            return cur.lastrowid

    def get_reservations(self, limit: int = 100) -> List[Dict]:
        with get_db() as db:
            rows = db.execute("SELECT * FROM reservations ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
            return [dict(r) for r in rows]

    def get_reservation_stats(self) -> Dict:
        with get_db() as db:
            total = db.execute("SELECT COUNT(*) FROM reservations").fetchone()[0]
            revenue = db.execute("SELECT COALESCE(SUM(precio_total), 0) FROM reservations").fetchone()[0]
            avg_price = db.execute("SELECT COALESCE(AVG(precio_noche), 0) FROM reservations WHERE precio_noche > 0").fetchone()[0]
            return {"total_reservations": total, "total_revenue": revenue, "avg_price_per_night": avg_price}

    # ---- Price Queries ----
    def save_query(self, data: Dict) -> int:
        comp_prices = data.get("competitor_prices", {})
        with get_db() as db:
            cur = db.execute("""
                INSERT INTO price_queries (
                    session_id, total_guests, total_nights,
                    lead_time, arrival_month, room_type, meal_plan,
                    predicted_price, market_adjustment, final_price,
                    competitor_prices, source
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                data.get("session_id", ""), data.get("total_guests", 2),
                data.get("total_nights", 1), data.get("lead_time", 30),
                data.get("arrival_month", 7), data.get("room_type", ""),
                data.get("meal_plan", ""), data.get("predicted_price", 0),
                data.get("market_adjustment", 0), data.get("final_price", 0),
                json.dumps(comp_prices), data.get("source", "customer_portal")
            ))
            return cur.lastrowid

    def get_queries(self, limit: int = 100) -> List[Dict]:
        with get_db() as db:
            rows = db.execute("SELECT * FROM price_queries ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
            result = []
            for r in rows:
                d = dict(r)
                try:
                    d["competitor_prices"] = json.loads(d["competitor_prices"])
                except (json.JSONDecodeError, TypeError):
                    d["competitor_prices"] = {}
                result.append(d)
            return result

    def get_query_stats(self) -> Dict:
        with get_db() as db:
            total = db.execute("SELECT COUNT(*) FROM price_queries").fetchone()[0]
            today = datetime.now().strftime("%Y-%m-%d")
            today_q = db.execute("SELECT COUNT(*) FROM price_queries WHERE created_at >= ?", (today,)).fetchone()[0]
            return {"total_queries": total, "queries_today": today_q}

    # ---- Price Overrides ----
    def save_override(self, modifier: float, reason: str = "", admin: str = "admin") -> int:
        with get_db() as db:
            db.execute("UPDATE price_overrides SET active=0 WHERE active=1")
            cur = db.execute(
                "INSERT INTO price_overrides (admin_user, modifier_percent, reason) VALUES (?,?,?)",
                (admin, modifier, reason)
            )
            return cur.lastrowid

    def get_active_override(self) -> Optional[Dict]:
        with get_db() as db:
            row = db.execute("SELECT * FROM price_overrides WHERE active=1 ORDER BY created_at DESC LIMIT 1").fetchone()
            return dict(row) if row else None

    def get_override_history(self, limit: int = 20) -> List[Dict]:
        with get_db() as db:
            rows = db.execute("SELECT * FROM price_overrides ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
            return [dict(r) for r in rows]

    # ---- Competitor Snapshots ----
    def save_competitor_price(self, hotel_id: str, ota: str, price: float, currency: str = "EUR", raw: str = "") -> int:
        with get_db() as db:
            cur = db.execute(
                "INSERT INTO competitor_snapshots (hotel_id, ota, price, currency, raw_response) VALUES (?,?,?,?,?)",
                (hotel_id, ota, price, currency, raw)
            )
            return cur.lastrowid

    def get_latest_competitor_prices(self, hotel_id: str) -> List[Dict]:
        with get_db() as db:
            rows = db.execute("""
                SELECT ota, price, currency, created_at FROM competitor_snapshots
                WHERE hotel_id = ? AND created_at >= datetime('now', '-1 day')
                ORDER BY created_at DESC
            """, (hotel_id,)).fetchall()
            return [dict(r) for r in rows]

    # ---- Feedback ----
    def save_feedback(self, session_id: str, query_id: int, rating: int, comment: str = "", accepted: bool = False) -> int:
        with get_db() as db:
            cur = db.execute(
                "INSERT INTO feedback (session_id, query_id, rating, comment, accepted_price) VALUES (?,?,?,?,?)",
                (session_id, query_id, rating, comment, int(accepted))
            )
            return cur.lastrowid

    # ---- Export for ML ----
    def export_for_training(self, output_path: str = None) -> str:
        """Export price queries + reservations as a training dataset"""
        import pandas as pd
        queries = self.get_queries(limit=10000)
        df = pd.DataFrame(queries)
        if not df.empty:
            df = df.drop(columns=["competitor_prices", "session_id", "source"], errors="ignore")
        if output_path is None:
            output_path = os.path.join(DB_DIR, "processed", "db_training_data.csv")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        return output_path


# Singleton instance
db = OptimusDB()
