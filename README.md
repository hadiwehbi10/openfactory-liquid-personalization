```markdown
# OpenFactory Liquid Personalization

OpenFactory app for a personalized liquid production line.

## Goal

This project is the first software prototype for a virtual OpenFactory-based production line.

The user can create a personalized liquid product order by choosing:

- RGB color
- liquid volume
- label text

The app then generates a first virtual recipe and production sequence.

## Current Scope

This first version is intentionally simple.

It does not control real hardware yet. The goal is to start with a virtual factory workflow before connecting the physical 4-nozzle liquid filling machine, sensors, pumps, conveyor, and labeling hardware.

## Planned Factory Concept

User order:

RGB color + volume + label

OpenFactory logic:

Product order -> recipe calculation -> virtual work order

Virtual production flow:

Bottle source -> conveyor -> bottle detection -> filling station -> optional labeling -> finished bottle

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

## First Software Milestone

The first milestone is to build a minimal Flask-based OpenFactory App that allows a user to:

1. choose a target color
2. choose a liquid volume
3. enter label text
4. generate a virtual recipe
5. generate a virtual production sequence

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
```
