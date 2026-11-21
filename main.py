import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.animation import FuncAnimation
import math


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

for test_dt in (1, 5, 10, 20):
    test_steps = duration // test_dt
    test_x, test_y, *_ = simulate_orbit(x,y,vx,vy, test_dt, test_steps)
    measured = measure_period(test_x, test_y, test_dt)

    if measured is None:
        print(f"dt = {test_dt:2d} s | No completed orbit")
    else:
        error = abs(measured - predicted_period)
        print(f"dt = {test_dt:2d} s | Period error = {error:.6f} s")


minimum_altitude = min(altitudes)
maximum_altitude = max(altitudes)

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


def update(frame):
    orbit_line.set_data(
        x_positions[:frame + 1],
        y_positions[:frame + 1]
    )

    satellite.set_data(
        [x_positions[frame]],
        [y_positions[frame]]
    )

    return orbit_line, satellite

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


plt.show()
