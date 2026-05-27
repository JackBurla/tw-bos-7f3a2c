// Per-event scored-guests dashboard. Mirrors HCLS people layout, with
// tier / decision / search / unverified filters.

const dataNode = document.getElementById("guests-data");
const payload = JSON.parse(dataNode.textContent);
const guests = payload.guests || [];

const storageKey = `burla-guest-decisions-${payload.event_id}-v1`;

const peopleList = document.getElementById("peopleList");
const decisionCounts = document.getElementById("decisionCounts");
const resultCount = document.getElementById("resultCount");
const tierSel = document.getElementById("tier");
const decisionSel = document.getElementById("decision");
const searchInput = document.getElementById("search");
const hideUnverified = document.getElementById("hideUnverified");

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

function tierOf(score) {
  if (score >= 90) return "top";
  if (score >= 75) return "strong";
  if (score >= 55) return "aware";
  return "other";
}

function filtered() {
  const tier = tierSel.value;
  const dec = decisionSel.value;
  const q = searchInput.value.trim().toLowerCase();
  const hideUnv = hideUnverified.checked;

  return guests.filter((g) => {
    if (hideUnv && g.needs_verification) return false;

    const t = tierOf(g.score);
    if (tier === "top" && t !== "top") return false;
    if (tier === "strong" && t !== "strong") return false;
    if (tier === "aware" && t !== "aware") return false;
    if (tier === "other" && t !== "other") return false;
    if (tier === "actionable" && g.score < 55) return false;

    const current = decisions[g.name] || "Unmarked";
    if (dec && dec !== current) return false;

    if (q) {
      const hay = [
        g.name,
        g.company,
        g.role,
        (g.tags || []).join(" "),
        g.evidence,
      ]
        .join(" ")
        .toLowerCase();
      if (!hay.includes(q)) return false;
    }

    return true;
  });
}

function renderCounts() {
  const counts = guests.reduce(
    (acc, g) => {
      const d = decisions[g.name] || "Unmarked";
      acc[d] = (acc[d] || 0) + 1;
      return acc;
    },
    { Interested: 0, Maybe: 0, Not: 0, Unmarked: 0 }
  );
  decisionCounts.innerHTML = `
    <span class="count-pill">${guests.length} guests</span>
    <span class="count-pill">${counts.Interested} interested</span>
    <span class="count-pill">${counts.Maybe} maybe</span>
    <span class="count-pill">${counts.Not} not</span>
  `;
}

function render() {
  renderCounts();
  const list = filtered();
  resultCount.textContent = `Showing ${list.length} of ${guests.length} guests`;
  if (!list.length) {
    peopleList.innerHTML = `<p class="empty">No guests match the current filters.</p>`;
    return;
  }
  peopleList.innerHTML = list.map(renderGuest).join("");
}

function renderGuest(g, index) {
  const decision = decisions[g.name] || "Unmarked";
  const t = tierOf(g.score);
  const tierClass = `tier-${t}`;
  const linkedin = g.linkedin
    ? `<a class="linkedin-link" href="${escapeAttr(g.linkedin)}" target="_blank" rel="noreferrer">LinkedIn</a>`
    : `<span class="linkedin-link missing">No profile verified</span>`;
  const verify = g.needs_verification
    ? `<span class="data-pill unverified">needs verification</span>`
    : "";
  const tagsHtml = (g.tags || [])
    .map((tag) => `<span class="data-pill">${escapeHtml(tag)}</span>`)
    .join("");
  const role = g.role || "Role unknown";
  const company = g.company || "Company unknown";
  return `
    <article class="person-card ${tierClass}">
      <div class="person-main">
        <div class="person-top">
          <span class="rank-pill">#${index + 1}</span>
          <h2>${escapeHtml(g.name)}</h2>
          <span class="score-pill">${g.score}</span>
        </div>
        <p class="subtitle">${escapeHtml(role)} | ${escapeHtml(company)}</p>
        <p class="evidence">${escapeHtml(g.evidence || "No evidence captured.")}</p>
        <div class="tags">${tagsHtml}${verify}</div>
      </div>
      <div class="person-actions">
        ${linkedin}
        <div class="decision-buttons" data-person="${escapeAttr(g.name)}">
          ${renderDecisionButton("Interested", decision)}
          ${renderDecisionButton("Maybe", decision)}
          ${renderDecisionButton("Not", decision)}
        </div>
      </div>
    </article>
  `;
}

function renderDecisionButton(value, current) {
  const label = value === "Not" ? "Not" : value;
  const active = value === current ? " active" : "";
  return `<button class="${active}" type="button" data-decision="${escapeAttr(value)}">${label}</button>`;
}

peopleList.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-decision]");
  if (!button) return;
  const group = button.closest("[data-person]");
  const name = group.dataset.person;
  const decision = button.dataset.decision;
  decisions[name] = decisions[name] === decision ? "Unmarked" : decision;
  saveDecisions();
  render();
});

[tierSel, decisionSel, hideUnverified].forEach((el) =>
  el.addEventListener("change", render)
);
searchInput.addEventListener("input", render);

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

render();
