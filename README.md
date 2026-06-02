# OpenFactory Liquid Personalization

OpenFactory app for a personalized liquid production line.

This repository is the first software prototype for a virtual OpenFactory-based production line. The app allows a user to create a personalized liquid product order by choosing a target color, liquid volume, and label text. The app then generates a first virtual recipe and production sequence.

## Thesis Context

The goal is to start with a virtual factory workflow before connecting the physical lab setup.

The future lab setup is expected to be based on a 4-nozzle automatic liquid filling machine. The production line will eventually support personalized liquid products, where the user defines product parameters and OpenFactory converts them into executable work orders.

## Current Scope

This first version does not control real hardware yet.

It currently provides:

- a Flask-based OpenFactory App
- OpenFactory app deployment through `ofa apps up`
- Docker-based app packaging
- Traefik routing through OpenFactory
- a simple UNS schema for app registration
- a user-facing web form for product orders
- RGB color selection
- volume selection
- label text input
- recipe calculation
- virtual production sequence generation
- unit tests for recipe logic
- route tests for the web app

## Planned Factory Concept

User order:

```text
RGB color + volume + label
```

OpenFactory logic:

```text
Product order -> recipe calculation -> virtual work order
```

Virtual production flow:

```text
Bottle source -> conveyor -> bottle detection -> filling station -> optional labeling -> finished bottle
```

## Planned Hardware Context

The future physical setup may include:

- 4-nozzle automatic liquid filling machine
- conveyor belt
- base liquid reservoir
- color reservoirs
- peristaltic dosing pumps
- tubing, fittings, and check valves
- mixing container or mixing chamber
- mixer or stirrer
- bottle presence sensors
- industrial control hardware / I/O
- 24V power supply
- relay modules / switching hardware
- label printer
- label applicator
- bottle guides and mechanical fixturing
- emergency stop and basic safety components
- bottles, caps, labels, and liquid consumables
- industrial control unit running Linux

## Development Setup

This project is intended to be developed inside the OpenFactory SDK devcontainer.

After opening the repository in the devcontainer, install the project with development dependencies:

```bash
pip install -e .[dev]
```

## Run Tests

```bash
pytest
```

Expected result:

```text
8 passed
```

## Run the App as an OpenFactory App

Start the OpenFactory stack from inside the devcontainer:

```bash
spinup
```

Build the app image:

```bash
docker build -t liquid-personalization-app .
```

Export the UNS schema path:

```bash
export OPENFACTORY_UNS_SCHEMA=/workspaces/openfactory-liquid-personalization/uns_schema.yml
```

Deploy the app with OpenFactory:

```bash
ofa apps up app_liquid_personalization.yml
```

Check deployed apps:

```bash
ofa apps ls
```

The app should appear as available:

```text
LIQUID-PERSONALIZATION-APP   AVAILABLE
```

Open the app through Traefik:

```text
http://localhost/liquid-personalization-app/
```

Health check:

```text
http://localhost/liquid-personalization-app/health
```

To stop the app:

```bash
ofa apps down app_liquid_personalization.yml
```

## Optional Local Development Run

For quick local development without OpenFactory deployment, the app can still be started directly:

```bash
OPENFACTORY_TEST_MODE=true liquid-personalization-app
```

Then open:

```text
http://127.0.0.1:4000
```

Health check:

```text
http://127.0.0.1:4000/health
```

This mode is mainly for development and testing. The intended OpenFactory deployment uses `ofa apps up`.

## First Software Milestone

The first milestone is to build a minimal Flask-based OpenFactory App that allows a user to:

1. choose a target color
2. choose a liquid volume
3. enter label text
4. generate a virtual recipe
5. generate a virtual production sequence

This milestone now includes deployment as a proper OpenFactory-managed app with Docker packaging and Traefik routing.

## Later Milestones

Future versions will replace virtual components one by one with real lab hardware.

Possible progression:

1. fully virtual product order and recipe generation
2. virtual production sequence
3. simulated factory devices
4. connection to real sensors and I/O
5. connection to the filling machine
6. optional labeling integration
7. full OpenFactory-controlled personalized production line