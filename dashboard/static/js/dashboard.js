/**
 * Mintuu AI Ecosystem v2 — Dashboard Controller
 * Real-time polling with collaboration feed, workflow graph,
 * autonomous status, and inter-agent communication rendering.
 */

const API_BASE = '';
const POLL_INTERVAL = 3000;  // 3s for real-time feel
let conversationId = null;
let lastCollabCount = 0;
let lastWorkflowCount = 0;
let lastAutoEvents = 0;
const reasoningStore = {}; // agent_type -> thought_process

// ── Init ────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    initChat();
    initLogs();
    initWebSocket();
    fetchInitialState();
});

let ws;
let reconnectAttempts = 0;

function initWebSocket() {
    // If not running on a real server yet, default to localhost:8000
    const host = window.location.host || 'localhost:8000';
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${host}/ws`;
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        console.log("WebSocket connected");
        reconnectAttempts = 0;
        const healthEl = byId('system-health');
        if(healthEl) {
            healthEl.textContent = 'SYSTEM ONLINE (WS)';
            healthEl.style.color = '#10b981';
        }
    };
    
    ws.onmessage = (event) => {
        try {
            const payload = JSON.parse(event.data);
            handleWebSocketEvent(payload);
        } catch (e) {
            console.error("Failed to parse WS message", e);
        }
    };
    
    ws.onclose = () => {
        console.warn("WebSocket disconnected. Reconnecting...");
        const healthEl = byId('system-health');
        if(healthEl) {
            healthEl.textContent = 'SYSTEM OFFLINE (RECONNECTING)';
            healthEl.style.color = '#ef4444';
        }
        
        const timeout = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
        setTimeout(initWebSocket, timeout);
        reconnectAttempts++;
    };
    
    ws.onerror = (err) => {
        console.error("WebSocket error:", err);
    };
}

function handleWebSocketEvent(payload) {
    const { type, data } = payload;
    
    if (type === 'state_update') {
        updateStats(data);
        updateAgents(data.agents || []);
        updateWorkflows(data);
    } else if (type === 'collaboration_update') {
        updateCollaboration(data);
    } else if (type === 'autonomous_update') {
        updateAutonomous(data);
    } else if (type === 'log_event') {
        addLog(data.level || 'info', data.message);
    }
    
    // Check for reasoning trace in status updates
    if (type === 'state_update' || type === 'status_update') {
        const ev = data.event || '';
        if (ev === 'reasoning_trace' && data.thought_process) {
            reasoningStore[data.agent] = data.thought_process;
            // if currently viewing this agent, update UI
            const badge = byId('reasoning-agent-badge');
            if (badge && badge.textContent === data.agent) {
                showReasoning(data.agent);
            }
        }
    }
}

function showReasoning(agentType) {
    byId('reasoning-agent-badge').textContent = agentType;
    const stream = byId('reasoning-stream');
    const thought = reasoningStore[agentType];
    if (thought) {
        stream.innerHTML = `<div class="reasoning-content" style="padding: 15px; border-left: 3px solid #a78bfa; background: rgba(255,255,255,0.05); margin-top:10px;">${escapeHtml(thought)}</div>`;
    } else {
        stream.innerHTML = `<div class="empty-state"><p>No reasoning captured yet for ${agentType}...</p></div>`;
    }
}

// ── Initial Fetch ───────────────────────────────────────────
async function fetchInitialState() {
    try {
        const [status, collabResp, autoResp] = await Promise.all([
            fetch(`${API_BASE}/api/v1/status`).then(r => r.json()),
            fetch(`${API_BASE}/api/v1/collaboration`).then(r => r.json()).catch(() => null),
            fetch(`${API_BASE}/api/v1/autonomous`).then(r => r.json()).catch(() => null),
        ]);
        updateStats(status);
        updateAgents(status.agents || []);
        updateWorkflows(status);
        if (collabResp) updateCollaboration(collabResp);
        if (autoResp) updateAutonomous(autoResp);
    } catch (e) {
        console.warn('Initial fetch failed:', e);
    }
}

// ── Stats ───────────────────────────────────────────────
function updateStats(data) {
    const eco = data.ecosystem || {};
    const sys = data.system_state || {};
    const collab = data.collaboration || {};
    const tools = data.tools || {};

    byId('uptime').textContent = formatUptime(eco.uptime_seconds || 0);
    byId('version').textContent = eco.version || '2.0';
    byId('total-agents').textContent = sys.total_agents || 0;
    byId('tasks-completed').textContent = sys.total_tasks_completed || 0;
    byId('total-tools').textContent = tools.tools_available || 0;
    byId('total-collabs').textContent = collab.total_collaborations || 0;

    const wfCompleted = sys.total_workflows_completed || 0;
    const wfActive = (data.active_workflows || []).length;
    byId('total-workflows').textContent = wfCompleted + wfActive;

    byId('system-health').textContent = sys.system_health === 'HEALTHY' ? 'SYSTEM ONLINE' : sys.system_health;
}

// ── Agents ──────────────────────────────────────────────
function updateAgents(agents) {
    const grid = byId('agents-grid');
    byId('agent-count-badge').textContent = `${agents.length} agents`;

    const emojiMap = { CEO: '👔', HR: '👥', Marketing: '📣', Finance: '💰', Production: '🚀', Operations: '⚙️', Research: '🔍' };

    grid.innerHTML = agents.map(a => {
        const st = a.state || {};
        const status = st.status || 'IDLE';
        const dotClass = status === 'EXECUTING' ? 'executing' : status === 'IDLE' ? 'idle' : status === 'OFFLINE' ? 'offline' : '';
        const emoji = emojiMap[a.agent_type] || '🤖';
        const isActive = ['EXECUTING', 'PLANNING', 'COMMUNICATING'].includes(status);
        return `
        <div class="agent-card ${isActive ? 'active' : ''}" onclick="showReasoning('${a.agent_type}')" style="cursor: pointer;">
            <div class="agent-card-header">
                <span class="agent-dot ${dotClass}"></span>
                <span class="agent-card-name">${emoji} ${a.name}</span>
            </div>
            <div class="agent-card-type">${a.agent_type} Dept</div>
            <div class="agent-card-stats">
                <span class="agent-stat">✅ <span class="num">${st.tasks_completed || 0}</span></span>
                <span class="agent-stat">❌ <span class="num">${st.tasks_failed || 0}</span></span>
                <span class="agent-stat">${status}</span>
            </div>
        </div>`;
    }).join('');
}

// ── Workflows ───────────────────────────────────────────
function updateWorkflows(data) {
    const list = byId('workflow-list');
    const active = data.active_workflows || [];
    const completed = data.completed_workflows || [];
    const all = [...active, ...completed];

    byId('workflow-count-badge').textContent = `${all.length} runs`;

    if (all.length === 0) {
        list.innerHTML = '<div class="empty-state"><span class="empty-icon">⚡</span><p>Send a complex request to trigger workflows.</p></div>';
        return;
    }

    list.innerHTML = all.map(wf => {
        const steps = wf.steps || [];
        const collabs = wf.collaboration_log || [];
        const statusClass = (wf.status || 'pending').toLowerCase();

        const stepDots = steps.map(s => {
            const st = (s.state || s.status || 'PENDING').toUpperCase();
            const cls = st === 'COMPLETED' ? 'done' : st === 'FAILED' ? 'fail' : st === 'RUNNING' ? 'active' : '';
            return `<span class="workflow-step-dot ${cls}" title="${s.agent_type}: ${st}">${s.index + 1}</span>`;
        }).join('');

        const collabLine = collabs.length > 0
            ? `<div class="workflow-collab-count">🤝 ${collabs.length} collaborations</div>` : '';

        return `
        <div class="workflow-item">
            <div class="workflow-item-header">
                <span class="workflow-item-name">${wf.name || 'Workflow'}</span>
                <span class="workflow-status ${statusClass}">${wf.status}</span>
            </div>
            <div class="workflow-steps">${stepDots}</div>
            ${collabLine}
        </div>`;
    }).join('');

    // Update Live Workflow Graph & Timeline with the most recent active or completed workflow
    const activeWf = active.length > 0 ? active[0] : (completed.length > 0 ? completed[0] : null);
    if (activeWf) {
        renderWorkflowGraphAndTimeline(activeWf);
    }
}

function renderWorkflowGraphAndTimeline(wf) {
    const graphContainer = byId('workflow-graph-container');
    const timelineContainer = byId('execution-timeline');
    
    if (!graphContainer || !timelineContainer) return;

    const steps = wf.steps || [];
    if (steps.length === 0) return;

    // Render Graph (Nodes + Edges)
    let graphHtml = '<div style="display: flex; align-items: center; justify-content: flex-start; gap: 15px; padding: 20px; overflow-x: auto;">';
    steps.forEach((s, i) => {
        const st = (s.state || s.status || 'PENDING').toUpperCase();
        let color = '#64748b'; // gray
        let shadow = 'none';
        if (st === 'COMPLETED') color = '#34d399'; // green
        else if (st === 'RUNNING' || st === 'EXECUTING') { color = '#a78bfa'; shadow = '0 0 10px #a78bfa'; } // purple
        else if (st === 'FAILED') color = '#ef4444'; // red

        graphHtml += `
            <div style="min-width: 120px; padding: 10px; border: 2px solid ${color}; border-radius: 8px; box-shadow: ${shadow}; background: rgba(0,0,0,0.5); text-align: center;">
                <div style="font-size: 12px; color: #94a3b8; margin-bottom: 5px;">Step ${i+1}</div>
                <div style="font-weight: bold; color: ${color};">${s.agent_type}</div>
            </div>
        `;
        if (i < steps.length - 1) {
            graphHtml += `
            <div style="color: ${color}; font-weight: bold; font-size: 20px;">→</div>
            `;
        }
    });
    graphHtml += '</div>';
    graphContainer.innerHTML = graphHtml;

    // Render Timeline
    let timelineHtml = '<div style="display: flex; flex-direction: column; gap: 8px; padding: 10px;">';
    
    // Find max duration to scale the bars properly (assuming total duration is sum, but let's just make max 100%)
    let maxDur = 0;
    steps.forEach(s => { if(s.duration_ms > maxDur) maxDur = s.duration_ms; });
    if (maxDur === 0) maxDur = 1000; // prevent div by zero

    steps.forEach((s, i) => {
        const durMs = s.duration_ms || 0;
        const durSec = (durMs / 1000).toFixed(1);
        let width = Math.max((durMs / maxDur) * 100, 5); // min 5% width
        if (width > 100) width = 100;
        
        const st = (s.state || s.status || 'PENDING').toUpperCase();
        let color = '#64748b'; // gray
        if (st === 'COMPLETED') color = '#34d399'; // green
        else if (st === 'RUNNING' || st === 'EXECUTING') color = '#a78bfa'; // purple
        else if (st === 'FAILED') color = '#ef4444'; // red

        timelineHtml += `
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 100px; text-align: right; font-size: 12px; color: #94a3b8;">${s.agent_type}</div>
                <div style="flex: 1; background: rgba(255,255,255,0.1); border-radius: 4px; height: 16px; overflow: hidden; position: relative;">
                    <div style="width: ${width}%; background: ${color}; height: 100%; transition: width 0.3s ease;"></div>
                </div>
                <div style="width: 50px; font-size: 12px; color: #94a3b8;">${durSec}s</div>
            </div>
        `;
    });
    timelineHtml += '</div>';
    timelineContainer.innerHTML = timelineHtml;
}

// ── Collaboration Feed ──────────────────────────────────
function updateCollaboration(data) {
    const feed = byId('collab-feed');
    const msgs = data.message_history || [];
    const stats = data.stats || {};

    byId('collab-count-badge').textContent = `${stats.total_collaborations || 0} total`;

    if (msgs.length === 0) {
        feed.innerHTML = '<div class="empty-state"><span class="empty-icon">🤝</span><p>Collaboration feed — run a workflow to see agents communicate.</p></div>';
        return;
    }

    // Only update if changed
    if (msgs.length === lastCollabCount) return;
    lastCollabCount = msgs.length;

    feed.innerHTML = msgs.slice(-30).reverse().map(m => {
        const type = (m.message_type || '').toLowerCase();
        let cls = '';
        if (type.includes('data') || type.includes('status')) cls = 'handoff';
        else if (type.includes('approval')) cls = 'approval';
        else if (type.includes('broadcast')) cls = 'broadcast';

        const time = m.timestamp ? formatTime(m.timestamp) : '';
        const sender = (m.sender || '').replace('agent-', '').toUpperCase();
        const receiver = (m.receiver || '*').replace('agent-', '').toUpperCase();
        const content = m.content || {};
        const summary = content.update || content.event || content.type || type;

        return `
        <div class="collab-item ${cls}">
            <span class="collab-time">${time}</span>
            <span class="collab-arrow">${sender} → ${receiver}</span>
            <span class="collab-text">${summary}</span>
        </div>`;
    }).join('');
}

// ── Autonomous Engine ───────────────────────────────────
function updateAutonomous(data) {
    const container = byId('auto-tasks');
    const tasks = data.tasks || [];
    const isRunning = data.is_running;

    byId('auto-status-badge').textContent = isRunning ? 'Running' : 'Stopped';

    container.innerHTML = tasks.map(t => {
        const dotClass = t.is_active ? '' : 'paused';
        const timeAgo = t.last_run ? formatTimeAgo(t.last_run) : 'never';
        return `
        <div class="auto-task">
            <div class="auto-task-info">
                <span class="auto-task-name"><span class="auto-dot ${dotClass}"></span>${t.name}</span>
                <span class="auto-task-agent">${t.agent_type} Agent • Every ${formatInterval(t.interval_seconds)}</span>
            </div>
            <div class="auto-task-meta">
                <span class="auto-task-runs">${t.run_count} runs</span>
                <span class="auto-task-next">Last: ${timeAgo}</span>
            </div>
        </div>`;
    }).join('');
}

// ── Chat ────────────────────────────────────────────────
function initChat() {
    const input = byId('chat-input');
    const send = byId('chat-send');
    send.addEventListener('click', sendMessage);
    input.addEventListener('keydown', e => { if (e.key === 'Enter') sendMessage(); });
}

async function sendMessage() {
    const input = byId('chat-input');
    const msg = input.value.trim();
    if (!msg) return;
    input.value = '';

    appendChat('user', msg);
    appendChat('system', 'Processing...', true);

    try {
        const res = await fetch(`${API_BASE}/api/v1/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: msg, conversation_id: conversationId }),
        });
        const data = await res.json();
        conversationId = data.conversation_id;
        removeTypingIndicator();
        appendChat('system', data.response || 'Done.');
        addLog('success', `Chat: ${msg.slice(0, 50)}...`);
        fetchInitialState();  // Refresh state
    } catch (e) {
        removeTypingIndicator();
        appendChat('system', '❌ Error communicating with ecosystem.');
        addLog('error', `Chat error: ${e.message}`);
    }
}

