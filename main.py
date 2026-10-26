"""API FastAPI pentru simulatorul PID + pagina web.

Pornire (din folderul proiectului):
    python -m uvicorn main:app --reload
apoi deschide http://127.0.0.1:8000
Documentatia automata a API-ului: http://127.0.0.1:8000/docs
"""
from pathlib import Path
from typing import Literal, Optional

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from pid_core import PIDSimulator

AICI = Path(__file__).resolve().parent

app = FastAPI(
    title="PID Simulator API",
    description="Simulează un regulator PID pe un motor și întoarce răspunsul și metricile.",
    version="1.0",
)


class SimulationRequest(BaseModel):
    kp: float = Field(2.0, ge=0, le=100, description="Câștig proporțional")
    ki: float = Field(0.1, ge=0, le=100, description="Câștig integral")
    kd: float = Field(0.05, ge=0, le=10, description="Câștig derivativ")
    setpoint: float = Field(1.0, gt=0, le=10000, description="Valoarea dorită (viteza)")
    model: Literal["simple", "dc_motor"] = Field(
        "simple", description="simple = modelul original; dc_motor = modelul din Motor.cs (Unity)")
    duration: float = Field(5.0, gt=0, le=60, description="Durata simulării (s)")
    dt: float = Field(0.1, ge=0.001, le=1, description="Pasul de timp (s)")
    max_rpm: float = Field(312.0, gt=0, le=20000, description="dc_motor: turația maximă")
    time_constant: float = Field(0.08, gt=0, le=10, description="dc_motor: constanta de timp (s)")


class Metrics(BaseModel):
    rise_time: Optional[float]
    overshoot: Optional[float]
    overshoot_percent: Optional[float] = None
    settling_time: Optional[float]
    steady_state_error: Optional[float]


class SimulationResponse(BaseModel):
    time: list[float]
    value: list[float]
    control: list[float]
    setpoint: float
    metrics: Metrics


@app.post("/api/simulate", response_model=SimulationResponse)
def simulate(req: SimulationRequest):
    steps = int(round(req.duration / req.dt))
    steps = max(1, min(steps, 20000))  # limita, ca un request sa nu blocheze serverul

    sim = PIDSimulator(req.kp, req.ki, req.kd, req.setpoint, dt=req.dt,
                       model=req.model, max_rpm=req.max_rpm,
                       time_constant=req.time_constant)
    timp, valori = sim.run(steps)

    return SimulationResponse(
        time=[round(t, 4) for t in timp],
        value=[round(v, 5) for v in valori],
        control=[round(u, 5) for u in sim.comenzi],
        setpoint=req.setpoint,
        metrics=Metrics(**sim.metrics()),
    )


@app.get("/api/health")
def health():
    return {"status": "ok"}


app.mount("/static", StaticFiles(directory=AICI / "static"), name="static")


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(AICI / "static" / "index.html")
