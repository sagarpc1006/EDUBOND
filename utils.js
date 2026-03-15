// EduBond Shared Utilities
const CHAT_STORE_KEY = 'edubond_chats_v1';
let activeThreadId = null;
let activeThreadMeta = null;
let chatPollTimer = null;
let notifPollTimer = null;

// ── Auth helpers ──────────────────────────────────
function normalizeUser(u) {
  if (!u || typeof u !== 'object') return u;
  const user = { ...u };
  const emailKey = (user.email || '').toLowerCase();
  const savedProfile = emailKey
    ? JSON.parse(localStorage.getItem(`edubond_profile_${emailKey}`) || 'null')
    : null;
  const rawName = (user.name || '').trim();
  if (!rawName) {
    const base = (savedProfile?.name || user.email || user.username || 'user').split('@')[0];
    user.name = base
      .replace(/[._-]+/g, ' ')
      .replace(/\b\w/g, c => c.toUpperCase())
      .trim() || 'User';
  }
  if (!user.avatar && savedProfile?.avatar) user.avatar = savedProfile.avatar;
  if (!user.year) user.year = '3rd Year';
  if (!user.branch) user.branch = 'CSE';
  if (!user.college) user.college = 'Indira ICEM';
  return user;
}

const Auth = {
  getUser: () => {
    try {
      const parsed = JSON.parse(localStorage.getItem('edubond_user') || 'null');
      const user = normalizeUser(parsed);
      if (user && JSON.stringify(parsed) !== JSON.stringify(user)) {
        localStorage.setItem('edubond_user', JSON.stringify(user));
      }
      return user;
    } catch {
      return null;
    }
  },
  setUser: (u) => localStorage.setItem('edubond_user', JSON.stringify(normalizeUser(u))),
  logout: () => {
    Object.keys(localStorage)
      .filter(key => key.startsWith('edubond_profile'))
      .forEach(key => localStorage.removeItem(key));
    localStorage.removeItem('edubond_user');
    localStorage.removeItem('edubond_profile');
    localStorage.removeItem('edubond_access');
    localStorage.removeItem('edubond_refresh');
    window.location.href = 'index.html';
  },
  requireAuth: () => {
    const u = Auth.getUser();
    if (!u) { window.location.href = 'index.html'; return null; }
    return u;
  }
};

async function syncCurrentUserFromApi() {
  const token = localStorage.getItem('edubond_access') || '';
  const current = Auth.getUser();
  if (!token || !current?.email) return current;
  try {
    const res = await fetch('/api/auth/profile/', {
      method: 'GET',
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) return current;
    const data = await res.json();
    const merged = {
      ...current,
      name: data.name || current.name,
      email: (data.email || current.email || '').toLowerCase(),
      year: data.year || current.year,
      branch: data.branch || current.branch,
      college: data.college_name || current.college || 'Indira ICEM',
      avatar: data.profile_pic || current.avatar || '',
      is_staff: !!data.is_staff,
      is_superuser: !!data.is_superuser,
    };
    Auth.setUser(merged);
    return merged;
  } catch {
    return current;
  }
}

function refreshNavbarAvatar(user) {
  const navAvatar = document.querySelector('#mainNav .avatar');
  if (!navAvatar || !user) return;
  const initials = (user.name || 'U').split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
  navAvatar.innerHTML = user.avatar
    ? `<img src="${user.avatar}" alt="${user.name || 'User'}" style="width:100%;height:100%;object-fit:cover;border-radius:50%" />`
    : initials;
}

// ── Toast ──────────────────────────────────────────
function showToast(msg, type = 'default', duration = 3000) {
  let tc = document.getElementById('toastContainer');
  if (!tc) {
    tc = document.createElement('div');
    tc.id = 'toastContainer';
    tc.className = 'toast-container';
    document.body.appendChild(tc);
  }
  const icons = { success: '✅', error: '❌', warning: '⚠️', default: 'ℹ️' };
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.innerHTML = `<span>${icons[type]}</span><span>${msg}</span>`;
  tc.appendChild(t);
  setTimeout(() => { t.style.opacity = '0'; t.style.transform = 'translateX(100%)'; t.style.transition = '0.3s'; setTimeout(() => t.remove(), 300); }, duration);
}

// ── Chat Box ────────────────────────────────────────
function getChatStore() {
  try {
    return JSON.parse(localStorage.getItem(CHAT_STORE_KEY) || '{"threads":{}}');
  } catch {
    return { threads: {} };
  }
}

function saveChatStore(store) {
  localStorage.setItem(CHAT_STORE_KEY, JSON.stringify(store));
}

function chatThreadId(name) {
  return String(name || 'unknown').trim().toLowerCase().replace(/\s+/g, '_');
}

function currentUserKey() {
  const u = Auth.getUser() || {};
  return String(u.email || u.username || u.name || 'user').trim().toLowerCase();
}

function currentUserName() {
  const u = Auth.getUser() || {};
  return String(u.name || 'User').trim();
}

async function requestConnection(otherName, otherKey, reason = '') {
  const me = Auth.getUser() || {};
  const meKey = currentUserKey();
  const toKey = String(otherKey || otherName || '').trim().toLowerCase();
  if (!toKey || !meKey || toKey === meKey) {
    return { connected: true, status: 'accepted' };
  }
  const res = await fetch('/api/chat/connections/request/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      from_key: meKey,
      from_name: currentUserName(),
      to_key: toKey,
      to_name: otherName || 'User',
      reason: String(reason || '').slice(0, 255),
    }),
  });
  if (!res.ok) throw new Error('request failed');
  return await res.json();
}

