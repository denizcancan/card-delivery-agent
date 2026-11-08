"use strict";
const $ = (s) => document.querySelector(s);
const STATUS = {
  pending: ["Aranmadı", ""], scheduled: ["Planlandı", "ok"], waitlisted: ["Bekleme listesi", "warn"],
  escalated: ["Operasyonda", "warn"], verification_failed: ["Doğrulanamadı", "bad"],
  not_reached: ["Ulaşılamadı", ""], declined: ["Reddetti", "bad"],
};
const REASONS = {
  capacity_request: "Ek kapasite", address_change: "Adres değişikliği", third_party: "Üçüncü kişiye teslim",
  verification_failed: "Kimlik doğrulanamadı", customer_request: "İnsanla görüşme", other: "Diğer",
};
const ENDPOINT_MS = 700;   // son konuşma sonucundan bu kadar sessizlik sonra cümle gönderilir
const IDLE_MS = 600;       // asistan sustuktan sonra mikrofon açılmadan önceki bekleme

let board = null;
let call = null;           // { ws, customer, turn, mode, ending, turnActive, lastEl, metrics }

const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

// ---------------- pano ----------------
async function refresh() {
  try { board = await (await fetch("/bank/board")).json(); render(); } catch { /* sunucu yeniden başlıyor olabilir */ }
}

function slotShort(id) {
  const s = board.slots.find((x) => x.slot_id === id);
  return s ? `${s.day} ${s.start}-${s.end}` : `#${id}`;
}

function render() {
  if (!board) return;
  const busy = !!call;
  $("#customers").innerHTML = board.customers.map((c) => {
    const [label, cls] = STATUS[c.status] || [c.status, ""];
    const appt = c.appointment
      ? `<div class="appt">${esc(c.appointment.label)}${c.appointment.source === "waitlist_promotion" ? " · listeden atandı" : ""}</div>` : "";
    return `<li class="customer ${call && call.customer.id === c.id ? "active" : ""}">
      <div class="row"><span class="name">${esc(c.full_name)}</span><span class="chip ${cls}">${label}</span></div>
      <div class="row muted small"><span>${esc(c.district)} · ${esc(c.delivery_address)}</span><span>${esc(c.phone)}</span></div>
      ${appt}
      <div class="row"><button class="primary small" data-call="${c.id}" ${busy ? "disabled" : ""}>Ara</button>
        ${c.appointment ? `<button class="ghost small" data-cancel="${c.appointment.appointment_id}" title="Teslimatı iptal et; boşalan yer bekleme listesine geçer">Teslimatı iptal et</button>` : ""}
      </div></li>`;
  }).join("");

  const booked = board.slots.reduce((a, s) => a + s.booked, 0);
  $("#capacity-summary").textContent = `${board.totals.customers} müşteri · ${board.totals.capacity} yer · ${booked} dolu`;
  $("#slots").innerHTML = board.slots.map((s) => `<div class="slot">
      <div class="row"><span class="district">${esc(s.district)}</span><span>${s.booked}/${s.capacity}</span></div>
      <div class="muted small">${esc(s.label)}</div>
      <div class="bar ${s.booked >= s.capacity ? "full" : ""}"><span style="width:${(100 * s.booked) / s.capacity}%"></span></div>
      <div class="who">${s.customers.map(esc).join(", ") || "—"}</div></div>`).join("");

  $("#waitlist").innerHTML = board.waitlist.length
    ? board.waitlist.map((w, i) => `<li><b>${i + 1}. ${esc(w.full_name)}</b> · ${esc(w.district)}<br>
        <span class="muted">Yer açılırsa: ${w.accepted_slot_ids.map(slotShort).map(esc).join(", ") || "yalnız gelecek hafta"}</span></li>`).join("")
    : `<li class="empty">Boş</li>`;
  $("#escalations").innerHTML = board.escalations.length
    ? board.escalations.map((e) => `<li><b>${esc(REASONS[e.reason] || e.reason)}</b> · ${esc(e.full_name)}${e.note ? `<br><span class="muted">${esc(e.note)}</span>` : ""}</li>`).join("")
    : `<li class="empty">Yok</li>`;
  $("#sms").innerHTML = board.sms.length
    ? board.sms.map((s) => `<li><b>${esc(s.full_name)}</b>: ${esc(s.body)}</li>`).join("")
    : `<li class="empty">Henüz yok</li>`;
  $("#reset").disabled = busy;
}

