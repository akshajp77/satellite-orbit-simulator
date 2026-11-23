import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.animation import FuncAnimation
import math
from typing import NamedTuple
import numpy as np
from matplotlib.ticker import MaxNLocator
from matplotlib.widgets import Button, RadioButtons, Slider, TextBox

from physics import earth_radius, measure_period, mu, simulate_orbit


altitude = 400_000

x = earth_radius + altitude
y = 0


# Set the initial velocity for the elliptical orbit.
r = (x**2 + y**2)**0.5
speed_multiplier = 1.1
vx = 0
vy = (mu / r)**0.5 * speed_multiplier

dt = 1
steps = 8000

x_positions, y_positions, altitudes, speeds, energies = simulate_orbit(
    x, y, vx, vy, dt, steps
)

initial_energy = energies[0]
semimajor_axis = -mu / (2 * initial_energy)
predicted_period = 2 * math.pi * (semimajor_axis**3 / mu)**0.5

print(f"Predicted orbital period: {predicted_period / 60:.2f} minutes")
    
duration = 8000

time_steps = []
period_errors = []

for test_dt in (1, 5, 10, 20):
    test_steps = duration // test_dt
    test_x, test_y, *_ = simulate_orbit(x,y,vx,vy, test_dt, test_steps)
    measured = measure_period(test_x, test_y, test_dt)

    if measured is None:
        print(f"dt = {test_dt:2d} s | No completed orbit")
    else:
        error = abs(measured - predicted_period)
        time_steps.append(test_dt)
        period_errors.append(error)
        print(f"dt = {test_dt:2d} s | Period error = {error:.6f} s")


minimum_altitude = min(altitudes)
maximum_altitude = max(altitudes)

perigee_radius = math.hypot(x,y)
predicted_apogee = 2 * semimajor_axis - perigee_radius - earth_radius
apogee_error = abs(maximum_altitude - predicted_apogee)

print(f"Predicted apogee alititude: {predicted_apogee / 1000:.3f} km")
print(f"Apogee altitude error: {apogee_error:.2f} m")

max_relative_error = max(
    abs(energy - initial_energy) / abs(initial_energy)
    for energy in energies
)

print(f"Minimum altitude {minimum_altitude / 1000:.2f} km")
print(f"Maximum altitude {maximum_altitude / 1000:.2f} km")
print(f"Altitude range: {(maximum_altitude - minimum_altitude):.3f} m")

print(f"Maximum energy error: {max_relative_error * 100:.6f}%")




## Plotting Code

fig, ax = plt.subplots()

earth = Circle((0,0), earth_radius, color = "royalblue")
ax.add_patch(earth)

orbit_line, = ax.plot([], [], color = "orange", label = "Orbit")
satellite, = ax.plot([], [], "ro", label = "Satellite")

view_limit = earth_radius * 2

ax.set_xlim(-view_limit, view_limit)
ax.set_ylim(-view_limit, view_limit)
ax.set_aspect("equal")

ax.set_xlabel("x position (m)")
ax.set_ylabel("y position (m)")
ax.set_title("Satellite starting position")
ax.legend()

telemetry = ax.text(
    0.02, 0.98, "",
    transform = ax.transAxes,
    va="top",
    bbox={"facecolor": "white", "alpha": 0.9}
)


def update(frame):
    orbit_line.set_data(
        x_positions[:frame + 1],
        y_positions[:frame + 1]
    )

    satellite.set_data(
        [x_positions[frame]],
        [y_positions[frame]]
    )

    elapsed_minutes = frame * dt / 60
    altitude_km = altitudes[frame] / 1000
    speed_km_s = speeds[frame] / 1000

    telemetry.set_text(
        f"Time: {elapsed_minutes: .1f} min\n"
        f"Alititude: {altitude_km:,.0f} km\n"
        f"Speed: {speed_km_s: .2f} km/s"
    )

    return orbit_line, satellite, telemetry

animation = FuncAnimation(
    fig,
    update,
    frames = range(0, len(x_positions), 20),
    interval = 20,
    blit = True,
    repeat = False
)


times_minutes = [
    step * dt / 60
    for step in range(len(altitudes))
]

altitudes_km = [
    height / 1000
    for height in altitudes
]

speeds_km = [
    speed / 1000
    for speed in speeds
]

fig_altitude, ax_altitude = plt.subplots()

