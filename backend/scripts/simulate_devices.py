import argparse
import json
import random
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime

import paho.mqtt.client as mqtt


@dataclass
class PumpSimulationState:
    station_id: str
    pump_id: str
    device_id: str
    attendant_id: str
    price_per_liter: int = 972
    active: bool = False
    liters: float = 0
    amount: float = 0
    pulse_count: int = 0
    duration_seconds: int = 0
    anomaly_mode: str | None = None
    last_pulse: int = 0
    started_at: float = field(default_factory=time.time)


class DeviceSimulator:
    def __init__(self, host: str, port: int, interval: float) -> None:
        self.host = host
        self.port = port
        self.interval = interval
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.random = random.Random(7)
        self.states = self._build_states()

    def _build_states(self) -> list[PumpSimulationState]:
        stations = ["STA001", "STA002", "STA003"]
        attendants = [f"ATT{i:03d}" for i in range(1, 21)]
        states: list[PumpSimulationState] = []
        for index in range(20):
            station_id = stations[index % len(stations)]
            states.append(
                PumpSimulationState(
                    station_id=station_id,
                    pump_id=f"PUMP{index + 1:02d}",
                    device_id=f"DEV{index + 1:03d}",
                    attendant_id=self.random.choice(attendants),
                    price_per_liter=self.random.choice([940, 955, 972, 985]),
                )
            )
        return states

    def connect(self) -> None:
        self.client.connect(self.host, self.port, 60)
        self.client.loop_start()

    def disconnect(self) -> None:
        self.client.loop_stop()
        self.client.disconnect()

    def publish(self, topic: str, payload: dict) -> None:
        self.client.publish(topic, json.dumps(payload), qos=0)

    def run(self) -> None:
        print(f"Publishing simulator traffic to mqtt://{self.host}:{self.port}")
        self.connect()
        try:
            while True:
                for state in self.states:
                    self._tick_state(state)
                time.sleep(self.interval)
        except KeyboardInterrupt:
            print("Simulator stopped.")
        finally:
            self.disconnect()

    def _tick_state(self, state: PumpSimulationState) -> None:
        if self.random.random() < 0.02:
            return

        if not state.active and self.random.random() < 0.18:
            state.active = True
            state.started_at = time.time()
            state.liters = 0
            state.amount = 0
            state.duration_seconds = 0
            state.pulse_count = 0
            state.last_pulse = 0
            state.attendant_id = f"ATT{self.random.randint(1, 35):03d}"
            state.anomaly_mode = self.random.choices(
                [None, "low_pulse", "stalled_pulse", "meter_reset"],
                weights=[85, 7, 5, 3],
            )[0]

        if state.active:
            pulse_increment = self.random.randint(35, 120)
            liters_increment = pulse_increment / 100
            if state.anomaly_mode == "low_pulse":
                liters_increment = pulse_increment / self.random.uniform(45, 70)
            elif state.anomaly_mode == "stalled_pulse" and self.random.random() < 0.6:
                pulse_increment = 0
                liters_increment = self.random.uniform(0.2, 0.8)
            elif state.anomaly_mode == "meter_reset" and self.random.random() < 0.05:
                state.pulse_count = max(0, state.pulse_count - self.random.randint(80, 180))

            state.pulse_count += pulse_increment
            state.liters = round(state.liters + liters_increment, 2)
            state.amount = round(state.liters * state.price_per_liter, 2)
            state.duration_seconds = int(time.time() - state.started_at)

            telemetry_payload = {
                "device_id": state.device_id,
                "pump_id": state.pump_id,
                "pulse_count": state.pulse_count,
                "flowing": True,
                "voltage": round(self.random.uniform(11.1, 12.6), 2),
                "rssi": self.random.randint(-82, -53),
                "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            }
            self.publish(f"fuel/{state.station_id}/{state.pump_id}/telemetry", telemetry_payload)

            should_finish = state.liters >= self.random.uniform(6, 45) or state.duration_seconds > 95
            if should_finish:
                transaction_payload = {
                    "pump_id": state.pump_id,
                    "liters": state.liters,
                    "amount": state.amount,
                    "price_per_liter": state.price_per_liter,
                    "pulse_count": state.pulse_count,
                    "duration_seconds": max(state.duration_seconds, 1),
                    "attendant_id": state.attendant_id,
                    "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                }
                self.publish(
                    f"fuel/{state.station_id}/{state.pump_id}/transaction",
                    transaction_payload,
                )
                state.active = False
        else:
            telemetry_payload = {
                "device_id": state.device_id,
                "pump_id": state.pump_id,
                "pulse_count": state.pulse_count,
                "flowing": False,
                "voltage": round(self.random.uniform(11.4, 12.7), 2),
                "rssi": self.random.randint(-80, -50),
                "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            }
            self.publish(f"fuel/{state.station_id}/{state.pump_id}/telemetry", telemetry_payload)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SmartFMD device simulator")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", default=1883, type=int)
    parser.add_argument("--interval", default=1.0, type=float)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    DeviceSimulator(args.host, args.port, args.interval).run()

