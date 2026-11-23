"""Physics for a planar orbit around a spherical Earth, in SI units."""

earth_radius = 6_371_000  # m
mu = 3.986004418e14  # Earth's gravitational parameter, m^3/s^2


def acceleration(x , y):
    r = (x**2 + y**2)**0.5
    ax = -mu * x * (1/r**3)
    ay = -mu * y * (1/r**3)
    return ax, ay

def specific_energy(x, y, vx, vy):
    radius = (x**2 + y**2)**0.5
    return 0.5 * (vx**2 + vy**2) - mu / radius

def verlet_step(x, y, vx, vy, dt):
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


def state_derivative(state):
    x, y, vx, vy = state
    ax, ay = acceleration(x, y)
    return vx, vy, ax, ay


def advance_state(state, derivative, dt):
    return tuple(value + rate * dt for value, rate in zip(state, derivative))


def rk4_step(x, y, vx, vy, dt):
    """Advance the position and velocity with classical fourth-order Runge–Kutta."""
    state = (x, y, vx, vy)
    # Sample the derivative at the start, two midpoints, and the end.
    first = state_derivative(state)
    second = state_derivative(advance_state(state, first, dt / 2))
    third = state_derivative(advance_state(state, second, dt / 2))
    fourth = state_derivative(advance_state(state, third, dt))

    return tuple(
        value + dt * (start + 2 * midpoint_a + 2 * midpoint_b + end) / 6
        for value, start, midpoint_a, midpoint_b, end
        in zip(state, first, second, third, fourth)
    )


def simulate_orbit(x, y, vx, vy, dt, steps, *, integrator=verlet_step):
    # Record the starting state at time zero.
    x_positions = [x]
    y_positions = [y]

    starting_radius = (x**2 + y**2)**0.5
    altitudes = [starting_radius - earth_radius]
    speeds = [(vx**2 + vy**2)**0.5]
    energies = [specific_energy(x, y, vx, vy)]

    for _ in range(steps):
        x, y, vx, vy = integrator(x, y, vx, vy, dt)

        x_positions.append(x)
        y_positions.append(y)

        current_radius = (x**2 + y**2)**0.5
        altitudes.append(current_radius - earth_radius)
        speeds.append((vx**2 + vy**2)**0.5)
        energies.append(specific_energy(x, y, vx, vy))

    return x_positions, y_positions, altitudes, speeds, energies


def measure_period(x_positions, y_positions, dt):
    """Find the first upward crossing of the positive x-axis after launch."""
    for index in range(1, len(y_positions)):
        y_before = y_positions[index - 1]
        y_after = y_positions[index]
        if y_before < 0 <= y_after and x_positions[index] > 0:
            fraction = -y_before / (y_after - y_before)
            return (index - 1 + fraction) * dt
    return None