async function apiEnsureThread(name, initials, subject = '', otherKey = '') {
  const meKey = currentUserKey();
  const payload = {
    me_key: meKey,
    me_name: currentUserName(),
    other_key: String(otherKey || name || '').trim().toLowerCase().replace(/\s+/g, '_'),
    other_name: name,
    subject: subject || '',
  };
  const res = await fetch('/api/chat/threads/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('thread create failed');
  const t = await res.json();
  return {
    id: t.id,
    name: t.other_name || name,
    initials: initials || ((t.other_name || name || 'U').split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()),
    subject: t.subject || subject || '',
  };
}

async function apiFetchThreads() {
  const meKey = encodeURIComponent(currentUserKey());
  const res = await fetch(`/api/chat/threads/?me_key=${meKey}`);
  if (!res.ok) throw new Error('threads fetch failed');
  return await res.json();
}

async function apiFetchMessages(threadId) {
  const meKey = encodeURIComponent(currentUserKey());
  const res = await fetch(`/api/chat/threads/${threadId}/messages/?me_key=${meKey}`);
  if (!res.ok) throw new Error('messages fetch failed');
  const data = await res.json();
  return data.map(m => ({
    sender: String(m.sender_key || '').toLowerCase() === currentUserKey() ? 'me' : 'other',
    text: m.content,
    ts: new Date(m.created_at).getTime(),
  }));
}

async function apiSendMessage(threadId, text) {
  const res = await fetch(`/api/chat/threads/${threadId}/messages/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      me_key: currentUserKey(),
      me_name: currentUserName(),
      content: text,
    }),
  });
  if (!res.ok) throw new Error('send failed');
  return await res.json();
}

function ensureThread(name, initials, subject = '') {
  const store = getChatStore();
  const id = chatThreadId(name);
  if (!store.threads[id]) {
    store.threads[id] = { id, name, initials, subject, unread: 0, messages: [] };
  } else {
    store.threads[id].name = name || store.threads[id].name;
    store.threads[id].initials = initials || store.threads[id].initials;
    if (subject) store.threads[id].subject = subject;
  }
  saveChatStore(store);
  return store.threads[id];
}

function formatChatTime(ts) {
  return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function renderMessages(thread) {
  const msgs = document.getElementById('chatMessages');
  if (!msgs) return;
  msgs.innerHTML = thread.messages.map(m => `
    <div class="chat-msg ${m.sender === 'me' ? 'sent' : 'recv'}">
      <div><div class="bubble">${m.text}</div><div class="time">${formatChatTime(m.ts)}</div></div>
    </div>
  `).join('') || `
    <div class="chat-msg recv">
      <div><div class="bubble">Hi! How can I help?</div><div class="time">Just now</div></div>
    </div>
  `;
  msgs.scrollTop = msgs.scrollHeight;
}

function closeChatBox() {
  clearInterval(chatPollTimer);
  chatPollTimer = null;
  activeThreadId = null;
  activeThreadMeta = null;
  document.getElementById('globalChat')?.remove();
}

function updateMsgBadge() {
  const badge = document.getElementById('msgBadge');
  if (!badge) return;
  const store = getChatStore();
  const unread = Object.values(store.threads || {}).reduce((s, t) => s + (t.unread || 0), 0);
  badge.textContent = unread;
  badge.style.display = unread > 0 ? 'flex' : 'none';
}

function renderNotificationDropdown(items) {
  const dropdown = document.getElementById('notifDropdown');
  if (!dropdown) return;
  if (!items.length) {
    dropdown.innerHTML = `<div style="padding:10px 12px;font-size:13px;color:var(--text-muted)">No new requests</div>`;
    return;
  }
  dropdown.innerHTML = items.map(r => `
    <div style="padding:10px 12px;border-bottom:1px solid var(--border)">
      <div style="font-size:13px;font-weight:700">${r.from_name || r.from_key}</div>
      <div style="font-size:12px;color:var(--text-muted);margin-top:2px">${r.reason || 'Wants to connect'}</div>
      <div style="display:flex;gap:6px;margin-top:8px">
        <button class="btn btn-primary btn-sm" onclick="respondConnectionFromNotif(${r.id},'accept')">Accept</button>
        <button class="btn btn-outline btn-sm" onclick="respondConnectionFromNotif(${r.id},'reject')">Reject</button>
      </div>
    </div>
  `).join('');
}

async function refreshConnectionNotifications() {
  const badge = document.getElementById('notifBadge');
  const meKey = currentUserKey();
  if (!badge || !meKey) return;
  try {
    const res = await fetch(`/api/chat/connections/?me_key=${encodeURIComponent(meKey)}`);
    if (!res.ok) throw new Error('notif fetch failed');
    const data = await res.json();
    const incoming = data.incoming || [];
    badge.textContent = String(incoming.length);
    badge.style.display = incoming.length ? 'flex' : 'none';
    renderNotificationDropdown(incoming);
  } catch (_err) {
    badge.style.display = 'none';
  }
}

async function respondConnectionFromNotif(requestId, action) {
  try {
    const res = await fetch(`/api/chat/connections/${requestId}/respond/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ me_key: currentUserKey(), action }),
    });
    if (!res.ok) throw new Error('respond failed');
    showToast(action === 'accept' ? 'Connection accepted' : 'Connection rejected', action === 'accept' ? 'success' : 'warning');
    await refreshConnectionNotifications();
  } catch (_err) {
    showToast('Could not update request', 'error');
  }
}