document.addEventListener("click", async (e) => {
  const callBtn = e.target.closest("[data-call]");
  if (callBtn) return startCall(Number(callBtn.dataset.call));
  const cancelBtn = e.target.closest("[data-cancel]");
  if (cancelBtn) {
    const r = await (await fetch(`/bank/appointments/${cancelBtn.dataset.cancel}/cancel`, { method: "POST" })).json();
    toast(r.promoted
      ? `Yer açıldı → ${r.promoted.full_name} otomatik atandı (${r.promoted.slot.label}), SMS gönderildi.`
      : "Teslimat iptal edildi; bu slotu bekleyen müşteri yok.");
    refresh();
  }
});

$("#reset").onclick = async () => {
  await fetch("/bank/admin/reset", { method: "POST" });
  $("#transcript").innerHTML = "";
  toast("Demo sıfırlandı.");
  refresh();
};

// ---------------- ses çıkışı ----------------
const audio = { ctx: null, next: 0, sources: new Set(), minTurn: 0, rate: 24000 };

function ensureAudio() {
  if (!audio.ctx) audio.ctx = new (window.AudioContext || window.webkitAudioContext)();
  if (audio.ctx.state === "suspended") audio.ctx.resume();
}

function playPcm(buf) {
  if (!call || call.mode !== "eleven") return;
  const turn = new DataView(buf).getUint32(0, true);
  if (turn < audio.minTurn) return;                       // söz kesilmiş tur
  const pcm = new Int16Array(buf, 4);
  const f32 = new Float32Array(pcm.length);
  for (let i = 0; i < pcm.length; i++) f32[i] = pcm[i] / 32768;
  const b = audio.ctx.createBuffer(1, f32.length, audio.rate);
  b.copyToChannel(f32, 0);
  const src = audio.ctx.createBufferSource();
  src.buffer = b;
  src.connect(audio.ctx.destination);
  const t = Math.max(audio.ctx.currentTime + 0.03, audio.next);
  src.start(t);
  audio.next = t + b.duration;
  audio.sources.add(src);
  src.onended = () => { audio.sources.delete(src); onActivityChange(); };
  onActivityChange();
}

function speakBrowser(text) {
  if (!("speechSynthesis" in window)) return;
  const u = new SpeechSynthesisUtterance(text);
  u.lang = "tr-TR";
  const v = speechSynthesis.getVoices().find((x) => (x.lang || "").toLowerCase().startsWith("tr"));
  if (v) u.voice = v;
  u.onend = u.onerror = () => setTimeout(onActivityChange, 50);
  speechSynthesis.speak(u);
  onActivityChange();
}

function stopAudio() {
  for (const s of audio.sources) { try { s.stop(); } catch { /* zaten bitti */ } }
  audio.sources.clear();
  audio.next = 0;
  if ("speechSynthesis" in window) speechSynthesis.cancel();
  onActivityChange();
}

const isSpeaking = () => audio.sources.size > 0 || ("speechSynthesis" in window && (speechSynthesis.speaking || speechSynthesis.pending));
const botBusy = () => !!call && (call.turnActive || isSpeaking());

