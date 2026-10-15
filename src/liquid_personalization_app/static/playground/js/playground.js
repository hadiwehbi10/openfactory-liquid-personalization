const state = {
  conveyorRunning: false,
  stopperEngaged: false,
  sensor1Detected: false,
  sensor2Detected: false,
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


async function request(url, options = {}) {
  const response = await fetch(window.location.pathname.replace(/\/playground\/?$/, "") + url, {
    method: options.method || "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json();
}


function applyServerState(serverState) {
  const availability = String(serverState.opta_availability ?? "UNKNOWN").trim().toUpperCase();
  document.getElementById("optaAvailability").textContent = availability === "AVAILABLE" ? "Available" : availability === "UNAVAILABLE" ? "Unavailable" : "Unknown";
  document.getElementById("optaHealthDot").style.background = availability === "AVAILABLE" ? "#10b981" : availability === "UNAVAILABLE" ? "#ef4444" : "#f59e0b";
  state.conveyorRunning = serverState.conveyor_running;
  state.stopperEngaged = serverState.stopper_engaged;
  state.sensor1Detected = serverState.sensor1_detected;
  state.sensor2Detected = serverState.sensor2_detected;

  renderState();
}


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


async function startConveyor() {
  try {
    const serverState = await request(
      "/api/playground/conveyor/start",
      { method: "POST" }
    );

    applyServerState(serverState);

    addEvent(
      "Conveyor started",
      "Simulation command accepted."
    );
  } catch (error) {
    console.error(error);

    addEvent(
      "Conveyor command failed",
      "Unable to start the simulated conveyor."
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
      "Conveyor stopped",
      "Simulation command accepted."
    );
  } catch (error) {
    console.error(error);

    addEvent(
      "Conveyor command failed",
      "Unable to stop the simulated conveyor."
    );
  }
}


async function engageStopper() {
  try {
    const serverState = await request(
      "/api/playground/stopper/engage",
      { method: "POST" }
    );

    applyServerState(serverState);

    addEvent(
      "Stopper engaged",
      "Simulation command accepted."
    );
  } catch (error) {
    console.error(error);

    addEvent(
      "Stopper command failed",
      "Unable to engage the simulated stopper."
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
      "Stopper released",
      "Simulation command accepted."
    );
  } catch (error) {
    console.error(error);

    addEvent(
      "Stopper command failed",
      "Unable to release the simulated stopper."
    );
  }
}


function updateApiStatus(online) {
  const status = online ? "API Responding" : "API Unavailable";
  document.getElementById("connectionLabel").textContent = status;
  document.getElementById("appApiStatus").textContent = status;
  document.getElementById("liveStatusLabel").textContent = online ? "Polling Active" : "Data Unavailable";
  for (const id of ["connectionDot", "liveStatusDot"]) document.getElementById(id).style.background = online ? "#34d399" : "#ef4444";
  elements.startConveyorButton.disabled = !online;
  elements.engageStopperButton.disabled = !online;
  if (!online) {
    document.getElementById("optaAvailability").textContent = "Unknown";
    document.getElementById("optaHealthDot").style.background = "#f59e0b";
    for (const id of ["sensor1SceneState", "sensor2SceneState", "sensor1Status", "sensor2Status"]) document.getElementById(id).textContent = "Unavailable";
    for (const id of ["conveyorSceneState", "conveyorControlState", "conveyorStatus", "stopperControlState", "stopperStatus", "stopperSceneState"]) document.getElementById(id).textContent = "Unknown";
  }
}

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


let statePollInFlight = false;

async function refreshLiveState() {
  if (statePollInFlight) return;
  statePollInFlight = true;
  try {
    applyServerState(await request("/api/playground/state"));
    updateApiStatus(true);
  } catch (error) {
    console.error("Live state refresh failed:", error);
    updateApiStatus(false);
  } finally {
    statePollInFlight = false;
  }
}

loadInitialState();
setInterval(refreshLiveState, 500);