function toggleNotifications(event) {
  if (event && typeof event.stopPropagation === 'function') event.stopPropagation();
  const dd = document.getElementById('notifDropdown');
  const btn = document.getElementById('notifBtn');
  if (!dd) return;
  if (btn) {
    const rect = btn.getBoundingClientRect();
    dd.style.position = 'fixed';
    dd.style.top = `${rect.bottom + 8}px`;
    dd.style.right = `${Math.max(window.innerWidth - rect.right, 12)}px`;
  }
  dd.classList.toggle('hidden');
  if (!dd.classList.contains('hidden')) refreshConnectionNotifications();
}

async function openChat(name, initials, subject = '', otherKey = '', bypassConnection = false) {
  const normalizedOther = String(otherKey || name || '').trim().toLowerCase();
  const target = { name, initials, subject, otherKey: normalizedOther, bypassConnection: !!bypassConnection };
  if (bypassConnection) {
    sessionStorage.setItem('chatTarget', JSON.stringify(target));
    window.location.href = 'messages.html';
    return;
  }

  try {
    const req = await requestConnection(name, normalizedOther, subject || 'Want to connect');
    if (req.connected || req.status === 'accepted') {
      sessionStorage.setItem('chatTarget', JSON.stringify(target));
      window.location.href = 'messages.html';
      return;
    }
    showToast(`Connection request sent to ${name}. Chat unlocks after accept.`, 'warning');
    window.location.href = 'messages.html';
  } catch (_err) {
    showToast('Could not send connection request right now.', 'error');
  }
}

