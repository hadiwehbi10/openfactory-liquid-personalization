# Arduino OPTA Firmware

## Overview

This directory contains the Arduino OPTA firmware used in the OpenFactory liquid-personalization research project at Concordia University.

The firmware provides an OPC UA server that exposes the OPTA's physical inputs and relay outputs to external applications.

The current implementation serves as a baseline for evaluating distributed manufacturing control using OpenFactory.

## Firmware

**File:** `OPCUA_Bidirectional_Test/OPCUA_Bidirectional_Test.ino`

The sketch is based on the Arduino OPC UA library's `opta_opcua_server` example, with modifications to configure a static Ethernet address for the laboratory network.

Baseline Git commit: `2b30e21`

Baseline SHA-256:

`963ac4671f901347d1a79abb844bebbea713928d559230c0cb9e8bb5b198758a`

This hash identifies the preserved source file. An exact match with the firmware currently flashed onto the OPTA has not been independently established.

## Hardware Configuration

| Component | OPTA Connection | Function |
|---|---|---|
| Infrared Sensor 1 | Input I1 | Bottle detection |
| Infrared Sensor 2 | Input I2 | Bottle detection |
| Conveyor motor control | Relay 2 | Conveyor activation |
| Bottle stopper control | Relay 4 | Stopper activation |

The infrared sensors use active-low detection in the current laboratory configuration:

- `true` (HIGH): No bottle detected
- `false` (LOW): Bottle detected

These values represent the configured sensor signals, not a guarantee of physical equipment safety.

## Network Configuration

| Parameter | Value |
|---|---|
| OPTA IP address | `192.168.0.50` |
| Laboratory PC Ethernet IP | `192.168.0.10` |
| Subnet mask | `255.255.255.0` |
| OPC UA port | `4840` |
| OPC UA endpoint | `opc.tcp://192.168.0.50:4840` |

## OpenFactory Integration

OpenFactory communicates with the OPTA through an OPC UA gateway.

**Asset ID:** `OPTA-LAB-001`

| Asset Variable | OPC UA Node ID |
|---|---|
| `digital_input_i1` | `ns=0;i=50069` |
| `digital_input_i2` | `ns=0;i=50070` |
| `relay_2` | `ns=0;i=50078` |
| `relay_4` | `ns=0;i=50080` |

These Node IDs are taken from the current laboratory OpenFactory device configuration and should be revalidated after firmware or library changes.

## Control Architecture

The current implementation separates physical I/O execution from supervisory software.

**Arduino OPTA responsibilities:**

- Read physical sensor inputs.
- Expose input values through OPC UA.
- Receive OPC UA write requests.
- Operate physical relay outputs.
- Manage the embedded OPC UA server.

**OpenFactory and application responsibilities:**

- Monitor the exposed equipment state.
- Request relay operations through the OpenFactory communication infrastructure.
- Provide the laboratory control dashboard.

The current firmware does not implement the complete autonomous bottle-handling production sequence. That distinction is important for future comparisons between local, distributed, and hybrid control.

## Current Limitations

The following capabilities have not yet been implemented or validated as station-level safety features:

- A local production-sequence state machine.
- A communication watchdog that enforces safe actuator behavior.
- Explicit startup and fault-recovery policies for the conveyor and stopper.
- Validated OPC UA recovery after network interruption.
- Deterministic timing instrumentation for latency experiments.

The sketch also uses NTP time synchronization with a compilation-date fallback. Timestamp accuracy has not been validated for research measurements.

**Safety:** OPC UA availability and displayed relay values must not be treated as proof of safe physical actuator states. Hardware isolation, appropriate protective circuitry, and independently verified stopping behavior remain necessary.

## Research Development

This baseline will be preserved while subsequent firmware versions investigate:

1. Local manufacturing control.
2. Distributed supervisory control.
3. Hybrid local and distributed control.
4. Communication latency and variability.
5. Network-failure detection and recovery.
6. Scalability with additional physical and virtual equipment.

Any functional firmware changes should be developed and tested separately from the preserved baseline.