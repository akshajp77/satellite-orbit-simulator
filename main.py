import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.animation import FuncAnimation
import math
import numpy as np
from matplotlib.ticker import MaxNLocator
from matplotlib.widgets import Slider
from matplotlib.widgets import Button, Slider


earth_radius = 6_371_000
altitude = 400_000

x = earth_radius + altitude
y = 0


mu = 3.986004418e14 #Earth's graviational parameter, m^3/s^2


#Acceleration function, m/s^2

def acceleration(x , y):
    r = (x**2 + y**2)**0.5
    ax = -mu * x * (1/r**3)
    ay = -mu * y * (1/r**3)
    return ax, ay

def specific_energy(x, y, vx, vy):
    radius = (x**2 + y**2)**0.5
    return 0.5 * (vx**2 + vy**2) - mu / radius

def verlet_step(x,y,vx,vy,dt):
     # Acceleration at the current position
        accel_x, accel_y = acceleration(x,y)
    
        # Update position using current velocity and acceleration
        x = x + vx * dt + 0.5 * accel_x * dt**2
        y = y + vy * dt + 0.5 * accel_y * dt**2
    
        # Acceleration at the new position
        new_accel_x, new_accel_y = acceleration(x,y)
    
    
        # Update velocity using the average acceleration
        vx = vx + 0.5 * (accel_x + new_accel_x) * dt
        vy = vy + 0.5 * (accel_y + new_accel_y) * dt

        return x,y,vx,vy


def simulate_orbit(x, y, vx, vy, dt, steps):
    # Record the starting state at time zero.
    x_positions = [x]
    y_positions = [y]

    starting_radius = (x**2 + y**2)**0.5
    altitudes = [starting_radius - earth_radius]
    speeds = [(vx**2 + vy**2)**0.5]
    energies = [specific_energy(x, y, vx, vy)]

    for _ in range(steps):
        x, y, vx, vy = verlet_step(x, y, vx, vy, dt)

        x_positions.append(x)
        y_positions.append(y)

        current_radius = (x**2 + y**2)**0.5
        altitudes.append(current_radius - earth_radius)
        speeds.append((vx**2 + vy**2)**0.5)
        energies.append(specific_energy(x, y, vx, vy))

    return x_positions, y_positions, altitudes, speeds, energies


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
    
def measure_period(x_positions, y_positions, dt):
    for i in range(1, len(y_positions)):
        y_before = y_positions[i-1]
        y_after = y_positions[i]

        if y_before < 0 <= y_after and x_positions[i] > 0:
            fraction = -y_before / (y_after - y_before)
            return (i-1+fraction) * dt
    return None

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
fig_3d = plt.figure(figsize=(13, 7), layout="constrained")
grid = fig_3d.add_gridspec(4, 2, height_ratios=[20, 1, 1, 1.5])
ax_3d = fig_3d.add_subplot(grid[0, 0], projection="3d")

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
ax_3d.plot(orbit_x, orbit_y, orbit_z, color="#cc5500", linewidth=2.5, label="Orbit")
ax_3d.plot(
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

ax_3d.set_title(f"Satellite orbit at {inclination_degrees}° inclination")
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
    angle = math.radians(degrees)
    new_y = [sample * math.cos(angle) / kilometer for sample in y_positions]
    new_z = [sample * math.sin(angle) / kilometer for sample in y_positions]

    orbit_line_3d.set_data_3d(orbit_x, new_y, new_z)
    ax_3d.set_title(f"Satellite orbit at {degrees:.0f}° inclination")
    longitude_deg, latitude_deg = ground_track(orbit_x, new_y, new_z, dt)
    track_points.set_offsets(
        np.column_stack((longitude_deg[::10], latitude_deg[::10]))
    )
    update_time(time_slider.val)



inclination_slider.on_changed(update_inclination)

def ground_track(orbit_x, orbit_y, orbit_z, dt):
    longitude_in_space = np.arctan2(orbit_y, orbit_x)
    latitude = np.arctan2(orbit_z, np.hypot(orbit_x, orbit_y))

    elapsed_seconds = np.arange(len(orbit_x)) * dt
    earth_rotation = 2 * math.pi * elapsed_seconds / 86_164

    longitude_deg = np.degrees(longitude_in_space - earth_rotation)
    longitude_deg = (longitude_deg + 180) % 360 - 180
    return longitude_deg, np.degrees(latitude)

longitude_deg, latitude_deg = ground_track(orbit_x, orbit_y, orbit_z, dt)


ax_track = fig_3d.add_subplot(grid[0, 1])
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
    set_playing(False)
    time_slider.set_val(apogee_index * dt)

apogee_button.on_clicked(jump_to_apogee)

plt.show()