// Yarı çift yönlü: asistan konuşurken/düşünürken mikrofon kapanır (hoparlör yankısı STT'ye girmesin).
let idleTimer = null;
function onActivityChange() {
  updateMicState();
  if (!call) return;
  if (botBusy()) {
    clearTimeout(idleTimer); idleTimer = null;
    if (!$("#barge").checked && !stt.paused) sttPause();
    return;
  }
  if (idleTimer) return;
  idleTimer = setTimeout(() => {
    idleTimer = null;
    if (!call || botBusy()) return;
    if (call.ending) finishCall(); else sttResume();
  }, IDLE_MS);
}

// ---------------- konuşma tanıma (Chrome Web Speech, tr-TR) ----------------
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
const stt = { rec: null, paused: false, finalText: "", lastInterim: "", timer: null, retries: 0, interimEl: null };

const sttWanted = () => !!call && !call.ending && $("#mic-on").checked && !stt.paused;

function sttStart() {
  if (!SR || stt.rec || !sttWanted()) { updateMicState(); return; }
  const rec = new SR();
  rec.lang = "tr-TR";
  rec.continuous = true;
  rec.interimResults = true;
  rec.onresult = onSpeech;
  rec.onerror = (e) => {
    if (e.error === "not-allowed" || e.error === "service-not-allowed") {
      $("#mic-on").checked = false;
      sys("Mikrofon izni yok; yazarak devam edebilirsin.", true);
    }
  };
  rec.onend = () => {
    if (stt.rec === rec) stt.rec = null;
    updateMicState();
    if (sttWanted()) setTimeout(sttStart, 150);          // Chrome sessizlikte kapatır; yeniden aç
  };
  try { rec.start(); stt.rec = rec; } catch { /* zaten çalışıyor */ }
  updateMicState();
}

function sttStop() {
  const r = stt.rec;
  stt.rec = null;
  if (r) { r.onend = null; try { r.abort(); } catch { /* yok say */ } }
  clearTimeout(stt.timer);
  stt.finalText = ""; stt.lastInterim = ""; stt.retries = 0;
  clearInterim();
  updateMicState();
}
function sttPause() { stt.paused = true; sttStop(); }
function sttResume() { stt.paused = false; sttStart(); }

function onSpeech(e) {
  let interim = "";
  for (let i = e.resultIndex; i < e.results.length; i++) {
    const r = e.results[i];
    if (r.isFinal) stt.finalText += r[0].transcript.trim() + " ";
    else interim += r[0].transcript;
  }
  const heard = (stt.finalText + interim).trim();
  if (!heard) return;
  if (botBusy()) {
    if (!$("#barge").checked) { stt.finalText = ""; return; }
    if (heard.split(/\s+/).length >= 2) bargeIn();
  }
  stt.lastInterim = heard;
  showInterim(heard);
  clearTimeout(stt.timer);
  stt.retries = 0;
  stt.timer = setTimeout(commitSpeech, ENDPOINT_MS);
  updateMicState(true);
}

function commitSpeech() {
  let text = stt.finalText.trim();
  if (!text) {                                            // Chrome final sonucu henüz vermedi
    if (++stt.retries < 5) { stt.timer = setTimeout(commitSpeech, 250); return; }
    text = stt.lastInterim.trim();
  }
  stt.finalText = ""; stt.lastInterim = ""; stt.retries = 0;
  clearInterim();
  if (text) sendUser(text);
}

function bargeIn() {
  if (!call) return;
  stopAudio();
  audio.minTurn = call.turn + 1;
  document.querySelectorAll(`.bubble.bot[data-turn="${call.turn}"]`).forEach((el) => el.classList.add("stale"));
  call.ws.send(JSON.stringify({ type: "interrupt" }));
}

function updateMicState(hearing = false) {
  const el = $("#mic-state");
  let text = "mikrofon kapalı", cls = "idle";
  if (call && !SR) text = "Bu tarayıcıda STT yok (Chrome kullan)";
  else if (call && isSpeaking()) { text = "asistan konuşuyor"; cls = "speaking"; }
  else if (call && call.turnActive) { text = "asistan düşünüyor…"; cls = "speaking"; }
  else if (stt.rec) { text = hearing ? "duyuyorum…" : "dinliyor"; cls = hearing ? "hearing" : "listening"; }
  el.textContent = text;
  el.className = `mic ${cls}`;
}

