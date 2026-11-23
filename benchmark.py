"""Compare Verlet and RK4 on the simulator's default elliptical orbit."""

from math import ceil, hypot, pi, sqrt
from statistics import median
from time import perf_counter

from physics import earth_radius, measure_period, mu, rk4_step, simulate_orbit, specific_energy, verlet_step

INTEGRATORS = (("Velocity Verlet", verlet_step), ("RK4", rk4_step))


def final_position_error(trajectory, initial_state, step):
    x_positions, y_positions, *_ = trajectory
    return hypot(x_positions[step] - initial_state[0], y_positions[step] - initial_state[1])


def time_runs(initial_state, dt, steps, integrator, repetitions=7):
    runtimes = []
    for _ in range(repetitions):
        start = perf_counter()
        trajectory = simulate_orbit(*initial_state, dt, steps, integrator=integrator)
        runtimes.append(perf_counter() - start)
    return trajectory, median(runtimes) * 1000


def find_step_count(initial_state, period, integrator, tolerance):
    def error_at(steps):
        trajectory = simulate_orbit(*initial_state, period / steps, steps, integrator=integrator)
        return final_position_error(trajectory, initial_state, steps)

    # Start where the fixed-step experiment already shows convergence.
    lower = upper = 100
    while error_at(upper) >= tolerance:
        lower = upper
        upper *= 2

    # Bisect the bracket between the last failure and the first success.
    while upper - lower > 1:
        middle = (lower + upper) // 2
        if error_at(middle) < tolerance:
            upper = middle
        else:
            lower = middle

    return upper


def compare_at_tolerance(initial_state, period, tolerance):
    print()
    print(f"Accuracy target: less than {tolerance:g} m after one predicted orbit")
    print("Step counts are found by bisection from 100 steps upward.")
    print(f"{'Integrator':<17} {'Steps':>7} {'Step (s)':>10} "
          f"{'Position error (m)':>19} {'Runtime (ms)':>13}")

    for name, integrator in INTEGRATORS:
        steps = find_step_count(initial_state, period, integrator, tolerance)
        dt = period / steps
        trajectory, runtime = time_runs(initial_state, dt, steps, integrator)
        error = final_position_error(trajectory, initial_state, steps)
        print(f"{name:<17} {steps:7d} {dt:10.6f} {error:19.6f} {runtime:13.3f}")


def run_at_runtime_target(initial_state, period, integrator, orbits, target_ms):
    steps_per_orbit = 100
    for _ in range(3):
        trajectory, runtime = time_runs(
            initial_state, period / steps_per_orbit, orbits * steps_per_orbit,
            integrator, repetitions=3,
        )
        if abs(runtime - target_ms) <= 0.10 * target_ms:
            return steps_per_orbit, trajectory, runtime
        adjusted_steps = max(1, round(steps_per_orbit * target_ms / runtime))
        if adjusted_steps == steps_per_orbit:
            return steps_per_orbit, trajectory, runtime
        steps_per_orbit = adjusted_steps

    trajectory, runtime = time_runs(
        initial_state, period / steps_per_orbit, orbits * steps_per_orbit,
        integrator, repetitions=3,
    )
    return steps_per_orbit, trajectory, runtime


def compare_over_many_orbits(initial_state, period):
    orbits = 100
    target_ms = 100
    print()
    print(f"Long run: {orbits} predicted orbits, targeting {target_ms} ms per integrator")
    print("Actual runtimes are medians of three runs. Energy changes are in parts per million (ppm).")
    print()

    for name, integrator in INTEGRATORS:
        steps_per_orbit, trajectory, runtime = run_at_runtime_target(
            initial_state, period, integrator, orbits, target_ms,
        )
        _, _, _, _, energies = trajectory
        starting_energy = energies[0]
        relative_energy_ppm = [
            (energy - starting_energy) / abs(starting_energy) * 1_000_000
            for energy in energies
        ]

        print(f"{name} · step {period / steps_per_orbit:.3f} s · runtime {runtime:.2f} ms")
        print(f"{'Orbit':>5} {'Position error (m)':>19} "
              f"{'Energy change (ppm)':>20} {'Peak abs. change (ppm)':>23}")
        for orbit in (1, 10, orbits):
            index = orbit * steps_per_orbit
            position_error = final_position_error(trajectory, initial_state, index)
            peak_change = max(abs(change) for change in relative_energy_ppm[:index + 1])
            print(f"{orbit:5d} {position_error:19.3f} "
                  f"{relative_energy_ppm[index]:+20.6f} {peak_change:23.6f}")
        print()


def main():
    starting_radius = earth_radius + 400_000
    initial_state = (starting_radius, 0, 0, 1.1 * sqrt(mu / starting_radius))
    semimajor_axis = -mu / (2 * specific_energy(*initial_state))
    exact_period = 2 * pi * sqrt(semimajor_axis**3 / mu)

    print(f"Default elliptical orbit · predicted period {exact_period / 60:.2f} min")
    print("Position error is the distance from the starting point at the predicted period.")
    print("Period measurements use linear interpolation at the x-axis crossing.")
    print("Runtime is the median of seven runs over 1.05 predicted orbits.")
    print()
    print(f"{'Integrator':<17} {'Step (s)':>9} {'Position error (m)':>19} "
          f"{'Period error (s)':>17} {'Runtime (ms)':>13}")

    for steps_per_period in (100, 200, 400, 800):
        dt = exact_period / steps_per_period
        total_steps = ceil(1.05 * steps_per_period)
        for name, integrator in INTEGRATORS:
            trajectory, runtime = time_runs(initial_state, dt, total_steps, integrator)
            x_positions, y_positions, *_ = trajectory
            position_error = final_position_error(trajectory, initial_state, steps_per_period)
            measured_period = measure_period(x_positions, y_positions, dt)
            period_error = "—" if measured_period is None else f"{abs(measured_period - exact_period):.6f}"
            print(f"{name:<17} {dt:9.3f} {position_error:19.6f} "
                  f"{period_error:>17} {runtime:13.3f}")

    compare_at_tolerance(initial_state, exact_period, tolerance=10)
    compare_over_many_orbits(initial_state, exact_period)


if __name__ == "__main__":
    main()
