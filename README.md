# OpenFactory Liquid Personalization

A research-driven manufacturing application developed as part of a Master of Applied Science (MASc) project in Mechanical Engineering at Concordia University.

The project investigates **distributed systems for manufacturing**, using OpenFactory and an Arduino OPTA industrial controller to study how control, monitoring, and orchestration responsibilities can be allocated between local and distributed software components.

The long-term application is a personalized liquid production line, in which customers specify product characteristics such as color, volume, and labeling.

## 1. Project Overview

The project currently includes:

- An OpenFactory-managed Flask application.
- A web dashboard for station monitoring and manual control.
- A simulation backend for software development.
- A real OpenFactory backend connected to an Arduino OPTA.
- Two physical bottle-detection sensors.
- Relay control of a conveyor and bottle stopper.
- Arduino firmware exposing the OPTA's I/O through OPC UA.
- Automated Python and JavaScript tests.
- Initial customer-order and virtual recipe-generation functionality.

The existing hardware integration supports manual supervisory control. A complete autonomous production sequence and automated filling system have not yet been implemented.

## 2. Research Objectives

The principal research direction is the evaluation of distributed manufacturing control architectures.

Planned investigations include:

1. Local control executed directly on the Arduino OPTA.
2. Distributed supervisory control through OpenFactory.
3. Hybrid control combining local execution with distributed orchestration.
4. Communication latency and timing variability.
5. Network-failure detection, recovery, and safe operating behavior.
6. Integration of virtual equipment and evaluation of scalability.

These are research objectives, not claims that every architecture or experiment has already been implemented.

## 3. System Architecture

The current laboratory system connects a web application to physical equipment through OpenFactory and an OPC UA gateway.

**Supervisory command path:**

```text
Web Dashboard
      |
      v
Flask Application
      |
      v
OpenFactory Asset SDK
      |
      v
OpenFactory Infrastructure
      |
      v
OPC UA Gateway
      |
      v
Arduino OPTA
      |
      v
Physical Relay Outputs
      |
      +--> Conveyor
      |
      +--> Bottle Stopper
```

**Sensor observation path:**

```text
Physical Sensors
      |
      v
Arduino OPTA
      |
      v
OPC UA Server
      |
      v
OpenFactory Gateway
      |
      v
OpenFactory Asset
      |
      v
Flask API
      |
      v
Web Dashboard
```

### Control Responsibilities

**Arduino OPTA**

- Interfaces electrically with sensors and actuators.
- Reads physical input signals.
- Exposes input values through its OPC UA server.
- Receives OPC UA output commands.
- Switches physical relay outputs.

**OpenFactory**

- Provides distributed communication and asset infrastructure.
- Integrates the OPTA through an OPC UA gateway.
- Exposes station attributes to applications.
- Routes supervisory requests toward the controller.

**Liquid Personalization Application**

- Provides an operator interface.
- Monitors OpenFactory-reported station values.
- Submits manual actuator-control requests.
- Supports software simulation.
- Generates virtual personalized-product recipes.

A successful software request does not independently verify physical actuator movement.

## 4. Current Laboratory Hardware

| Component | OPTA Connection | Purpose |
|---|---|---|
| Infrared Sensor 1 | Input I1 | Bottle detection |
| Infrared Sensor 2 | Input I2 | Bottle detection |
| Conveyor control | Relay 2 | Conveyor activation/deactivation |
| Bottle stopper | Relay 4 | Stopper actuation |

The installed sensors use active-low logic:

- `True` / HIGH: No bottle detected.
- `False` / LOW: Bottle detected.

The real station backend converts these values into the detection states expected by the dashboard.

### Network Configuration

| Parameter | Value |
|---|---|
| OPTA IP | `192.168.0.50` |
| Laboratory PC Ethernet IP | `192.168.0.10` |
| Subnet mask | `255.255.255.0` |
| OPC UA endpoint | `opc.tcp://192.168.0.50:4840` |
| OpenFactory asset UUID | `OPTA-LAB-001` |

### OpenFactory Variable Mapping

| Attribute | OPC UA Node ID |
|---|---|
| `digital_input_i1` | `ns=0;i=50069` |
| `digital_input_i2` | `ns=0;i=50070` |
| `relay_2` | `ns=0;i=50078` |
| `relay_4` | `ns=0;i=50080` |

These mappings represent the current laboratory configuration and must be revalidated if the firmware or OPC UA address space changes.

## 5. Project Structure

