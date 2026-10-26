"""Nucleul simulatorului PID, fara interfata grafica.

Folosit de:
  - PIDClass.py  (interfata live cu matplotlib)
  - main.py      (API-ul FastAPI + pagina web)

Doua modele de "motor":
  - "simple":   modelul original: iesirea PID schimba direct viteza
                (viteza += (P + I + D) * dt)
  - "dc_motor": acelasi model ca Motor.cs din simulatorul meu Unity:
                iesirea PID e o putere -1..1, iar turatia urmareste
                putere * maxRPM cu o constanta de timp (ordinul I).
"""
import math


class PIDSimulator:
    def __init__(self, kp, ki, kd, setpoint, dt=0.1,
                 model="simple", max_rpm=312.0, time_constant=0.08):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.dt = dt
        self.model = model
        self.max_rpm = max_rpm
        self.time_constant = time_constant
        self.reset()

    def reset(self):
        self.vitezaCurenta = 0
        self.eroareAnterioara = 0
        self.sumaErori = 0
        self.timp = []
        self.viteze = []
        self.comenzi = []  # iesirea regulatorului la fiecare pas

    def step(self):
        """Un singur pas de simulare — folosit de UI (frame cu frame)."""
        if self.model == "dc_motor":
            # eroarea normalizata la turatia maxima, ca in Unity (RUN_WITH_ENCODER)
            eroare = (self.setpoint - self.vitezaCurenta) / self.max_rpm
        else:
            eroare = self.setpoint - self.vitezaCurenta

        P = self.kp * eroare
        self.sumaErori += eroare * self.dt
        I = self.ki * self.sumaErori
        D = self.kd * (eroare - self.eroareAnterioara) / self.dt
        u = P + I + D

        if self.model == "dc_motor":
            u = max(-1.0, min(1.0, u))  # puterea motorului e limitata la -1..1
            alpha = 1 - math.exp(-self.dt / self.time_constant)
            self.vitezaCurenta += (u * self.max_rpm - self.vitezaCurenta) * alpha
        else:
            self.vitezaCurenta += u * self.dt

        self.eroareAnterioara = eroare

        self.timp.append(len(self.timp) * self.dt)
        self.viteze.append(self.vitezaCurenta)
        self.comenzi.append(u)

    def run(self, steps=100):
        """Rulează N pași complet și returnează rezultatul — folosit de API."""
        self.reset()
        for _ in range(steps):
            self.step()
        return self.timp, self.viteze

    def metrics(self):
        """Calculează rise time, overshoot și settling time după un run()."""
        if not self.viteze or self.setpoint == 0:
            return {"rise_time": None, "overshoot": None, "settling_time": None,
                    "steady_state_error": None}

        target = self.setpoint
        rise_time = None
        overshoot = max(self.viteze) - target
        settling_time = None

        # parcurgem de la final spre inceput: ultimul moment in afara benzii de ±2%
        band = 0.02 * abs(target)
        last_outside = None
        for i in range(len(self.viteze) - 1, -1, -1):
            if abs(self.viteze[i] - target) > band:
                last_outside = i
                break
        if last_outside is None:
            settling_time = self.timp[0]
        elif last_outside < len(self.viteze) - 1:
            settling_time = self.timp[last_outside + 1]

        for i, v in enumerate(self.viteze):
            if v >= 0.9 * target:
                rise_time = self.timp[i]
                break

        return {
            "rise_time": round(rise_time, 3) if rise_time is not None else None,
            "overshoot": round(max(overshoot, 0.0), 4),
            "overshoot_percent": round(max(overshoot, 0.0) / abs(target) * 100, 2),
            "settling_time": round(settling_time, 3) if settling_time is not None else None,
            "steady_state_error": round(target - self.viteze[-1], 4),
        }