// ---------------- görüşme dökümü ----------------
function addEl(cls, text) {
  const el = document.createElement("div");
  el.className = cls;
  el.textContent = text;
  $("#transcript").appendChild(el);
  if (stt.interimEl) $("#transcript").appendChild(stt.interimEl);
  $("#transcript").scrollTop = 1e9;
  return el;
}
function sys(text, err = false) { addEl(`sys${err ? " err" : ""}`, text); }

function botSay(turn, text) {
  if (call.lastEl && call.lastEl.dataset.turn === String(turn)) {
    call.lastEl.textContent += " " + text;
  } else {
    call.lastEl = addEl("bubble bot", text);
    call.lastEl.dataset.turn = String(turn);
  }
}

function showInterim(text) {
  if (!stt.interimEl) stt.interimEl = addEl("bubble user interim", "");
  stt.interimEl.textContent = text;
  $("#transcript").scrollTop = 1e9;
}
function clearInterim() { if (stt.interimEl) stt.interimEl.remove(); stt.interimEl = null; }

function toolSummary(m) {
  const r = m.result || {};
  if (r.ok === false) return `${m.name} → reddedildi: ${r.error}`;
  switch (m.name) {
    case "verify_identity":
      return r.verified ? "verify_identity → doğrulandı" : r.locked ? "verify_identity → kilitlendi" : `verify_identity → yanlış (kalan hak ${r.attempts_left})`;
    case "list_available_slots":
      return r.slots && r.slots.length ? `list_available_slots → ${r.slots.map((s) => s.label).join(" | ")}` : "list_available_slots → ilçe dolu (taşma)";
    case "book_slot": return `book_slot → ${r.slot ? r.slot.label : "?"}`;
    case "join_waitlist": return `join_waitlist → sıra ${r.position}`;
    case "escalate": return `escalate(${m.input.reason}) → talep #${r.ticket_id}`;
    case "end_call": return `end_call → ${(STATUS[r.outcome] || [r.outcome])[0]}`;
    default: return m.name;
  }
}

function addTool(m) {
  const el = addEl(`tool${m.result && m.result.ok === false ? " err" : ""}`, toolSummary(m));
  el.title = JSON.stringify({ input: m.input, result: m.result }, null, 2);
  call.lastEl = null;
}

function setMetric(turn, patch) {
  const m = (call.metrics[turn] = Object.assign(call.metrics[turn] || {}, patch));
  if (!m.el && m.total_ms != null) m.el = addEl("metrics", "");
  if (!m.el) return;
  const parts = [];
  if (m.first_text_ms != null) parts.push(`LLM ilk metin ${m.first_text_ms} ms`);
  if (m.first_audio_ms != null) parts.push(`ilk ses ${m.first_audio_ms} ms`);
  if (m.total_ms != null) parts.push(`tur ${m.total_ms} ms`);
  m.el.textContent = parts.join(" · ");
}

// ---------------- arama yaşam döngüsü ----------------
function startCall(customerId) {
  if (call || !board) return;
  const customer = board.customers.find((c) => c.id === customerId);
  ensureAudio();
  const mode = $("#tts-mode").value;
  $("#transcript").innerHTML = "";
  const proto = location.protocol === "https:" ? "wss" : "ws";
  const ws = new WebSocket(`${proto}://${location.host}/ws/call/${customerId}?tts_mode=${mode}`);
  ws.binaryType = "arraybuffer";
  call = { ws, customer, turn: 0, mode, ending: false, turnActive: false, lastEl: null, metrics: {} };
  audio.minTurn = 0;
  $("#call-title").textContent = `${customer.full_name} aranıyor…`;
  $("#call-sub").textContent = "Claude oturumu açılıyor";
  $("#hangup").disabled = false;
  render();
  ws.onmessage = (ev) => (typeof ev.data === "string" ? handle(JSON.parse(ev.data)) : playPcm(ev.data));
  ws.onclose = cleanupCall;
}

