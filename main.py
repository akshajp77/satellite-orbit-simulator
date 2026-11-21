import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.animation import FuncAnimation

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

accel_x, accel_y = acceleration(x,y)
print("Acceleration:", accel_x, accel_y)

#Determine Initial Speed, m/s
r = (x**2 + y**2)**0.5

vx = 0
vy = (mu / r) ** 0.5

print("Starting velocity: ", vx , vy)

dt = 1
steps = 6000
x_positions = [x]
y_positions = [y]

for step in range(steps):
    accel_x, accel_y = acceleration(x,y)

    vx = vx + accel_x * dt
    vy = vy + accel_y * dt

    x = x + vx * dt
    y = y + vy * dt

    x_positions.append(x)
    y_positions.append(y)



## Plotting Code

fig, ax = plt.subplots()

earth = Circle((0,0), earth_radius, color = "royalblue")
ax.add_patch(earth)

orbit_line, = ax.plot([], [], color = "orange", label = "Orbit")
satellite, = ax.plot([], [], "ro", label = "Satellite")

view_limit = earth_radius * 1.3

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


plt.show()