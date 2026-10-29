/**
 * Regression tests for the browser-side station dashboard.
 *
 * No network requests or hardware commands are sent. The DOM and fetch are
 * simulated, while the actual playground.js file is executed in a Node VM.
 * Run: node --test tests/test_playground_ui.cjs
 */

'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const scriptPath = path.join(
  __dirname,
  '..',
  'src',
  'liquid_personalization_app',
  'static',
  'playground',
  'js',
  'playground.js'
);
const script = fs.readFileSync(scriptPath, 'utf8');

function makeElement() {
  const classes = new Set();
  return {
    textContent: '',
    innerHTML: '',
    style: {},
    disabled: false,
    children: [],
    prepend(child) { this.children.unshift(child); },
    addEventListener() {},
    classList: {
      add(name) { classes.add(name); },
      remove(name) { classes.delete(name); },
      contains(name) { return classes.has(name); },
      toggle(name, enabled) {
        if (enabled === undefined ? !classes.has(name) : enabled) classes.add(name);
        else classes.delete(name);
      },
    },
  };
}

function dashboard() {
  const nodes = new Map();
  const get = id => {
    if (!nodes.has(id)) nodes.set(id, makeElement());
    return nodes.get(id);
  };

  // The startup state request never resolves, so tests have exclusive control
  // over the state being applied. No real HTTP request is made.
  const context = {
    document: { getElementById: get, createElement: makeElement },
    window: { location: { pathname: '/liquid-personalization-app/playground' } },
    fetch: () => new Promise(() => {}),
    setInterval: () => 0,
    console,
  };
  vm.createContext(context);
  vm.runInContext(script, context, { filename: 'playground.js' });
  return {
    context,
    get,
    apply: data => vm.runInContext(`applyServerState(${JSON.stringify(data)})`, context),
    api: online => vm.runInContext(`updateApiStatus(${online})`, context),
  };
}

const readings = {
  sensor1_detected: true,
  sensor2_detected: false,
  conveyor_running: true,
  stopper_engaged: true,
};

test('available real OPTA displays readings and permits activation', () => {
  const ui = dashboard();
  ui.apply({ ...readings, opta_availability: 'AVAILABLE' });
  assert.equal(ui.get('optaAvailability').textContent, 'Available');
  assert.equal(ui.get('sensor1Status').textContent, 'Detected');
  assert.equal(ui.get('conveyorStatus').textContent, 'Running');
  assert.equal(ui.get('startConveyorButton').disabled, false);
  assert.equal(ui.get('engageStopperButton').disabled, false);
});

test('unavailable real OPTA hides cached readings and blocks activation', () => {
  const ui = dashboard();
  ui.apply({ ...readings, opta_availability: 'AVAILABLE' });
  ui.apply({ ...readings, opta_availability: 'UNAVAILABLE' });
  assert.equal(ui.get('optaAvailability').textContent, 'Unavailable');
  for (const id of ['sensor1Status', 'sensor2Status', 'conveyorStatus', 'stopperStatus', 'conveyorSceneState', 'stopperSceneState']) {
    assert.equal(ui.get(id).textContent, 'Unknown', id);
  }
  assert.equal(ui.get('conveyorVisual').classList.contains('is-running'), false);
  assert.equal(ui.get('stopperVisual').classList.contains('is-engaged'), false);
  assert.equal(ui.get('startConveyorButton').disabled, true);
  assert.equal(ui.get('engageStopperButton').disabled, true);
});

test('unknown OPTA availability fails closed for activation', () => {
  const ui = dashboard();
  ui.apply({ ...readings, opta_availability: 'UNKNOWN' });
  assert.equal(ui.get('sensor1Status').textContent, 'Unknown');
  assert.equal(ui.get('startConveyorButton').disabled, true);
  assert.equal(ui.get('engageStopperButton').disabled, true);
});

test('simulation works without physical OPTA availability', () => {
  const ui = dashboard();
  ui.apply(readings);
  assert.equal(ui.get('optaAvailability').textContent, 'Simulation');
  assert.equal(ui.get('conveyorStatus').textContent, 'Running');
  assert.equal(ui.get('startConveyorButton').disabled, false);
  assert.equal(ui.get('engageStopperButton').disabled, false);
});

test('API outage hides previously received readings and blocks activation', () => {
  const ui = dashboard();
  ui.apply({ ...readings, opta_availability: 'AVAILABLE' });
  ui.api(false);
  assert.equal(ui.get('optaAvailability').textContent, 'Unknown');
  assert.equal(ui.get('conveyorStatus').textContent, 'Unknown');
  assert.equal(ui.get('sensor1Status').textContent, 'Unknown');
  assert.equal(ui.get('startConveyorButton').disabled, true);
  assert.equal(ui.get('engageStopperButton').disabled, true);
});

test('successful command message does not claim verified physical motion', async () => {
  const ui = dashboard();
  ui.context.fetch = async () => ({
    ok: true,
    json: async () => ({ ...readings, opta_availability: 'AVAILABLE' }),
  });
  await vm.runInContext('startConveyor()', ui.context);
  const entry = ui.get('eventList').children[0].innerHTML;
  assert.match(entry, /Conveyor start request completed/);
  assert.match(entry, /physical operation not independently verified/i);
  assert.doesNotMatch(entry, /Simulation command accepted/);
});
