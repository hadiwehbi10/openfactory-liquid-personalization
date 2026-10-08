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
  const response = await fetch(url, {
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


async function loadInitialState() {
  try {
    const serverState = await request(
      "/api/playground/state"
    );

    applyServerState(serverState);
  } catch (error) {
    console.error(error);

    addEvent(
      "Station unavailable",
      "Unable to load the simulated station state."
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


loadInitialState();