async function sendMsg() {
  const input = document.getElementById('chatInput');
  const text = input.value.trim();
  if (!text || !activeThreadId) return;
  input.value = '';
  try {
    await apiSendMessage(activeThreadId, text);
    const latest = await apiFetchMessages(activeThreadId);
    renderMessages({ ...activeThreadMeta, messages: latest });
  } catch {
    const store = getChatStore();
    const thread = store.threads[activeThreadId];
    if (!thread) return;
    thread.messages.push({ sender: 'me', text, ts: Date.now() });
    saveChatStore(store);
    renderMessages(thread);
    setTimeout(() => {
      const replies = ["Sure, let's discuss!", "Sounds good 👍", "I'll get back to you.", "What's your best price?", "Can we meet on campus?"];
      const s2 = getChatStore();
      const t2 = s2.threads[activeThreadId];
      if (!t2) return;
      t2.messages.push({ sender: 'other', text: replies[Math.floor(Math.random() * replies.length)], ts: Date.now() });
      t2.unread = 0;
      saveChatStore(s2);
      renderMessages(t2);
      updateMsgBadge();
    }, 1200);
  }
}

// ── Navbar builder ──────────────────────────────────
function buildNav(activePage) {
  const user = Auth.getUser();
  if (!user) return;
  const initials = (user.name || 'U').split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
  const avatarContent = user.avatar
    ? `<img src="${user.avatar}" alt="${user.name || 'User'}" style="width:100%;height:100%;object-fit:cover;border-radius:50%" />`
    : initials;

  const pages = [
    { id: 'home', label: 'Home', icon: '🏠', href: 'home.html' },
    { id: 'marketplace', label: 'Marketplace', icon: '🛒', href: 'marketplace.html' },
    { id: 'studyhub', label: 'Study Hub', icon: '📚', href: 'studyhub.html' },
    { id: 'hostel', label: 'Hostel Desk', icon: '🏨', href: 'hostel.html' },
  ];

  const navLinks = pages.map(p => `
    <a href="${p.href}" class="nav-link ${activePage === p.id ? 'active' : ''}">
      <span>${p.icon}</span><span>${p.label}</span>
    </a>
  `).join('');

  const navHTML = `
    <nav class="navbar" id="mainNav">
      <div class="nav-brand">Edu<span>Bond</span></div>
      <div class="nav-links">${navLinks}</div>
      <div class="nav-search" style="position:relative">
        <span class="search-icon">🔍</span>
        <input type="text" placeholder="Search people..." id="globalSearch" autocomplete="off" />
        <div class="search-dropdown hidden" id="searchDropdown"></div>
      </div>
      <div class="nav-actions">
        <div id="notifWrap" style="position:relative">
          <button class="nav-icon-btn" id="notifBtn" onclick="toggleNotifications(event)" title="Notifications" style="position:relative">
            🔔
            <span class="msg-count" id="notifBadge" style="position:absolute;top:4px;right:4px;font-size:9px;min-width:16px;height:16px;background:var(--danger);color:#fff;border-radius:99px;display:none;align-items:center;justify-content:center;font-weight:700">0</span>
          </button>
          <div class="hidden" id="notifDropdown" style="position:fixed;right:12px;top:74px;width:300px;max-height:360px;overflow:auto;background:var(--surface);border:1px solid var(--border);border-radius:12px;box-shadow:var(--shadow);z-index:9999;text-align:left"></div>
        </div>
        <button class="nav-icon-btn" onclick="toggleChatList()" title="Messages" style="position:relative">
          💬
          <span class="msg-count" id="msgBadge" style="position:absolute;top:4px;right:4px;font-size:9px;min-width:16px;height:16px;background:var(--danger);color:#fff;border-radius:99px;display:flex;align-items:center;justify-content:center;font-weight:700">3</span>
        </button>
        <a href="profile.html" class="avatar" style="cursor:pointer;overflow:hidden">${avatarContent}</a>
        <button class="btn btn-outline btn-sm" onclick="Auth.logout()">Logout</button>
      </div>
    </nav>
  `;

  document.body.insertAdjacentHTML('afterbegin', navHTML);
  syncCurrentUserFromApi().then(refreshNavbarAvatar);
  initSearch();
  updateMsgBadge();
  refreshConnectionNotifications();
  if (notifPollTimer) clearInterval(notifPollTimer);
  notifPollTimer = setInterval(refreshConnectionNotifications, 8000);
  if (!window.__notifDocClickBound) {
    document.addEventListener('click', (e) => {
      const dd = document.getElementById('notifDropdown');
      if (!dd) return;
      if (!e.target.closest('#notifWrap')) dd.classList.add('hidden');
    });
    window.__notifDocClickBound = true;
  }
}

