import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider

from pid_core import PIDSimulator  # clasa e acum in pid_core.py, folosita si de API


# ── UI ────────────────────────────────────────────────────────────────────────

sim = PIDSimulator(kp=2, ki=0.1, kd=0.05, setpoint=1)

fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.2)

linie, = ax.plot([], [], label="Viteza motor")
ax.axhline(y=sim.setpoint, color='red', linestyle='--', label="Setpoint")
ax.set_xlim(0, 5)
ax.set_ylim(0, 1.5)
ax.set_title("PID Simulator")
ax.set_xlabel("Timp (s)")
ax.set_ylabel("Viteza")
ax.legend()
ax.grid(True)

ax_kp = plt.axes([0.2, 0.02, 0.6, 0.03])
ax_kd = plt.axes([0.2, 0.06, 0.6, 0.03])
ax_ki = plt.axes([0.2, 0.10, 0.6, 0.03])

slider_kp = Slider(ax_kp, 'Kp', 0.0, 3.0, valinit=sim.kp)
slider_kd = Slider(ax_kd, 'Kd', 0.0, 0.1, valinit=sim.kd)
slider_ki = Slider(ax_ki, 'Ki', 0.0, 0.5, valinit=sim.ki)


def update(val):
    sim.kp = slider_kp.val
    sim.ki = slider_ki.val
    sim.kd = slider_kd.val
    sim.reset()


slider_kp.on_changed(update)
slider_kd.on_changed(update)
slider_ki.on_changed(update)


def animate(frame):
    sim.step()
    linie.set_data(sim.timp, sim.viteze)
    return linie,


anim = animation.FuncAnimation(fig, animate, interval=50, blit=True)
plt.show()
