
const state = {
  conveyorRunning: false,
  stopperEngaged: false,
  sensor1Detected: false,
  sensor2Detected: false,
  realMode: false,
  optaAvailable: false,
};


const elements = {
  conveyorVisual: document.getElementById("conveyorVisual"),
  stopperVisual: document.getElementById("stopperVisual"),

  conveyorSceneState: document.getElementById("conveyorSceneState"),
  conveyorSceneDot: document.getElementById("conveyorSceneDot"),

  conveyorControlState: document.getElementById("conveyorControlState"),
  stopperControlState: document.getElementById("stopperControlState"),

  conveyorStatus: document.getElementById("conveyorStatus"),
  stopperStatus: document.getElementById("stopperStatus"),

  sensor1SceneState: document.getElementById("sensor1SceneState"),
  sensor2SceneState: document.getElementById("sensor2SceneState"),

  sensor1Status: document.getElementById("sensor1Status"),
  sensor2Status: document.getElementById("sensor2Status"),

  startConveyorButton: document.getElementById("startConveyorButton"),
  stopConveyorButton: document.getElementById("stopConveyorButton"),

  engageStopperButton: document.getElementById("engageStopperButton"),
  releaseStopperButton: document.getElementById("releaseStopperButton"),

  clearEventsButton: document.getElementById("clearEventsButton"),

  eventList: document.getElementById("eventList"),
};


// ==========================================================
// API COMMUNICATION
// ==========================================================