```text
openfactory-liquid-personalization/
|
|-- firmware/
|   |-- README.md
|   `-- OPCUA_Bidirectional_Test/
|       `-- OPCUA_Bidirectional_Test.ino
|
|-- src/
|   `-- liquid_personalization_app/
|       |-- app.py
|       |-- recipe.py
|       |-- station/
|       |   |-- base.py
|       |   |-- simulator.py
|       |   `-- openfactory_station.py
|       |-- templates/
|       `-- static/
|
|-- tests/
|
|-- app_liquid_personalization.yml
|-- uns_schema.yml
|-- Dockerfile
|-- pyproject.toml
`-- README.md
```

### Important Modules

**`app.py`**

Implements the Flask routes for the customer interface, operator playground, health endpoint, and station-control API.

**`station/base.py`**

Defines the common station interface and normalized state representation.

**`station/simulator.py`**

Implements an in-memory station simulator for development and automated testing.

**`station/openfactory_station.py`**

Connects the application to the `OPTA-LAB-001` OpenFactory asset and requests relay operations through the OpenFactory SDK.

**`recipe.py`**

Provides virtual RGB-based recipe calculations for personalized product orders.

**`firmware/`**

Contains the Arduino OPC UA firmware and hardware integration documentation. See [Firmware Documentation](firmware/README.md).

## 6. Station Operating Modes

The application supports two backend modes, selected using the `STATION_MODE` environment variable.

### Simulation Mode

```text
STATION_MODE=simulation
```

This is the default mode.

The application uses an in-memory simulator rather than communicating with physical equipment.

It is intended for interface development, testing, and demonstrations without hardware actuation.

### Real Mode

```text
STATION_MODE=real
```

The application connects to the physical station through OpenFactory.

The current real-mode implementation supports:

- Sensor monitoring.
- Conveyor relay control.
- Bottle-stopper relay control.
- Device-availability reporting.
- Supervisory checks before new actuator activation requests.

The current firmware does not implement an automatic bottle-handling state machine.

### Dashboard Limitations

The dashboard distinguishes API availability from reported OPTA availability.

When the OPTA is reported unavailable, the updated interface hides potentially stale equipment readings and disables new activation requests.

These are application-level precautions, not validated physical safety mechanisms.

OpenFactory availability does not, by itself, guarantee fresh sensor data or confirmed actuator motion.

## 7. Development Environment

The application is developed alongside `openfactory-connectors`.

For the current laboratory setup, both repositories are accessible from the same VS Code Dev Container environment:

```text
/workspaces/openfactory-connectors
/home/vscode/openfactory-liquid-personalization
```

The running OpenFactory infrastructure uses the Docker daemon associated with the `openfactory-connectors` Dev Container.

Using a separate Dev Container with a different Docker daemon may prevent the application from accessing the existing deployment.

### Install Development Dependencies

From the project directory, use a Python virtual environment and install the project with development dependencies:

```bash
python -m pip install -e ".[dev]"
```

The existing laboratory development environment uses a repository-local `.venv`.

## 8. Automated Tests

### Python Tests

Run:

```bash
.venv/bin/python -m pytest -q
```

Baseline recorded on October 29, 2026:

```text
15 passed
```

The tests cover application routes, recipe functionality, simulation behavior, real-station adapter behavior, and availability-based activation restrictions.

### JavaScript Dashboard Tests

The dashboard regression suite is located at:

```text
tests/test_playground_ui.cjs
```

It can be run using Node.js:

```bash
node --test tests/test_playground_ui.cjs
```

Alternatively, from the repository root, use an isolated Docker container:

```bash
docker run --rm --network none -v "$PWD:/repo:ro" -w /repo node:22-alpine node --test tests/test_playground_ui.cjs
```

The six JavaScript tests cover controller availability, stale-state presentation, simulation mode, API outages, activation-button behavior, and command-feedback wording.

Recorded result on October 29, 2026:

```text
6 passed
```

These are software tests using simulated responses. They do not verify physical actuator movement, hardware stopping behavior, or network recovery.

## 9. OpenFactory Deployment

The application is packaged as a Docker image and deployed through OpenFactory.

**Application configuration:**

```text
app_liquid_personalization.yml
```

**Application UUID:**

```text
LIQUID-PERSONALIZATION-APP
```

### Build Image

From the project root:

```bash
docker build -t liquid-personalization-app .
```

### Deployment Configuration

The application YAML uses the following environment variables:

