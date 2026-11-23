# Satellite Orbit Simulator

An interactive Python simulator for exploring how a satellite moves around Earth.
Choose a circular or elliptical orbit, or set a custom starting altitude and
speed. Change the inclination and watch the 3D orbit and ground track update
together.

## Run it

```bash
python -m pip install numpy matplotlib
python main.py
```

## Try this

1. Set the inclination to 60°. The ground track reaches about 60° north and south.
2. Switch from **Circular** to **Elliptical**. Both start at 400 km, but the
   elliptical preset starts 10% faster and climbs to about 4,000 km.
3. Press **Play** to follow the satellite in both views, then click **Jump to apogee**
   to pause at its farthest point.

## Accuracy check

The default orbit starts at 400 km altitude with 1.1 times the local circular
speed. Its predicted period is 131.61 minutes. With a 1-second time step,
the measured period differs from the prediction by about 0.003 seconds.
Doubling the time step from 5 to 10 to 20 seconds roughly quadruples the
period error each time, consistent with the velocity Verlet method's
second-order accuracy.

## Integrator benchmark

```bash
python benchmark.py
```

Velocity Verlet and classical fourth-order Runge–Kutta (RK4) start from the
same elliptical orbit. At an exact multiple of the predicted period, the
ideal orbit returns to its launch point. The benchmark measures position
error as the distance between the simulated and expected positions at that
instant.

In one run, both methods met the same target of less than 10 m of position
error after one orbit. Runtime is the median of seven runs.

| Integrator | Steps per orbit | Time step | Position error | Median runtime |
|---|---:|---:|---:|---:|
| Velocity Verlet | 12,522 | 0.631 s | 9.998 m | 9.87 ms |
| RK4 | 160 | 49.355 s | 9.915 m | 0.41 ms |

For the 100-orbit comparison, the script calibrates the step size separately
for each method to target 100 ms of computation. It reports actual median
runtime, position error, and peak energy error. The same example run produced
these results.

| Integrator | Median runtime | Position error at orbit 100 | Peak relative energy error |
|---|---:|---:|---:|
| Velocity Verlet | 103.10 ms | 100.18 km | 7.095 ppm |
| RK4 | 98.59 ms | 348.52 m | 0.067 ppm |

RK4 was about 24 times faster at the one-orbit accuracy target and gave a
smaller position error in the 100-orbit comparison. Verlet's energy
fluctuated and ended close to its initial value, while RK4's energy trended
downward at the measured checkpoints. These results apply to this orbit and
the tested settings. Runtime and the calibrated step sizes vary by machine.

## Model assumptions

The model uses a spherical Earth with central gravity and constant rotation.
It omits atmospheric drag and Earth's oblateness.
