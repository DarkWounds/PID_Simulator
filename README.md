# PID Simulator

An interactive PID controller simulator: a **FastAPI** backend runs the simulation and a web page lets you tune **Kp**, **Ki** and **Kd** with sliders and see the response instantly. A desktop version with matplotlib is included too.

<!-- Add a screenshot or GIF of the web page here, e.g. ![demo](docs/pid.gif) -->

## Features

- Live chart of the speed against the setpoint, plus the controller output
- Step-response metrics: rise time (90%), overshoot, settling time (±2%) and steady-state error
- Presets to compare **P**, **PI** and **PID**
- Two motor models:
  - **Simple**: the PID output changes the speed directly (`speed += (P + I + D) * dt`)
  - **DC motor**: the same model as `Motor.cs` in my Unity FTC motor simulator. The PID output is a power limited to −1…1 and the speed follows `power × maxRPM` with a first-order time constant. Here you can see why a P controller alone leaves a steady-state error and how the I term removes it.
- REST API with automatic documentation at `/docs`

## How it works

```
error = setpoint - speed
P = Kp * error
I = Ki * (sum of error * dt)
D = Kd * (error - previous error) / dt
```

| File | Role |
|---|---|
| `pid_core.py` | `PIDSimulator` class and metrics, no UI |
| `main.py` | FastAPI app: `POST /api/simulate` and the web page |
| `static/index.html` | Sliders and charts (plain HTML, CSS and JavaScript, no libraries) |
| `PIDClass.py` | Desktop version with matplotlib sliders |

### API example

`POST /api/simulate`

```json
{ "kp": 2, "ki": 20, "kd": 0, "setpoint": 200, "model": "dc_motor", "duration": 1, "dt": 0.002 }
```

returns the time, speed and controller-output arrays plus the metrics. Parameters are validated (for example negative gains are rejected with `422`).

## Run it

On Windows: double-click **`Start_PID_Simulator.bat`**. It installs the packages on the first run, starts the server and opens the page in your browser. `Start_Desktop.bat` opens the matplotlib version.

Manually:

```bash
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Then open http://127.0.0.1:8000 (API docs at http://127.0.0.1:8000/docs).

Desktop version: `python PIDClass.py`

## Tech

Python · FastAPI · Pydantic · Uvicorn · HTML/CSS/JavaScript (canvas) · Matplotlib