function handle(m) {
  if (!call) return;
  switch (m.type) {
    case "call_started":
      $("#call-title").textContent = call.customer.full_name;
      $("#call-sub").textContent = `${m.model} · oturum ${m.connect_ms} ms · arama ${m.call_id}`;
      $("#text-input").disabled = false; $("#send").disabled = false;
      break;
    case "turn_started":
      call.turn = m.turn; call.turnActive = true; call.lastEl = null;
      onActivityChange();
      break;
    case "say":
      botSay(m.turn, m.text);
      if (call.mode === "browser" && m.turn >= audio.minTurn) speakBrowser(m.text);
      break;
    case "say_fallback":
      if (m.turn >= audio.minTurn) speakBrowser(m.text);
      break;
    case "tool": addTool(m); break;
    case "metric": setMetric(m.turn, { first_audio_ms: m.first_audio_ms }); break;
    case "turn_done":
      call.turnActive = false;
      setMetric(m.turn, { first_text_ms: m.first_text_ms, total_ms: m.total_ms });
      onActivityChange();
      break;
    case "board_changed": refresh(); break;
    case "call_ended": {
      call.ending = true;
      const [label, cls] = STATUS[m.outcome] || [m.outcome, ""];
      addEl(`chip outcome ${cls}`, `Sonuç: ${label}`);
      sttStop();
      onActivityChange();
      break;
    }
    case "tts_error":
      call.mode = "browser"; $("#tts-mode").value = "browser";
      sys(`ElevenLabs hatası, tarayıcı sesine geçildi: ${m.message}`, true);
      break;
    case "error": sys(m.message, true); break;
  }
}

function sendUser(text) {
  if (!call || call.ending) return;
  addEl("bubble user", text);
  call.lastEl = null;
  call.ws.send(JSON.stringify({ type: "user_text", text }));
}

function finishCall() {
  if (!call) return;
  try { call.ws.send(JSON.stringify({ type: "hangup" })); } catch { /* kapalı */ }
  call.ws.close();
}

function cleanupCall() {
  if (!call) return;
  sttStop();
  stopAudio();
  call = null;
  $("#hangup").disabled = true;
  $("#text-input").disabled = true; $("#send").disabled = true;
  $("#call-title").textContent = "Görüşme bitti";
  $("#call-sub").textContent = "Başka bir müşteri seçebilirsin.";
  updateMicState();
  refresh();
}

$("#hangup").onclick = () => { stopAudio(); finishCall(); };
$("#text-form").onsubmit = (e) => {
  e.preventDefault();
  const v = $("#text-input").value.trim();
  if (v) { sendUser(v); $("#text-input").value = ""; }
};
$("#tts-mode").onchange = () => {
  if (!call) return;
  call.mode = $("#tts-mode").value;
  if (call.mode !== "eleven") stopAudio();
  call.ws.send(JSON.stringify({ type: "tts_mode", mode: call.mode }));
};
$("#mic-on").onchange = () => ($("#mic-on").checked ? sttResume() : sttStop());
$("#barge").onchange = () => onActivityChange();

function toast(msg) {
  const t = $("#toast");
  t.textContent = msg; t.hidden = false;
  clearTimeout(toast._t);
  toast._t = setTimeout(() => (t.hidden = true), 4500);
}

fetch("/api/config").then((r) => r.json()).then((c) => {
  audio.rate = c.sample_rate;
  $("#meta").textContent = `LLM: ${c.model} (Agent SDK) · TTS: ${c.tts_available ? c.tts_model : "yok"} · STT: Chrome Web Speech`;
  if (!c.tts_available) $("#tts-mode").value = "browser";
});
if ("speechSynthesis" in window) speechSynthesis.getVoices();
refresh();
setInterval(refresh, 3000);