- `STATION_MODE`
- `KAFKA_BROKER`
- `KSQLDB_URL`
- `ASSET_ROUTER_URL`
- `LIQUID_PERSONALIZATION_APP_LOG_LEVEL`

The Kafka, ksqlDB, and Asset Router settings must correspond to the running OpenFactory infrastructure.

The OpenFactory UNS schema is defined in:

```text
uns_schema.yml
```

When the infrastructure is configured and ready, the application can be deployed using:

```bash
ofa apps up app_liquid_personalization.yml
```

Do not redeploy an already running laboratory system without first checking the current service state and confirming that actuator operation is physically safe.

### Laboratory URLs

**Customer interface:**

```text
http://localhost/liquid-personalization-app/
```

**Station playground:**

```text
http://localhost/liquid-personalization-app/playground
```

**Application health:**

```text
http://localhost/liquid-personalization-app/health
```

The health endpoint reports application responsiveness; it does not establish OPTA connectivity or physical equipment safety.

### Inspect the OPTA Asset

From the configured OpenFactory environment:

```bash
ofa asset inspect OPTA-LAB-001
```

Reported values should be interpreted with care because previously received attributes may remain visible during communication failures.

## 10. Firmware Baseline

The firmware is derived from the Arduino OPC UA library's OPTA server example and includes laboratory-specific static Ethernet configuration.

The original source version was preserved in Git commit:

```text
2b30e21
```

Original source SHA-256:

```text
963ac4671f901347d1a79abb844bebbea713928d559230c0cb9e8bb5b198758a
```

A separately annotated source version is maintained in the repository.

No change to the OPTA's flashed firmware was performed as part of these documentation updates. The exact flashed binary has not been independently verified against the preserved source.

See [Firmware Documentation](firmware/README.md) for additional information.

## 11. Known Limitations and Research Challenges

The current implementation requires further development and validation in several areas.

**Local Control**

The OPTA currently exposes physical I/O through OPC UA but does not implement the complete autonomous manufacturing sequence.

**Safe Startup and Shutdown**

Explicit station-level startup, watchdog, fault-response, and recovery policies have not yet been implemented and validated.

**Communication Reliability**

A previous network-interruption experiment demonstrated that restoring Ethernet connectivity did not always restore a working OPC UA session until the OPTA was power-cycled.

The precise root cause and reliable recovery mechanism remain subjects for investigation.

**Command Acknowledgement**

An OpenFactory write request and subsequent reported relay state do not independently confirm physical actuator movement.

**Data Freshness**

Reported asset attributes may be cached or delayed. Explicit measurement timestamps and freshness thresholds have not yet been established.

**Performance Measurement**

The dashboard's approximately 500 ms polling interval is intended for visualization, not precise communication-latency measurement.

**Production Automation**

Physical liquid dispensing, RGB dosing pumps, mixing, filling, and labeling are not yet integrated into an autonomous production line.

**Access Control**

The current Flask control routes do not implement application-level user authentication or authorization. The control interface must remain restricted to a trusted laboratory environment until appropriate access controls are introduced.

## 12. Safety Considerations

This software is a research prototype and must not be treated as a certified industrial safety system.

The laboratory setup requires appropriate hardware protection, electrical isolation, safe operating procedures, and independently verified stopping mechanisms.

In particular:

- Communication loss must not be assumed to stop an energized actuator.
- Software-reported relay values are not independent physical feedback.
- An unavailable controller may be unable to receive a stop request.
- A successful HTTP response is not proof of physical motion or stopping.
- The current OpenFactory availability check is not a local hardware watchdog.

Actuator power should be isolated when conducting software-only tests or investigating failure behavior without a validated local safety strategy.

## 13. Research Roadmap

Future development will focus on progressively evaluating and improving the laboratory system:

1. Document and verify the existing firmware, software, and hardware baseline.
2. Investigate communication recovery and establish safe operating policies.
3. Implement local OPTA control logic for the manufacturing sequence.
4. Implement comparable distributed and hybrid control workflows.
5. Design repeatable latency, jitter, failure, and recovery experiments.
6. Record measurements and analyze differences between architectures.
7. Extend the laboratory with virtual devices and additional physical equipment.
8. Integrate personalized liquid dispensing and production orchestration.

The objective is to evaluate distributed manufacturing control using reproducible implementations and experimentally supported results.

---

**Research context:** Concordia University — MASc Mechanical Engineering.

**Current stage:** Physical OPC UA integration, manual supervisory control, firmware documentation, and experimental baseline development.