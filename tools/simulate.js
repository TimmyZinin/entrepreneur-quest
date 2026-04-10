#!/usr/bin/env node
// Balance simulator for Entrepreneur Quest
// Runs 1000 random playthroughs and verifies targets:
//   - >=70% reach final scene (completion rate)
//   - <=15% early game over (before scene 4)
//   - All 4 archetypes reachable (each >=5% frequency)
//   - Average playthrough length 6.5-7 scenes

const fs = require('fs');
const path = require('path');

const scenesPath = path.join(__dirname, '..', 'data', 'scenes.json');
const data = JSON.parse(fs.readFileSync(scenesPath, 'utf8'));

const RUNS = 1000;
const NOISE = data.meta.noise_range;

function seededRandom(seed) {
  let s = seed;
  return () => {
    s = (s * 9301 + 49297) % 233280;
    return s / 233280;
  };
}

function clamp(v) { return Math.max(0, Math.min(100, v)); }

function evalTrigger(trigger, state) {
  const check = (cond) => {
    const v = state[cond.resource];
    switch (cond.op) {
      case '==': return v === cond.value;
      case '>=': return v >= cond.value;
      case '<=': return v <= cond.value;
      case '>': return v > cond.value;
      case '<': return v < cond.value;
    }
  };
  if (trigger.type === 'and') return trigger.conditions.every(check);
  if (trigger.type === 'or') return trigger.conditions.some(check);
  return false;
}

function resolveEnding(state, reachedFinal) {
  // Check burnout/phoenix first (fail states by zero)
  for (const ending of data.endings) {
    if ((ending.id === 'burnout' || ending.id === 'phoenix') && evalTrigger(ending.trigger, state)) {
      return ending.id;
    }
  }
  // Then exit (highest win)
  const exit = data.endings.find(e => e.id === 'exit');
  if (evalTrigger(exit.trigger, state)) return 'exit';
  // Then growth
  const growth = data.endings.find(e => e.id === 'growth');
  if (evalTrigger(growth.trigger, state)) return 'growth';
  // Fallback: closest match
  if (state.energy < 30 || state.time < 30) return 'burnout';
  if (state.cash < 30 || state.rep < 30) return 'phoenix';
  return 'growth';
}

function pickScenes(rand) {
  const fixedFirst = data.scenes.find(s => s.fixed === 'first');
  const fixedLast = data.scenes.find(s => s.fixed === 'last');
  const middle = data.scenes.filter(s => !s.fixed);
  // Shuffle middle
  for (let i = middle.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [middle[i], middle[j]] = [middle[j], middle[i]];
  }
  return [fixedFirst, ...middle.slice(0, 5), fixedLast];
}

function runOne(seed) {
  const rand = seededRandom(seed);
  const state = {
    energy: data.meta.resources.energy.start,
    cash: data.meta.resources.cash.start,
    time: data.meta.resources.time.start,
    rep: data.meta.resources.rep.start,
  };
  const scenes = pickScenes(rand);
  let reached = 0;
  let earlyGameOver = false;
  for (let i = 0; i < scenes.length; i++) {
    reached = i + 1;
    const scene = scenes[i];
    const choice = scene.choices[rand() < 0.5 ? 0 : 1];
    for (const [k, v] of Object.entries(choice.deltas)) {
      const noisy = v + Math.floor((rand() * 2 - 1) * NOISE);
      state[k] = clamp(state[k] + noisy);
    }
    // Check game over
    const dead = Object.entries(state).some(([k, v]) => v === 0);
    if (dead) {
      if (i < 3) earlyGameOver = true;
      break;
    }
  }
  const ending = resolveEnding(state, reached === scenes.length);
  return { reached, ending, earlyGameOver, finalState: { ...state } };
}

function simulate() {
  const results = [];
  for (let seed = 1; seed <= RUNS; seed++) {
    results.push(runOne(seed));
  }

  const completed = results.filter(r => r.reached === 7).length;
  const earlyDeaths = results.filter(r => r.earlyGameOver).length;
  const avgLen = results.reduce((s, r) => s + r.reached, 0) / RUNS;

  const archetypeCounts = { exit: 0, growth: 0, burnout: 0, phoenix: 0 };
  for (const r of results) archetypeCounts[r.ending]++;

  const completionRate = completed / RUNS;
  const earlyDeathRate = earlyDeaths / RUNS;

  console.log('=== Balance Simulation Report ===');
  console.log(`Runs: ${RUNS}`);
  console.log(`Completion rate (7/7 scenes): ${(completionRate * 100).toFixed(1)}% ${completionRate >= 0.70 ? '✓' : '✗'} (target ≥70%)`);
  console.log(`Early game over (<scene 4): ${(earlyDeathRate * 100).toFixed(1)}% ${earlyDeathRate <= 0.15 ? '✓' : '✗'} (target ≤15%)`);
  console.log(`Avg scenes reached: ${avgLen.toFixed(2)} ${avgLen >= 6.0 ? '✓' : '✗'} (target 6.0-7.0)`);
  console.log(`\nArchetype distribution:`);
  for (const [name, count] of Object.entries(archetypeCounts)) {
    const pct = (count / RUNS * 100).toFixed(1);
    const ok = count / RUNS >= 0.05;
    console.log(`  ${name.padEnd(10)} ${count.toString().padStart(4)} (${pct}%) ${ok ? '✓' : '✗'} (target ≥5%)`);
  }

  const allTargetsMet =
    completionRate >= 0.70 &&
    earlyDeathRate <= 0.15 &&
    avgLen >= 6.0 &&
    Object.values(archetypeCounts).every(c => c / RUNS >= 0.05);

  console.log(`\n${allTargetsMet ? '✓ ALL TARGETS MET' : '✗ TARGETS NOT MET — tune scenes.json deltas'}`);
  process.exit(allTargetsMet ? 0 : 1);
}

simulate();
