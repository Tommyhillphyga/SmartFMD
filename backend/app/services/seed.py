import random
from datetime import UTC, datetime, timedelta

from faker import Faker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import AlertSeverity, DeviceStatus, PumpStatus, Role
from app.core.security import hash_password
from app.models import Alert, Company, Device, Nozzle, Pump, Station, TelemetryLog, Transaction, User

try:
    fake = Faker("en_NG")
except AttributeError:
    fake = Faker("en_GB")


async def seed_database(session: AsyncSession) -> dict[str, int]:
    existing = (await session.execute(select(Company))).scalars().first()
    if existing:
        return {"companies": 0, "stations": 0, "pumps": 0, "users": 0, "transactions": 0}

    rng = random.Random(42)
    company = Company(id="COM001", name="SmartFMD Petroleum Holdings")
    session.add(company)

    stations = [
        Station(
            id="STA001",
            company_id=company.id,
            name="Lekki Phase 1 Station",
            location="Admiralty Way, Lekki",
            city="Lagos",
        ),
        Station(
            id="STA002",
            company_id=company.id,
            name="Ikeja Central Station",
            location="Allen Avenue, Ikeja",
            city="Lagos",
        ),
        Station(
            id="STA003",
            company_id=company.id,
            name="GRA Port Harcourt Station",
            location="Old GRA, Port Harcourt",
            city="Port Harcourt",
        ),
    ]
    session.add_all(stations)

    pumps: list[Pump] = []
    nozzles: list[Nozzle] = []
    devices: list[Device] = []
    station_pump_map = {
        "STA001": range(1, 8),
        "STA002": range(8, 15),
        "STA003": range(15, 21),
    }
    for station_id, pump_numbers in station_pump_map.items():
        for pump_number in pump_numbers:
            pump_id = f"PUMP{pump_number:02d}"
            pump = Pump(
                id=pump_id,
                station_id=station_id,
                name=f"Pump {pump_number:02d}",
                status=PumpStatus.IDLE,
                product_name="PMS",
                totalizer_liters=0,
                totalizer_amount=0,
            )
            nozzle = Nozzle(
                id=f"NOZ{pump_number:02d}",
                pump_id=pump_id,
                label="A",
                fuel_type="PMS",
                price_per_liter=972,
            )
            device = Device(
                id=f"DEV{pump_number:03d}",
                station_id=station_id,
                pump_id=pump_id,
                firmware_version=f"1.0.{pump_number % 5}",
                status=DeviceStatus.ONLINE,
                rssi=rng.randint(-78, -55),
                voltage=round(rng.uniform(11.5, 12.5), 2),
            )
            pumps.append(pump)
            nozzles.append(nozzle)
            devices.append(device)
    session.add_all(pumps + nozzles + devices)

    users: list[User] = [
        User(
            id="USRADMIN",
            company_id=company.id,
            station_id=None,
            full_name="Super Admin",
            email="admin@example.com",
            hashed_password=hash_password("Admin123!"),
            role=Role.SUPER_ADMIN,
        )
    ]
    owners = 3
    managers = 6
    attendants = 35
    auditors = 5
    user_counter = 1
    for index in range(owners):
        station = stations[index]
        user_counter += 1
        users.append(
            User(
                id=f"USR{user_counter:03d}",
                company_id=company.id,
                station_id=station.id,
                full_name=f"{station.city} Owner {index + 1}",
                email=f"owner{index + 1}@example.com",
                hashed_password=hash_password("Password123!"),
                role=Role.STATION_OWNER,
            )
        )
    for index in range(managers):
        station = stations[index % len(stations)]
        user_counter += 1
        users.append(
            User(
                id=f"USR{user_counter:03d}",
                company_id=company.id,
                station_id=station.id,
                full_name=fake.name(),
                email=f"manager{index + 1}@example.com",
                hashed_password=hash_password("Password123!"),
                role=Role.MANAGER,
            )
        )
    for index in range(attendants):
        station = stations[index % len(stations)]
        user_counter += 1
        users.append(
            User(
                id=f"ATT{index + 1:03d}",
                company_id=company.id,
                station_id=station.id,
                full_name=fake.name(),
                email=f"attendant{index + 1}@example.com",
                hashed_password=hash_password("Password123!"),
                role=Role.ATTENDANT,
            )
        )
    for index in range(auditors):
        station = stations[index % len(stations)]
        user_counter += 1
        users.append(
            User(
                id=f"USR{user_counter:03d}",
                company_id=company.id,
                station_id=station.id,
                full_name=fake.name(),
                email=f"auditor{index + 1}@example.com",
                hashed_password=hash_password("Password123!"),
                role=Role.AUDITOR,
            )
        )
    session.add_all(users)

    attendants_by_station = {
        station.id: [user for user in users if user.station_id == station.id and user.role == Role.ATTENDANT]
        for station in stations
    }
    nozzle_by_pump = {nozzle.pump_id: nozzle for nozzle in nozzles}
    device_by_pump = {device.pump_id: device for device in devices}
    station_by_pump = {pump.id: pump.station_id for pump in pumps}

    transactions: list[Transaction] = []
    now = datetime.now(UTC)
    for index in range(5000):
        pump = rng.choice(pumps)
        station_id = station_by_pump[pump.id]
        nozzle = nozzle_by_pump[pump.id]
        device = device_by_pump[pump.id]
        price = rng.choice([940, 955, 965, 972, 985, 995])
        liters = round(rng.uniform(4.5, 52.0), 2)
        duration = rng.randint(18, 220)
        pulse_count = int(liters * 100)
        if rng.random() < 0.03:
            pulse_count = int(liters * rng.uniform(48, 72))
        if rng.random() < 0.02:
            duration = rng.randint(3, 8)
        end_time = now - timedelta(
            days=rng.randint(0, 29),
            hours=rng.randint(0, 23),
            minutes=rng.randint(0, 59),
            seconds=rng.randint(0, 59),
        )
        start_time = end_time - timedelta(seconds=duration)
        amount = round(liters * price, 2)
        attendant = rng.choice(attendants_by_station[station_id])
        transactions.append(
            Transaction(
                id=f"TXN{index + 1:05d}",
                station_id=station_id,
                pump_id=pump.id,
                nozzle_id=nozzle.id,
                device_id=device.id,
                attendant_id=attendant.id,
                start_time=start_time,
                end_time=end_time,
                liters=liters,
                price_per_liter=price,
                amount=amount,
                pulse_count=pulse_count,
                duration_seconds=duration,
            )
        )
        pump.totalizer_liters += liters
        pump.totalizer_amount += amount
    session.add_all(transactions)

    alerts: list[Alert] = []
    for index in range(120):
        pump = rng.choice(pumps)
        severity = rng.choice(
            [AlertSeverity.LOW, AlertSeverity.MEDIUM, AlertSeverity.CRITICAL]
        )
        alerts.append(
            Alert(
                id=f"ALT{index + 1:04d}",
                station_id=pump.station_id,
                pump_id=pump.id,
                device_id=device_by_pump[pump.id].id,
                severity=severity,
                rule_name=rng.choice(
                    [
                        "abnormally_low_pulses_per_liter",
                        "too_many_short_transactions",
                        "device_offline_during_active_hours",
                        "sudden_meter_reset",
                    ]
                ),
                message=f"Seeded {severity.value} alert for {pump.name}",
                metadata_json={"seeded": True},
            )
        )
    session.add_all(alerts)

    telemetry_logs: list[TelemetryLog] = []
    for pump in pumps:
        device = device_by_pump[pump.id]
        timestamp = now - timedelta(seconds=rng.randint(5, 180))
        telemetry_logs.append(
            TelemetryLog(
                station_id=pump.station_id,
                pump_id=pump.id,
                device_id=device.id,
                pulse_count=rng.randint(1000, 9000),
                flowing=rng.random() < 0.2,
                voltage=device.voltage,
                rssi=device.rssi,
                timestamp=timestamp,
            )
        )
        device.last_heartbeat = timestamp
    session.add_all(telemetry_logs)

    await session.commit()
    return {
        "companies": 1,
        "stations": len(stations),
        "pumps": len(pumps),
        "users": len(users),
        "transactions": len(transactions),
        "alerts": len(alerts),
    }
