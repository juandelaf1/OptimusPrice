import numpy as np
import pandas as pd
from numpy.random import Generator, PCG64
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class HotelDataGenerator:
    """Genera datos sintéticos realistas para pequeños hoteles/pensiones."""

    SEASON_MULTIPLIER = {
        1: 0.70, 2: 0.65, 3: 0.75,
        4: 0.85, 5: 0.90, 6: 1.25,
        7: 1.40, 8: 1.35, 9: 0.95,
        10: 0.85, 11: 0.75, 12: 1.20,
    }

    ROOM_BASE_PRICES = {
        "Room_Type 1": 0,
        "Room_Type 2": 10,
        "Room_Type 3": 20,
        "Room_Type 4": 15,
        "Room_Type 5": 25,
        "Room_Type 6": 35,
        "Room_Type 7": 50,
    }

    ROOM_TYPES = list(ROOM_BASE_PRICES.keys())
    MEAL_PLANS = ["Not Selected", "Meal Plan 1", "Meal Plan 2", "Meal Plan 3"]
    MARKET_SEGMENTS = ["Online", "Offline", "Corporate", "Complementary", "Aviation"]

    def __init__(self, seed: int = 42, base_price: float = 55.0):
        self.rng = Generator(PCG64(seed))
        self.base_price = base_price

    def _random_date(self, year: int) -> pd.Timestamp:
        start = pd.Timestamp(f"{year}-01-01")
        end = pd.Timestamp(f"{year}-12-31")
        return start + pd.Timedelta(days=self.rng.integers(0, (end - start).days + 1))

    def _season_factor(self, month: int) -> float:
        return self.SEASON_MULTIPLIER.get(month, 1.0)

    def generate(self, n_samples: int = 30000, years: list | None = None) -> pd.DataFrame:
        if years is None:
            years = [2024, 2025, 2026]

        records = []
        samples_per_year = max(1, n_samples // len(years))

        for year in years:
            for _ in range(samples_per_year):
                arrival_date = self._random_date(year)

                no_of_adults = self.rng.choice([1, 2, 3, 4], p=[0.15, 0.60, 0.20, 0.05])
                no_of_children = self.rng.choice([0, 1, 2, 3], p=[0.70, 0.20, 0.08, 0.02])

                weekend_nights = self.rng.integers(0, 4)
                week_nights = self.rng.integers(0, 8)
                total_nights = weekend_nights + week_nights

                lead_time = int(self.rng.exponential(60))
                lead_time = min(max(lead_time, 0), 365)

                room_type = self.rng.choice(self.ROOM_TYPES,
                    p=[0.25, 0.30, 0.20, 0.10, 0.08, 0.05, 0.02])
                meal_plan = self.rng.choice(self.MEAL_PLANS,
                    p=[0.30, 0.35, 0.20, 0.15])

                market = self.rng.choice(self.MARKET_SEGMENTS,
                    p=[0.45, 0.25, 0.15, 0.10, 0.05])

                repeated = self.rng.choice([0, 1], p=[0.70, 0.30])
                prev_cancellations = int(self.rng.exponential(0.5)) if repeated else 0
                prev_bookings = int(self.rng.exponential(3)) if repeated else 0

                parking = int(self.rng.random() < 0.25)
                special_requests = int(self.rng.poisson(0.8))

                booking_status = self.rng.choice(["Not_Canceled", "Canceled"],
                    p=[0.73, 0.27])

                price = self._compute_price(
                    room_type=room_type,
                    meal_plan=meal_plan,
                    month=arrival_date.month,
                    is_weekend=arrival_date.weekday() >= 5,
                    total_nights=total_nights,
                    lead_time=lead_time,
                    adults=no_of_adults,
                    children=no_of_children,
                    parking=parking,
                    special_requests=special_requests,
                    market=market,
                )

                records.append({
                    "Booking_ID": f"RES{year}{self.rng.integers(10000, 99999)}",
                    "no_of_adults": no_of_adults,
                    "no_of_children": no_of_children,
                    "no_of_weekend_nights": weekend_nights,
                    "no_of_week_nights": week_nights,
                    "type_of_meal_plan": meal_plan,
                    "room_type_reserved": room_type,
                    "lead_time": lead_time,
                    "arrival_year": arrival_date.year,
                    "arrival_month": arrival_date.month,
                    "arrival_date": arrival_date.day,
                    "market_segment_type": market,
                    "repeated_guest": repeated,
                    "no_of_previous_cancellations": prev_cancellations,
                    "no_of_previous_bookings_not_canceled": prev_bookings,
                    "booking_status": booking_status,
                    "required_car_parking": parking,
                    "special_requests": special_requests,
                    "avg_price_per_room": round(price, 2),
                })

        df = pd.DataFrame(records)
        return df.sample(frac=1, random_state=self.rng.integers(9999)).reset_index(drop=True)

    def _compute_price(
        self, room_type: str, meal_plan: str, month: int,
        is_weekend: bool, total_nights: int, lead_time: int,
        adults: int, children: int, parking: int,
        special_requests: int, market: str,
    ) -> float:
        price = self.base_price
        price *= self._season_factor(month)
        if is_weekend:
            price *= 1.15
        price += self.ROOM_BASE_PRICES.get(room_type, 0)
        meal_bonus = {"Not Selected": 0, "Meal Plan 1": 5, "Meal Plan 2": 12, "Meal Plan 3": 20}
        price += meal_bonus.get(meal_plan, 0) * max(1, adults + children * 0.5)
        if lead_time > 180:
            price *= 0.90
        elif lead_time < 3:
            price *= 1.08
        if total_nights >= 7:
            price *= 0.92
        if parking:
            price += 5
        price += special_requests * 3
        market_mult = {"Online": 1.0, "Offline": 0.98, "Corporate": 0.92,
                       "Complementary": 0.85, "Aviation": 0.95}
        price *= market_mult.get(market, 1.0)
        noise = self.rng.normal(1.0, 0.12)
        price *= noise
        return max(price, 15.0)

    def generate_and_save(self, n_samples: int = 30000, data_dir: str | None = None) -> str:
        if data_dir is None:
            data_dir = os.path.join(BASE_DIR, "data", "raw")
        os.makedirs(data_dir, exist_ok=True)
        df = self.generate(n_samples)
        path = os.path.join(data_dir, "Hotel Reservations.csv")
        df.to_csv(path, index=False)
        print(f"Datos generados: {path} ({len(df)} registros)")
        return path


if __name__ == "__main__":
    gen = HotelDataGenerator()
    gen.generate_and_save()
