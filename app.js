const EVENTS = JSON.parse(document.getElementById("events-data").textContent);

const storageKey = "burla-techweek-event-decisions-v1";
const peopleList = document.getElementById("peopleList");
const decisionCounts = document.getElementById("decisionCounts");
const resultCount = document.getElementById("resultCount");
const tierFilter = document.getElementById("tier");
const dayFilter = document.getElementById("day");
const neighborhoodFilter = document.getElementById("neighborhood");
const decisionFilter = document.getElementById("decision");
const searchInput = document.getElementById("search");
const partifulOnly = document.getElementById("partifulOnly");

const dayLabels = {
  "2026-05-26": "Tue, May 26",
  "2026-05-27": "Wed, May 27",
  "2026-05-28": "Thu, May 28",
  "2026-05-29": "Fri, May 29",
  "2026-05-30": "Sat, May 30",
  "2026-05-31": "Sun, May 31",
};

let decisions = loadDecisions();

function loadDecisions() {
  try {
    return JSON.parse(localStorage.getItem(storageKey)) || {};
  } catch {
    return {};
  }
}

function saveDecisions() {
  localStorage.setItem(storageKey, JSON.stringify(decisions));
}

function decisionFor(ev) {
  return decisions[String(ev.id)] || "Unmarked";
}

function populateOptionsOnce() {
  const days = [...new Set(EVENTS.map((e) => e.date).filter(Boolean))].sort();
  for (const d of days) {
    const opt = document.createElement("option");
    opt.value = d;
    opt.textContent = dayLabels[d] || d;
    dayFilter.appendChild(opt);
  }

  const neighborhoods = [
    ...new Set(EVENTS.flatMap((e) => e.neighborhoods || []).filter(Boolean)),
  ].sort();
  for (const n of neighborhoods) {
    const opt = document.createElement("option");
    opt.value = n;
    opt.textContent = n;
    neighborhoodFilter.appendChild(opt);
  }
}

function filteredEvents() {
  const tier = tierFilter.value;
  const day = dayFilter.value;
  const neighborhood = neighborhoodFilter.value;
  const decision = decisionFilter.value;
  const search = searchInput.value.trim().toLowerCase();
  const partifulOnlyChecked = partifulOnly.checked;

  return EVENTS.filter((ev) => {
    if (tier === "actionable") {
      if (ev.score < 30) return false;
    } else if (tier !== "all") {
      if (ev.tier !== tier) return false;
    }
    if (day && ev.date !== day) return false;
    if (neighborhood && !(ev.neighborhoods || []).includes(neighborhood)) return false;
    if (decision && decisionFor(ev) !== decision) return false;
    if (partifulOnlyChecked && !ev.partiful) return false;
    if (search) {
      const blob = `${ev.name} ${(ev.hosts || []).join(" ")} ${(ev.tags || []).join(" ")}`.toLowerCase();
      if (!blob.includes(search)) return false;
    }
    return true;
  });
}

function render() {
  renderCounts();
  const visible = filteredEvents();
  resultCount.textContent = `${visible.length} event${visible.length === 1 ? "" : "s"} shown - ranked by Burla.dev ICP fit`;
  peopleList.innerHTML = visible.map((ev, i) => renderEvent(ev, i)).join("");
}

function renderCounts() {
  const counts = EVENTS.reduce(
    (acc, ev) => {
      const d = decisionFor(ev);
      acc[d] = (acc[d] || 0) + 1;
      return acc;
    },
    { Interested: 0, Maybe: 0, Not: 0, Unmarked: 0 }
  );
  decisionCounts.innerHTML = `
    <span class="count-pill">${EVENTS.length} events scored</span>
    <span class="count-pill">${counts.Interested} interested</span>
    <span class="count-pill">${counts.Maybe} maybe</span>
    <span class="count-pill">${counts.Not} not</span>
  `;
}

function scoreClass(score) {
  if (score >= 70) return "";
  if (score >= 40) return "mid";
  return "low";
}

function formatTime(t) {
  if (!t) return "";
  const [hStr, mStr] = t.split(":");
  let h = parseInt(hStr, 10);
  const m = mStr || "00";
  const suffix = h >= 12 ? "pm" : "am";
  h = h % 12;
  if (h === 0) h = 12;
  return m === "00" ? `${h}${suffix}` : `${h}:${m}${suffix}`;
}

function renderEvent(ev, index) {
  const decision = decisionFor(ev);
  const apply = ev.partiful
    ? `<a class="apply-link" href="${escapeAttr(ev.partiful)}" target="_blank" rel="noreferrer">Apply on Partiful</a>`
    : `<span class="apply-link missing">${ev.isInviteOnly ? "Invite only" : "No public link"}</span>`;

  const guestsLink = ev.guests_slug
    ? `<a class="apply-link guests-link" href="phase2_guests/guests-${escapeAttr(ev.guests_slug)}.html">View scored guests (${ev.guests_parsed || "?"}/${ev.guests_declared || "?"})</a>`
    : "";

  const meta = [
    dayLabels[ev.date] || ev.date,
    formatTime(ev.time),
    ev.location || (ev.neighborhoods || []).join(", "),
  ].filter(Boolean);

  const hosts = (ev.hosts && ev.hosts.length ? ev.hosts : [ev.company]).filter(Boolean);

  return `
    <article class="person-card">
      <div class="person-main">
        <div class="person-top">
          <span class="rank-pill">#${index + 1}</span>
          <h2>${escapeHtml(ev.name)}</h2>
          <span class="score-pill ${scoreClass(ev.score)}">${ev.score}</span>
          <span class="tier-pill">${escapeHtml(ev.tier)}</span>
          ${ev.isInviteOnly ? '<span class="invite-pill">Invite only</span>' : ""}
        </div>
        <p class="subtitle">${escapeHtml(hosts.join(", "))}</p>
        <div class="meta-row">
          ${meta.map((m) => `<span class="meta-pill">${escapeHtml(m)}</span>`).join("")}
        </div>
        <p class="evidence">${escapeHtml(ev.evidence)}</p>
        <div class="tags">
          ${(ev.tags || []).map((t) => `<span class="data-pill">${escapeHtml(t)}</span>`).join("")}
        </div>
      </div>
      <div class="person-actions">
        ${apply}
        ${guestsLink}
        <div class="decision-buttons" data-id="${escapeAttr(String(ev.id))}">
          ${renderDecisionButton("Interested", decision)}
          ${renderDecisionButton("Maybe", decision)}
          ${renderDecisionButton("Not", decision)}
        </div>
      </div>
    </article>
  `;
}

function renderDecisionButton(value, current) {
  const active = value === current ? " active" : "";
  return `<button class="${active}" type="button" data-decision="${escapeAttr(value)}">${value}</button>`;
}

peopleList.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-decision]");
  if (!button) return;
  const group = button.closest("[data-id]");
  const id = group.dataset.id;
  const decision = button.dataset.decision;
  decisions[id] = decisions[id] === decision ? "Unmarked" : decision;
  saveDecisions();
  render();
});

for (const el of [tierFilter, dayFilter, neighborhoodFilter, decisionFilter, partifulOnly]) {
  el.addEventListener("change", render);
}
searchInput.addEventListener("input", () => {
  clearTimeout(searchInput._t);
  searchInput._t = setTimeout(render, 80);
});

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function escapeAttr(value) {
  return escapeHtml(value);
}

populateOptionsOnce();
render();
