# Satellite Orbit Simulator

An interactive Python simulator for exploring how a satellite moves around Earth.
Change the orbital inclination and watch the 3D orbit and ground track update
together. Use the time slider, Play/Pause, or Jump to apogee to inspect the orbit.

## Run it

    python -m pip install numpy matplotlib
    python main.py

## Try this

Set the inclination to 60° and watch the ground track reach about 60° north
and south. Click **Jump to apogee** to see the satellite at its farthest point.

## Accuracy check

The default orbit starts at 400 km altitude with 1.1 times the local circular
speed. Its predicted period is 131.61 minutes. With a 1-second time step,
the measured period differs from the prediction by about 0.003 seconds.
Doubling the time step from 5 to 10 to 20 seconds roughly quadruples the
period error each time, consistent with the velocity Verlet method's
second-order accuracy.

The model uses a spherical Earth with central gravity and constant rotation.
It omits atmospheric drag and Earth's oblateness.