// ── People data ────────────────────────────────────
const PEOPLE = [
  { name: 'Arjun Sharma', year: '3rd Year', branch: 'CSE', email: 'arjun@indiraicem.ac.in', bio: 'DSA enthusiast and full-stack learner.', skills: ['C++', 'React', 'Problem Solving'] },
  { name: 'Priya Patel', year: '2nd Year', branch: 'ECE', email: 'priya@indiraicem.ac.in', bio: 'Interested in electronics and embedded systems.', skills: ['VLSI', 'Arduino'] },
  { name: 'Rahul Verma', year: '4th Year', branch: 'ME', email: 'rahul@indiraicem.ac.in', bio: 'Final-year mechanical student with internship experience.', skills: ['CAD', 'Thermodynamics'] },
  { name: 'Sneha Joshi', year: '1st Year', branch: 'CSE', email: 'sneha@indiraicem.ac.in', bio: 'Exploring coding, design, and open-source.', skills: ['Python', 'UI Design'] },
  { name: 'Amit Kumar', year: '3rd Year', branch: 'CE', email: 'amit@indiraicem.ac.in', bio: 'Civil engineering student focused on structures.', skills: ['AutoCAD', 'Surveying'] },
  { name: 'Anjali Singh', year: 'Alumni', branch: 'IT', email: 'anjali@indiraicem.ac.in', bio: 'Alumni mentor helping juniors with placement prep.', skills: ['System Design', 'Interviews'] },
  { name: 'Dev Mehta', year: '2nd Year', branch: 'EE', email: 'dev@indiraicem.ac.in', bio: 'Power systems and circuits learner.', skills: ['Network Theory', 'MATLAB'] },
  { name: 'Kavya Nair', year: 'Alumni', branch: 'CSE', email: 'kavya@indiraicem.ac.in', bio: 'Software engineer and campus mentor.', skills: ['Backend', 'Databases'] },
];

function getPerson(ref) {
  const key = String(ref || '').trim().toLowerCase();
  return PEOPLE.find(p => (p.email || '').toLowerCase() === key || (p.name || '').toLowerCase() === key);
}

function initSearch() {
  const input = document.getElementById('globalSearch');
  const dropdown = document.getElementById('searchDropdown');
  if (!input || !dropdown) return;

  input.addEventListener('input', () => {
    const q = input.value.trim().toLowerCase();
    if (!q) { dropdown.classList.add('hidden'); return; }
    const results = PEOPLE.filter(p => p.name.toLowerCase().includes(q) || p.branch.toLowerCase().includes(q));
    if (!results.length) { dropdown.classList.add('hidden'); return; }
    dropdown.innerHTML = results.map(p => {
      const ini = p.name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
      return `<div class="search-item" onclick="viewProfile('${p.email}')">
        <div class="avatar" style="width:32px;height:32px;font-size:12px">${ini}</div>
        <div class="info"><div class="name">${p.name}</div><div class="sub">${p.year} • ${p.branch}</div></div>
      </div>`;
    }).join('');
    dropdown.classList.remove('hidden');
  });

  document.addEventListener('click', e => {
    if (!e.target.closest('.nav-search')) dropdown.classList.add('hidden');
  });
}

function viewProfile(emailOrName) {
  const person = getPerson(emailOrName);
  sessionStorage.setItem('viewProfile', person?.email || emailOrName);
  window.location.href = 'profile.html';
}

function toggleChatList() {
  window.location.href = 'messages.html';
}

// ── Modal helpers ──────────────────────────────────
function openModal(id) { document.getElementById(id)?.classList.remove('hidden'); }
function closeModal(id) { document.getElementById(id)?.classList.add('hidden'); }
