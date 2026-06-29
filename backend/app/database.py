"""Database module — SQLite with schema matching PRODUCT_SPEC.md Section 5"""
import sqlite3
import os
from pathlib import Path
from datetime import datetime, timedelta
import uuid

DB_PATH = Path(__file__).resolve().parent.parent.parent / "optimus_price.db"


def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS hotels (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            hotel_id TEXT REFERENCES hotels(id),
            email TEXT UNIQUE NOT NULL,
            role TEXT CHECK (role IN ('admin', 'guest', 'superadmin')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS reservations (
            id TEXT PRIMARY KEY,
            hotel_id TEXT REFERENCES hotels(id),
            user_id TEXT REFERENCES users(id),
            guest_name TEXT,
            email TEXT,
            phone TEXT,
            check_in DATE NOT NULL,
            check_out DATE NOT NULL,
            nights INTEGER,
            guests INTEGER,
            room_type TEXT,
            meal_plan TEXT,
            lead_time INTEGER,
            season TEXT,
            base_price REAL,
            final_price REAL,
            override_pct REAL DEFAULT 0,
            status TEXT DEFAULT 'confirmed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS price_queries (
            id TEXT PRIMARY KEY,
            hotel_id TEXT REFERENCES hotels(id),
            session_id TEXT,
            features TEXT,
            predicted_price REAL,
            market_adjustment REAL,
            final_price REAL,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS competitor_prices (
            id TEXT PRIMARY KEY,
            hotel_id TEXT REFERENCES hotels(id),
            ota TEXT NOT NULL,
            price REAL,
            currency TEXT DEFAULT 'EUR',
            raw_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS price_overrides (
            id TEXT PRIMARY KEY,
            hotel_id TEXT REFERENCES hotels(id),
            user_id TEXT REFERENCES users(id),
            modifier_pct REAL,
            reason TEXT,
            active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS alerts (
            id TEXT PRIMARY KEY,
            hotel_id TEXT REFERENCES hotels(id),
            type TEXT,
            severity TEXT,
            message TEXT,
            read BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_competitor_hotel_ota ON competitor_prices(hotel_id, ota, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_queries_hotel_date ON price_queries(hotel_id, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_reservations_hotel ON reservations(hotel_id, created_at DESC);
    """)

    conn.commit()
    conn.close()
    print(f"[OK] Database initialized at {DB_PATH}")


def seed_data():
    conn = get_db()
    cur = conn.cursor()

    hotel_id = str(uuid.uuid4())

    # Hotels
    cur.execute("INSERT OR IGNORE INTO hotels (id, name, slug) VALUES (?, ?, ?)",
                (hotel_id, "Demo Hotel Boutique", "demo-hotel"))

    # Users
    cur.execute("""INSERT OR IGNORE INTO users (id, hotel_id, email, role) VALUES (?, ?, ?, ?)""",
                (str(uuid.uuid4()), hotel_id, "admin@demohotel.com", "admin"))

    # Alerts
    alerts = [
        (str(uuid.uuid4()), hotel_id, "price_drop", "critical", "Booking.com dropped 12% below your price", 0),
        (str(uuid.uuid4()), hotel_id, "competitor", "critical", "Expedia updated pricing for Aug 15-20", 0),
        (str(uuid.uuid4()), hotel_id, "occupancy", "warning", "Occupancy forecast exceeds 90% for next week", 0),
    ]
    cur.executemany("INSERT OR IGNORE INTO alerts (id, hotel_id, type, severity, message, read) VALUES (?, ?, ?, ?, ?, ?)", alerts)

    # Competitor prices — last 7 days
    today = datetime.now()
    otas = ["Booking.com", "Expedia", "Hotels.com", "Trivago"]
    base_prices = {"Booking.com": 168, "Expedia": 171, "Hotels.com": 176, "Trivago": 166}
    for i in range(7):
        day = today - timedelta(days=6 - i)
        for ota in otas:
            variation = (i * 0.5) + ((hash(ota + str(i)) % 10) - 5) * 0.3
            price = round(base_prices[ota] + variation, 2)
            cur.execute(
                "INSERT OR IGNORE INTO competitor_prices (id, hotel_id, ota, price, currency, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), hotel_id, ota, price, "EUR", day.isoformat())
            )

    # Price queries (trend data)
    for i in range(7):
        day = today - timedelta(days=6 - i)
        price = round(168 + i * 3.5 + (hash(str(i)) % 10) * 0.2, 2)
        cur.execute(
            "INSERT OR IGNORE INTO price_queries (id, hotel_id, predicted_price, source, created_at) VALUES (?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), hotel_id, price, "ml_model", day.isoformat())
        )

    # Reservations
    reservations = [
        (str(uuid.uuid4()), hotel_id, "Juan Pérez", "juan@example.com", "2026-08-15", "2026-08-18", 3, 2, "Double", "Bed & Breakfast", 30, "peak", 180, 540, "confirmed"),
        (str(uuid.uuid4()), hotel_id, "María Gómez", "maria@example.com", "2026-09-01", "2026-09-03", 2, 1, "Single", "Room Only", 45, "shoulder", 160, 320, "confirmed"),
        (str(uuid.uuid4()), hotel_id, "Carlos Ruiz", "carlos@example.com", "2026-07-28", "2026-08-02", 5, 4, "Suite", "Half Board", 14, "peak", 178, 890, "pending"),
        (str(uuid.uuid4()), hotel_id, "Ana López", "ana@example.com", "2026-08-03", "2026-08-04", 1, 2, "Double", "Bed & Breakfast", 7, "peak", 175, 175, "confirmed"),
        (str(uuid.uuid4()), hotel_id, "Pedro Sánchez", "pedro@example.com", "2026-08-20", "2026-08-22", 2, 3, "Triple", "Full Board", 60, "peak", 205, 410, "cancelled"),
    ]
    for r in reservations:
        cur.execute("""INSERT OR IGNORE INTO reservations 
            (id, hotel_id, guest_name, email, check_in, check_out, nights, guests, room_type, meal_plan, lead_time, season, base_price, final_price, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", r)

    conn.commit()
    conn.close()
    print(f"[OK] Seed data inserted for hotel '{hotel_id}'")
    return hotel_id


if __name__ == "__main__":
    init_db()
    seed_data()
