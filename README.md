# Satellite Orbit Simulator

A Python project that combines programming and orbital physics to
simulate a satellite moving around Earth.

## Project Goal

Build a two-dimensional orbit simulator and investigate how different
numerical methods and time steps affect its accuracy and execution time.

## How It Works

The simulator will begin with a satellite's starting position and velocity.
It will calculate gravitational acceleration and update the satellite's
motion over small time steps.

Plotting the resulting positions will show the satellite's orbit.

The initial model will treat Earth as a stationary, spherical source of
gravity and the satellite as a point mass. It will ignore atmospheric drag
and gravity from other celestial bodies.

## Research Question

How do numerical methods and time-step sizes affect the accuracy and
speed of a satellite orbit simulation?

## Planned Features

- Simulate and visualize circular and elliptical orbits.
- Adjust the satellite's starting position and velocity.
- Compare methods such as Euler and fourth-order Runge–Kutta.
- Measure position error, energy drift, and execution time.
- Validate results against known orbital equations.
- Compare selected scenarios with NASA's General Mission Analysis Tool.

## Tools

- Python
- NumPy for numerical calculations
- Matplotlib for plotting and visualization

## Learning Goals

Develop skills in Python, numerical methods, orbital mechanics,
scientific visualization, and evaluating simulation results.

## Project Status

Early development. Features listed above describe the planned scope.