function appendChat(type, text, isTyping = false) {
    const container = byId('chat-messages');
    const div = document.createElement('div');
    div.className = `chat-msg ${type}`;
    if (isTyping) div.id = 'typing-indicator';

    const avatar = type === 'user' ? '👤' : '🤖';
    const name = type === 'user' ? 'You' : 'Mintuu';
    div.innerHTML = `
        <div class="chat-avatar">${avatar}</div>
        <div class="chat-bubble">
            <strong>${name}</strong>
            <p>${escapeHtml(text)}</p>
        </div>`;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function removeTypingIndicator() {
    const el = byId('typing-indicator');
    if (el) el.remove();
}

// ── Logs ────────────────────────────────────────────────
function initLogs() {
    byId('clear-logs-btn').addEventListener('click', () => {
        byId('logs-list').innerHTML = '<div class="log-entry info"><span class="log-time">Now</span><span class="log-text">Logs cleared.</span></div>';
    });
}

function addLog(type, text) {
    const list = byId('logs-list');
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    const time = new Date().toLocaleTimeString('en', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    entry.innerHTML = `<span class="log-time">${time}</span><span class="log-text">${escapeHtml(text)}</span>`;
    list.prepend(entry);
    // Keep max 100 entries
    while (list.children.length > 100) list.removeChild(list.lastChild);
}

// ── Helpers ─────────────────────────────────────────────
function byId(id) { return document.getElementById(id); }

function escapeHtml(t) {
    const div = document.createElement('div');
    div.textContent = t;
    return div.innerHTML;
}

function formatUptime(s) {
    if (s < 60) return `${Math.round(s)}s`;
    if (s < 3600) return `${Math.floor(s/60)}m ${Math.round(s%60)}s`;
    return `${Math.floor(s/3600)}h ${Math.floor((s%3600)/60)}m`;
}

function formatTime(iso) {
    try {
        const d = new Date(iso);
        return d.toLocaleTimeString('en', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch { return ''; }
}

function formatTimeAgo(iso) {
    try {
        const d = new Date(iso);
        const diff = (Date.now() - d.getTime()) / 1000;
        if (diff < 60) return `${Math.round(diff)}s ago`;
        if (diff < 3600) return `${Math.floor(diff/60)}m ago`;
        return `${Math.floor(diff/3600)}h ago`;
    } catch { return 'unknown'; }
}

function formatInterval(s) {
    if (s < 60) return `${s}s`;
    if (s < 3600) return `${Math.round(s/60)}m`;
    return `${Math.round(s/3600)}h`;
}