ax_altitude.plot(times_minutes, altitudes_km)
ax_altitude.set_xlabel("Time (minutes)")
ax_altitude.set_ylabel("Altitude (km)")
ax_altitude.set_title("Satellite altitude over time")
ax_altitude.grid(True)

apogee_index = altitudes.index(maximum_altitude)

ax_altitude.scatter(
    times_minutes[apogee_index],
    altitudes_km[apogee_index],
    color = "crimson",
    label = "Apogee",
)

ax_altitude.legend()

fig_speeds, ax_speeds = plt.subplots()

ax_speeds.plot(times_minutes, speeds_km)
ax_speeds.set_xlabel("Time (minutes)")
ax_speeds.set_ylabel("Speed (km/s)")
ax_speeds.set_title("Satellite speed over time")
ax_speeds.grid(True)

circular_speed = (mu / r)**0.5
circular_x, circular_y, *_ = simulate_orbit(
     x, y, 0, circular_speed, dt, steps
)

fig_comparison, ax_comparison = plt.subplots()
ax_comparison.add_patch(Circle((0,0), earth_radius, color = "royalblue"))

ax_comparison.plot(circular_x, circular_y, label = "Circular orbit")
ax_comparison.plot(x_positions, y_positions, label = "Elliptical orbit")

ax_comparison.set_aspect("equal")
ax_comparison.set_xlabel("x position (m)")
ax_comparison.set_ylabel("y position (m)")
ax_comparison.set_title("How starting speed changes the orbit")
ax_comparison.legend()


fig_error, ax_error = plt.subplots()
ax_error.loglog(time_steps, period_errors, "o-", label="Measured error")

# Start the reference line at the first measured point.
reference_errors = [
    period_errors[0] * (step / time_steps[0])**2
    for step in time_steps
]
ax_error.loglog(time_steps, reference_errors, "--", label="Quadratic reference")

ax_error.set_xlabel("Time step (s)")
ax_error.set_ylabel("Absolute period error (s)")
ax_error.set_title("Orbital period error vs. time step")
ax_error.grid(True, which="both", alpha=0.3)
ax_error.legend()


kilometer = 1000
inclination_degrees = 45
inclination = math.radians(inclination_degrees)

orbit_x = [x_sample / kilometer for x_sample in x_positions]
orbit_y = [y_sample * math.cos(inclination) / kilometer for y_sample in y_positions]
orbit_z = [y_sample * math.sin(inclination) / kilometer for y_sample in y_positions]

radius_km = earth_radius / kilometer
fig_3d = plt.figure(figsize=(13, 8), layout="constrained")
grid = fig_3d.add_gridspec(6, 4, height_ratios=[20, 1, 1, 3, 2, 1])
ax_3d = fig_3d.add_subplot(grid[0, :2], projection="3d")

orbit_line_3d, = ax_3d.plot(
    orbit_x, orbit_y, orbit_z, color="#cc5500", linewidth=2.5, label="Orbit"
)

# Draw Earth as a wireframe so the full orbit stays visible.
longitude, latitude = np.meshgrid(
    np.linspace(0, 2 * math.pi, 25),
    np.linspace(-math.pi / 2, math.pi / 2, 13),
)
ax_3d.plot_wireframe(
    radius_km * np.cos(latitude) * np.cos(longitude),
    radius_km * np.cos(latitude) * np.sin(longitude),
    radius_km * np.sin(latitude),
    color="#4477aa", linewidth=0.6, alpha=0.35,
)

angles = np.linspace(0, 2 * math.pi, 181)
ax_3d.plot(
    radius_km * np.cos(angles), radius_km * np.sin(angles),
    np.zeros_like(angles), "--", color="#4477aa", label="Earth's equator",
)
starting_marker, = ax_3d.plot(
    orbit_x[:1], orbit_y[:1], orbit_z[:1],
    "o", color="#176e61", label="Starting position",
)

# Center all three axes on Earth and use the same scale in every direction.
farthest_radius_km = (earth_radius + max(altitudes)) / kilometer
axis_limit = 1.08 * max(radius_km, farthest_radius_km)
ax_3d.set_xlim(-axis_limit, axis_limit)
ax_3d.set_ylim(-axis_limit, axis_limit)
ax_3d.set_zlim(-axis_limit, axis_limit)
ax_3d.set_box_aspect((1, 1, 1))
ax_3d.set_proj_type("ortho")
ax_3d.view_init(elev=25, azim=-55)
for axis in (ax_3d.xaxis, ax_3d.yaxis, ax_3d.zaxis):
    axis.set_major_locator(MaxNLocator(5, symmetric=True))