async function request(url, options = {}) {
  const response = await fetch(
    window.location.pathname.replace(/\/playground\/?$/, "") + url,
    {
      method: options.method || "GET",
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json();
}


// ==========================================================
// EQUIPMENT AVAILABILITY AND UNKNOWN STATES
// ==========================================================

// The web API may remain available even when the physical
// OPTA controller becomes disconnected.
//
// Previously received sensor and relay values must not be
// presented as current hardware readings during an outage.
//
// This is a dashboard-level precaution, not a hardware
// safety mechanism.

function markHardwareUnknown() {
  const ids = [
    "sensor1SceneState",
    "sensor2SceneState",
    "sensor1Status",
    "sensor2Status",
    "conveyorSceneState",
    "conveyorControlState",
    "conveyorStatus",
    "stopperControlState",
    "stopperStatus",
    "stopperSceneState",
  ];

  for (const id of ids) {
    document.getElementById(id).textContent = "Unknown";
  }

  // Stop displaying inferred equipment activity.
  // This does not operate or stop the physical hardware.
  elements.conveyorVisual.classList.remove("is-running");
  elements.stopperVisual.classList.remove("is-engaged");
  elements.conveyorSceneDot.classList.remove("active");
}


// Prevent new activation requests when the API is offline,
// or when the real OPTA is reported unavailable.
//
// Stop/release requests remain accessible, but must never
// be mistaken for a guaranteed hardware emergency stop.

function updateActivationControls(apiOnline) {
  const canActivate =
    apiOnline && (!state.realMode || state.optaAvailable);

  elements.startConveyorButton.disabled = !canActivate;
  elements.engageStopperButton.disabled = !canActivate;
}


// ==========================================================
// APPLY STATE RECEIVED FROM THE BACKEND
// ==========================================================

function applyServerState(serverState) {
  const availability = String(
    serverState.opta_availability ?? "UNKNOWN"
  ).trim().toUpperCase();

  // The real OpenFactory backend includes opta_availability.
  // The simulator does not expose physical device availability.
  state.realMode = Object.prototype.hasOwnProperty.call(
    serverState,
    "opta_availability"
  );

  state.optaAvailable = availability === "AVAILABLE";

  document.getElementById("optaAvailability").textContent =
    !state.realMode
      ? "Simulation"
      : availability === "AVAILABLE"
        ? "Available"
        : availability === "UNAVAILABLE"
          ? "Unavailable"
          : "Unknown";

  document.getElementById("optaHealthDot").style.background =
    !state.realMode
      ? "#f59e0b"
      : availability === "AVAILABLE"
        ? "#10b981"
        : availability === "UNAVAILABLE"
          ? "#ef4444"
          : "#f59e0b";

  state.conveyorRunning = serverState.conveyor_running;
  state.stopperEngaged = serverState.stopper_engaged;
  state.sensor1Detected = serverState.sensor1_detected;
  state.sensor2Detected = serverState.sensor2_detected;

  renderState();

  // OpenFactory may retain previous attribute values after
  // communication is lost. Hide them instead of suggesting
  // that they represent current physical equipment state.
  if (state.realMode && !state.optaAvailable) {
    markHardwareUnknown();
  }

  updateActivationControls(true);
}


// ==========================================================
// RENDER STATION STATE
// ==========================================================

function renderState() {
  const conveyorText = state.conveyorRunning
    ? "Running"
    : "Stopped";

  const stopperText = state.stopperEngaged
    ? "Engaged"
    : "Released";

  const sensor1Text = state.sensor1Detected
    ? "Detected"
    : "Clear";

  const sensor2Text = state.sensor2Detected
    ? "Detected"
    : "Clear";

  elements.conveyorSceneState.textContent = conveyorText;
  elements.conveyorControlState.textContent = conveyorText;
  elements.conveyorStatus.textContent = conveyorText;

  elements.stopperControlState.textContent = stopperText;
  elements.stopperStatus.textContent = stopperText;

  document.getElementById("stopperSceneState").textContent =
    stopperText;

  elements.sensor1SceneState.textContent = sensor1Text;
  elements.sensor2SceneState.textContent = sensor2Text;

  elements.sensor1Status.textContent = sensor1Text;
  elements.sensor2Status.textContent = sensor2Text;

  elements.conveyorVisual.classList.toggle(
    "is-running",
    state.conveyorRunning
  );

  elements.stopperVisual.classList.toggle(
    "is-engaged",
    state.stopperEngaged
  );

  elements.conveyorSceneDot.classList.toggle(
    "active",
    state.conveyorRunning
  );
}


// ==========================================================
// EVENT TIMELINE
// ==========================================================

function currentTime() {
  return new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}


function addEvent(title, description) {
  const event = document.createElement("div");

  event.className = "event-item event-item-new";

  event.innerHTML = `
    <span class="event-time">
      ${currentTime()}
    </span>

    <div class="event-track">
      <span></span>
    </div>

    <div class="event-message">
      <strong>${title}</strong>
      <span>${description}</span>
    </div>
  `;

  elements.eventList.prepend(event);
}


// ==========================================================
// CONVEYOR COMMANDS
// ==========================================================

async function startConveyor() {
  try {
    const serverState = await request(
      "/api/playground/conveyor/start",
      { method: "POST" }
    );

    applyServerState(serverState);

    addEvent(
      "Conveyor start request completed",
      "API responded; physical operation not independently verified."
    );
  } catch (error) {
    console.error(error);

    addEvent(
      "Conveyor command failed",
      "Conveyor start request failed."
    );
  }
}


async function stopConveyor() {
  try {
    const serverState = await request(
      "/api/playground/conveyor/stop",
      { method: "POST" }
    );

    applyServerState(serverState);

    addEvent(
      "Conveyor stop request completed",
      "API responded; physical operation not independently verified."
    );
  } catch (error) {
    console.error(error);

    addEvent(
      "Conveyor command failed",
      "Conveyor stop request failed."
    );
  }
}


// ==========================================================
// STOPPER COMMANDS
// ==========================================================

async function engageStopper() {
  try {
    const serverState = await request(
      "/api/playground/stopper/engage",
      { method: "POST" }
    );

    applyServerState(serverState);

    addEvent(
      "Stopper engage request completed",
      "API responded; physical operation not independently verified."
    );
  } catch (error) {
    console.error(error);

    addEvent(
      "Stopper command failed",
      "Stopper engage request failed."
    );
  }
}


async function releaseStopper() {
  try {
    const serverState = await request(
      "/api/playground/stopper/release",
      { method: "POST" }
    );

    applyServerState(serverState);

    addEvent(
      "Stopper release request completed",
      "API responded; physical operation not independently verified."
    );
  } catch (error) {
    console.error(error);

    addEvent(
      "Stopper command failed",
      "Stopper release request failed."
    );
  }
}


// ==========================================================
// API HEALTH AND CONTROLLER AVAILABILITY
// ==========================================================

function updateApiStatus(online) {
  const status = online
    ? "API Responding"
    : "API Unavailable";

  document.getElementById("connectionLabel").textContent =
    status;

  document.getElementById("appApiStatus").textContent =
    status;

  document.getElementById("liveStatusLabel").textContent =
    online ? "Polling Active" : "Data Unavailable";

  for (const id of ["connectionDot", "liveStatusDot"]) {
    document.getElementById(id).style.background =
      online ? "#34d399" : "#ef4444";
  }

  updateActivationControls(online);

  if (!online) {
    document.getElementById("optaAvailability").textContent =
      "Unknown";

    document.getElementById("optaHealthDot").style.background =
      "#f59e0b";

    // The API is no longer supplying fresh readings.
    // Do not continue displaying cached equipment states.
    markHardwareUnknown();
  }
}


// ==========================================================
// INITIAL STATE LOADING
// ==========================================================

async function loadInitialState() {
  try {
    const serverState = await request(
      "/api/playground/state"
    );

    applyServerState(serverState);
    updateApiStatus(true);
  } catch (error) {
    console.error(error);
    updateApiStatus(false);

    addEvent(
      "Station unavailable",
      "Unable to retrieve station state from the API."
    );
  }
}


// ==========================================================
// USER INTERACTIONS
// ==========================================================

elements.startConveyorButton.addEventListener(
  "click",
  startConveyor
);

elements.stopConveyorButton.addEventListener(
  "click",
  stopConveyor
);

elements.engageStopperButton.addEventListener(
  "click",
  engageStopper
);

elements.releaseStopperButton.addEventListener(
  "click",
  releaseStopper
);

elements.clearEventsButton.addEventListener(
  "click",
  () => {
    elements.eventList.innerHTML = "";
  }
);


// ==========================================================
// LIVE STATE POLLING
// ==========================================================

// Prevent overlapping state-poll requests.
// The polling interval is for dashboard updates,
// not precise industrial timing measurements.

let statePollInFlight = false;

async function refreshLiveState() {
  if (statePollInFlight) {
    return;
  }

  statePollInFlight = true;

  try {
    const serverState = await request(
      "/api/playground/state"
    );

    applyServerState(serverState);
    updateApiStatus(true);
  } catch (error) {
    console.error("Live state refresh failed:", error);
    updateApiStatus(false);
  } finally {
    statePollInFlight = false;
  }
}


// ==========================================================
// APPLICATION STARTUP
// ==========================================================

// Disable activation buttons until the first successful
// state response establishes controller availability.
elements.startConveyorButton.disabled = true;
elements.engageStopperButton.disabled = true;

loadInitialState();

// Refresh dashboard approximately every 500 milliseconds.
// This does not provide real-time control guarantees.
setInterval(refreshLiveState, 500);