ax_3d.set_title(f"Elliptical orbit at {inclination_degrees}° inclination")
ax_3d.set_xlabel("x (km)")
ax_3d.set_ylabel("y (km)")
ax_3d.set_zlabel("z (km)")
ax_3d.legend(loc="upper left")

slider_ax = fig_3d.add_subplot(grid[1, :])
inclination_slider = Slider(
    slider_ax, "Inclination", 0, 90,
    valinit=inclination_degrees, valstep=1, valfmt="%d°"
)

def update_inclination(degrees):
    preset = orbit_preset.value_selected
    path = preset_paths[preset]
    angle = math.radians(degrees)
    new_x = np.asarray(path.x_positions) / kilometer
    y_km = np.asarray(path.y_positions) / kilometer
    new_y = y_km * math.cos(angle)
    new_z = y_km * math.sin(angle)

    orbit_line_3d.set_data_3d(new_x, new_y, new_z)
    ax_3d.set_title(f"{preset} orbit at {degrees:.0f}° inclination")
    longitude_deg, latitude_deg = ground_track(new_x, new_y, new_z, dt)
    track_points.set_offsets(
        np.column_stack((longitude_deg[::10], latitude_deg[::10]))
    )
    update_time(time_slider.val)



def ground_track(orbit_x, orbit_y, orbit_z, dt):
    longitude_in_space = np.arctan2(orbit_y, orbit_x)
    latitude = np.arctan2(orbit_z, np.hypot(orbit_x, orbit_y))

    elapsed_seconds = np.arange(len(orbit_x)) * dt
    earth_rotation = 2 * math.pi * elapsed_seconds / 86_164

    longitude_deg = np.degrees(longitude_in_space - earth_rotation)
    longitude_deg = (longitude_deg + 180) % 360 - 180
    return longitude_deg, np.degrees(latitude)

longitude_deg, latitude_deg = ground_track(orbit_x, orbit_y, orbit_z, dt)


ax_track = fig_3d.add_subplot(grid[0, 2:])
track_points = ax_track.scatter(longitude_deg[::10], latitude_deg[::10], s=6)
ax_track.set(
    title="Satellite ground track",
    xlabel="Longitude (°)",
    ylabel="Latitude (°)",
    xlim=(-180, 180),
    ylim=(-90, 90),
)
ax_track.grid(alpha=0.3)

satellite_marker, = ax_3d.plot([], [], [], "o", color="crimson")
ground_marker, = ax_track.plot([], [], "o", color="crimson")

time_slider = Slider(
    fig_3d.add_subplot(grid[2, :]),
    "Time (s)",
    0, (len(orbit_x) - 1) * dt,
    valinit=0, valstep=dt, valfmt="%.0f"
)

def update_time(elapsed_seconds):
    index = round(elapsed_seconds / dt)
    path_x, path_y, path_z = orbit_line_3d.get_data_3d()
    longitude, latitude = ground_track(path_x, path_y, path_z, dt)

    satellite_marker.set_data_3d(
        [path_x[index]], [path_y[index]], [path_z[index]]
    )

    ground_marker.set_data([longitude[index]], [latitude[index]])
    fig_3d.canvas.draw_idle()

time_slider.on_changed(update_time)
update_time(0)

play_button = Button(fig_3d.add_subplot(grid[3, 0]), "Play")
playback_timer = fig_3d.canvas.new_timer(interval=40)
playing = False


def set_playing(active):
    global playing
    playing = active

    if playing:
        play_button.label.set_text("Pause")
        playback_timer.start()
    else:
        play_button.label.set_text("Play")
        playback_timer.stop()

    fig_3d.canvas.draw_idle()


def advance_playback():
    next_time = min(time_slider.val + 20 * dt, time_slider.valmax)
    time_slider.set_val(next_time)

    if next_time >= time_slider.valmax:
        set_playing(False)


def toggle_playback(_event):
    if playing:
        set_playing(False)
    else:
        if time_slider.val >= time_slider.valmax:
            time_slider.set_val(0)
        set_playing(True)


playback_timer.add_callback(advance_playback)
play_button.on_clicked(toggle_playback)

apogee_button = Button(
    fig_3d.add_subplot(grid[3,1]),
    "Jump to apogee",
)

def jump_to_apogee(_event):
    index = preset_paths[orbit_preset.value_selected].apogee_index
    if index is None:
        return
    set_playing(False)
    time_slider.set_val(index * dt)

apogee_button.on_clicked(jump_to_apogee)


class ExplorerOrbit(NamedTuple):
    x_positions: list
    y_positions: list
    apogee_index: int | None


elliptical_path = ExplorerOrbit(x_positions, y_positions, apogee_index)
preset_paths = {
    "Circular": ExplorerOrbit(circular_x, circular_y, None),
    "Elliptical": elliptical_path,
    "Custom": elliptical_path,
}
preset_ax = fig_3d.add_subplot(grid[3, 2:])
preset_ax.set_title("Orbit preset", loc="left")
orbit_preset = RadioButtons(preset_ax, list(preset_paths), active=1)


def switch_orbit(preset):
    path = preset_paths[preset]
    set_playing(False)
    time_slider.reset()
    time_slider.valmax = (len(path.x_positions) - 1) * dt
    time_slider.ax.set_xlim(0, time_slider.valmax)

    starting_marker.set_data_3d([path.x_positions[0] / kilometer], [0], [0])
    path_radius_km = np.hypot(path.x_positions, path.y_positions).max() / kilometer
    limit = max(axis_limit, 1.08 * path_radius_km)
    ax_3d.set(xlim=(-limit, limit), ylim=(-limit, limit), zlim=(-limit, limit))

    has_apogee = path.apogee_index is not None
    apogee_button.set_active(has_apogee)
    apogee_button.label.set_text(
        "Jump to apogee" if has_apogee else "Apogee (ellipse only)"
    )
    update_inclination(inclination_slider.val)


altitude_input_ax = fig_3d.add_subplot(grid[4, 0])
altitude_input_ax.set_title("Starting altitude (km)", loc="left", fontsize=10)
altitude_input = TextBox(altitude_input_ax, "", initial="400")
speed_input_ax = fig_3d.add_subplot(grid[4, 1])
speed_input_ax.set_title("Speed (× local circular)", loc="left", fontsize=10)
speed_input = TextBox(speed_input_ax, "", initial="1.1")
apply_button = Button(fig_3d.add_subplot(grid[4, 2:]), "Apply custom orbit")
status_ax = fig_3d.add_subplot(grid[5, :])
status_ax.axis("off")
custom_status = status_ax.text(0, 0.5, "", va="center")


def apply_custom_orbit(_event):
    try:
        altitude_km = float(altitude_input.text)
        multiplier = float(speed_input.text)
    except ValueError:
        custom_status.set_text("Enter numbers for altitude and speed.")
        fig_3d.canvas.draw_idle()
        return

    if not (200 <= altitude_km <= 2000 and 0.90 <= multiplier <= 1.15):
        custom_status.set_text("Use 200–2,000 km and a speed multiplier of 0.90–1.15.")
        fig_3d.canvas.draw_idle()
        return

    start_radius = earth_radius + altitude_km * kilometer
    custom_semimajor_axis = start_radius / (2 - multiplier**2)
    opposite_radius = 2 * custom_semimajor_axis - start_radius
    if min(start_radius, opposite_radius) <= earth_radius:
        custom_status.set_text("This orbit crosses Earth. Increase the altitude or starting speed.")
        fig_3d.canvas.draw_idle()
        return

    custom_period = 2 * math.pi * math.sqrt(custom_semimajor_axis**3 / mu)
    custom_steps = math.ceil(custom_period / dt)
    custom_speed = math.sqrt(mu / start_radius) * multiplier
    custom_x, custom_y, custom_altitudes, *_ = simulate_orbit(
        start_radius, 0, 0, custom_speed, dt, custom_steps
    )
    custom_apogee_index = None
    if multiplier < 1:
        custom_apogee_index = 0
    elif multiplier > 1:
        custom_apogee_index = custom_altitudes.index(max(custom_altitudes))

    preset_paths["Custom"] = ExplorerOrbit(custom_x, custom_y, custom_apogee_index)
    custom_status.set_text(f"Custom orbit · Predicted period {custom_period / 60:.2f} min")
    orbit_preset.set_active(2)


inclination_slider.on_changed(update_inclination)
orbit_preset.on_clicked(switch_orbit)
apply_button.on_clicked(apply_custom_orbit)

plt.show()
