/**
 * Mintuu AI — App Controller (Alpine.js)
 * Handles onboarding, chat, agents, workflows, notifications, and all UI state.
 */
const API_BASE = '';

function mintuu() {
    return {
        // ── Auth State ───────────────────────────
        userName: '',
        userEmail: '',
        userInitials: '',
        theme: 'dark',

        // ── UI State ─────────────────────────────
        currentPage: 'chat',
        prevPage: '',
        sidebarCollapsed: false,
        showWelcome: false,
        welcomeStep: -1,
        showTour: false,
        tourStep: 0,
        spotlightStyle: '',
        tooltipStyle: '',
        isFirstTime: true,
        workflowRunning: false,
        pageTransition: false,
        showUserDropdown: false,
        dataLoaded: false,
        notificationCount: 0,

        // ── Data State ───────────────────────────
        chatMessages: [],
        chatInput: '',
        conversationId: null,
        agents: [],
        workflows: [],
        collabMessages: [],
        autoTasks: [],
        autoRunning: false,
        systemStatusText: 'All systems ready',
        systemStatusColor: 'green',
        systemStatusLabel: 'Online',
        historySearch: '',
        historyData: [],
        selectedHistory: null,
        expandedHistoryId: null,
        uptimeStart: Date.now(),
        uptimeText: '0m',
        systemInfo: {},

        // ── Rotating Placeholder ─────────────────
        placeholders: [
            'Launch a product by Q3 with 500 signups...',
            'Respond to this GitHub incident...',
            'Analyze our competitor pricing strategy...',
            'Run a system health check across all agents...',
            'Build a marketing campaign for $10K budget...',
            'Generate a quarterly financial report...',
        ],
        currentPlaceholder: 0,
        placeholderText: '',

        // ── Tour Steps ───────────────────────────
        tourSteps: [
            { target: '#chat-input-bar', title: 'Talk to Mintuu', description: 'Type any business goal or problem here. Mintuu figures out which of its specialist agents to activate. Try typing: Launch a new product by Q3 with 500 signups.' },
            { target: '#nav-agents, .mobile-nav-item:nth-child(2)', title: 'Your AI Team', description: 'These are Mintuu\'s 9 specialized agents — CEO, Research, Marketing, Finance, Operations, Production, HR, Security, and Infrastructure. Each one handles a different part of your business.' },
            { target: '#nav-workflows, .mobile-nav-item:nth-child(3)', title: 'How Work Gets Done', description: 'When you give Mintuu a goal, it breaks it into steps and assigns each one to the right agent. You can watch the progress here in real time.' },
            { target: '#nav-agents', title: 'Agents Talking to Each Other', description: 'Mintuu\'s agents don\'t just work alone — they pass information to each other, critique each other\'s plans, and hand off results. The collaboration feed shows every conversation.' },
            { target: '#nav-workflows', title: 'Always Working', description: 'Autonomous tasks run automatically on a schedule — health checks, budget reviews, competitor monitoring. All happening in the background without you asking.' },
            { target: '#nav-settings, .mobile-nav-item:nth-child(4)', title: 'Mintuu Remembers Everything', description: 'Every workflow, decision, and incident gets stored in Mintuu\'s organizational memory. The more you use it, the smarter it gets.' },
        ],

        // ── Agent icon/color map ─────────────────
        agentMeta: {
            'CEO Dept':           { icon: `<svg viewBox="0 0 24 24" fill="none" stroke="#7C3AED" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 4l3 12h14l3-12-6 7-4-7-4 7-6-7z"/><path d="M3 20h18v1H3z"/></svg>`, color: '#7C3AED', label: 'Strategy' },
            'Research Dept':      { icon: `<svg viewBox="0 0 24 24" fill="none" stroke="#06B6D4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="6"/><path d="M16 16l5 5"/><circle cx="11" cy="11" r="1.5" fill="#06B6D4"/><path d="M8 11h6M11 8v6"/></svg>`, color: '#06B6D4', label: 'Research' },
            'Marketing Dept':     { icon: `<svg viewBox="0 0 24 24" fill="none" stroke="#EC4899" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 5L6 9H2v6h4l5 4V5z"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>`, color: '#EC4899', label: 'Growth' },
            'Finance Dept':       { icon: `<svg viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>`, color: '#10B981', label: 'Finance' },
            'Operations Dept':    { icon: `<svg viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>`, color: '#F59E0B', label: 'Ops' },
            'Production Dept':    { icon: `<svg viewBox="0 0 24 24" fill="none" stroke="#3B82F6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/><line x1="12" y1="2" x2="12" y2="22"/><polyline points="9 5 12 2 15 5"/></svg>`, color: '#3B82F6', label: 'Build' },
            'HR Dept':            { icon: `<svg viewBox="0 0 24 24" fill="none" stroke="#14B8A6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>`, color: '#14B8A6', label: 'People' },
            'Security Dept':      { icon: `<svg viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><rect x="10" y="11" width="4" height="3" rx="1"/><path d="M11 11V9a1 1 0 0 1 2 0v2"/></svg>`, color: '#EF4444', label: 'Security' },
            'Infrastructure Dept':{ icon: `<svg viewBox="0 0 24 24" fill="none" stroke="#F97316" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="6" rx="2"/><rect x="2" y="10" width="20" height="6" rx="2"/><rect x="2" y="18" width="20" height="6" rx="2"/><line x1="6" y1="5" x2="6" y2="5"/><line x1="6" y1="13" x2="6" y2="13"/><line x1="6" y1="21" x2="6" y2="21"/></svg>`, color: '#F97316', label: 'Infra' },
        },

        getAgentMeta(agentType) {
            return this.agentMeta[agentType] || { icon: `<svg viewBox="0 0 24 24" fill="none" stroke="#7C3AED" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>`, color: '#7C3AED', label: agentType };
        },

        // ── Page titles for breadcrumb ───────────
        pageTitle() {
            const map = { chat: 'Chat', agents: 'Agent Network', workflows: 'Workflows', history: 'History', settings: 'Settings' };
            return map[this.currentPage] || 'Chat';
        },

        // ── Init ─────────────────────────────────
        init() {
            // Check auth
            if (!isLoggedIn()) { window.location.href = '/login'; return; }
            const user = getUser();
            if (user) {
                this.userName = user.full_name || user.email;
                this.userEmail = user.email;
                const parts = (user.full_name || user.email).split(' ');
                this.userInitials = parts.length >= 2 ? (parts[0][0] + parts[parts.length-1][0]).toUpperCase() : parts[0].substring(0,2).toUpperCase();
            }

            // Check onboarding
            const onboarded = user?.onboarding_complete;
            if (!onboarded) {
                this.showWelcome = true;
                this.animateWelcome();
            } else {
                this.isFirstTime = false;
            }

            // Load theme
            const saved = localStorage.getItem('mintuu_theme');
            if (saved) { this.theme = saved; document.documentElement.setAttribute('data-theme', saved); }

            // Rotating placeholder
            this.placeholderText = this.placeholders[0];
            setInterval(() => {
                this.currentPlaceholder = (this.currentPlaceholder + 1) % this.placeholders.length;
                this.placeholderText = this.placeholders[this.currentPlaceholder];
            }, 3000);

            // Uptime timer
            setInterval(() => { this.uptimeText = this.formatUptime(); }, 30000);
            this.uptimeText = this.formatUptime();

            // Close dropdown on outside click
            document.addEventListener('click', (e) => {
                if (!e.target.closest('.user-menu')) this.showUserDropdown = false;
            });

            // Fetch data
            this.fetchState();
            this.connectWebSocket();
            setInterval(() => this.fetchState(), 5000);
        },

        // ── Page Navigation with transition ──────
        navigateTo(page) {
            if (page === this.currentPage) return;
            this.pageTransition = true;
            this.prevPage = this.currentPage;
            setTimeout(() => {
                this.currentPage = page;
                this.pageTransition = false;
                if (page === 'history') this.loadHistory();
            }, 150);
        },

        // ── Welcome Animation ────────────────────
        animateWelcome() {
            setTimeout(() => this.welcomeStep = 0, 300);
            setTimeout(() => this.welcomeStep = 1, 1000);
            setTimeout(() => this.welcomeStep = 2, 3500);
        },
        skipWelcome() { this.showWelcome = false; this.completeOnboarding(); },
        startTour() { this.showWelcome = false; this.showTour = true; this.tourStep = 0; this.$nextTick(() => this.positionTour()); },
        positionTour() {
            const step = this.tourSteps[this.tourStep];
            if (!step) return;
            const el = document.querySelector(step.target);
            if (!el) { this.spotlightStyle = 'display:none'; this.tooltipStyle = 'top:50%;left:50%;transform:translate(-50%,-50%)'; return; }
            const r = el.getBoundingClientRect();
            const pad = 8;
            this.spotlightStyle = `top:${r.top - pad}px;left:${r.left - pad}px;width:${r.width + pad*2}px;height:${r.height + pad*2}px`;
            const below = r.bottom + 16;
            const above = r.top - 220;
            const topPos = (below + 200 < window.innerHeight) ? below : Math.max(16, above);
            const leftPos = Math.min(Math.max(16, r.left), window.innerWidth - 400);
            this.tooltipStyle = `top:${topPos}px;left:${leftPos}px`;
        },
        endTour() { this.showTour = false; this.completeOnboarding(); },
        restartTour() { this.showWelcome = true; this.welcomeStep = -1; this.animateWelcome(); },
        async completeOnboarding() {
            this.isFirstTime = this.chatMessages.length === 0;
            try {
                await authFetch(`${API_BASE}/auth/onboarding/complete`, { method: 'POST' });
                const u = getUser(); if (u) { u.onboarding_complete = true; setUser(u); }
            } catch {}
        },

        // ── Chat ─────────────────────────────────
        prefillChat(text) { this.chatInput = text; this.isFirstTime = false; document.getElementById('chat-input')?.focus(); },
        async sendChat() {
            const msg = this.chatInput.trim();
            if (!msg) return;
            this.chatInput = '';
            this.isFirstTime = false;
            this.chatMessages.push({ type: 'user', text: this.escapeHtml(msg) });
            this.chatMessages.push({ type: 'system', text: '<div class="typing-indicator"><span></span><span></span><span></span></div>' });
            this.systemStatusText = 'Agent reasoning...';
            this.systemStatusColor = 'orange';
            this.systemStatusLabel = 'Thinking';
            this.$nextTick(() => { const el = this.$refs.chatMessages; if (el) el.scrollTop = el.scrollHeight; });

            try {
                const res = await authFetch(`${API_BASE}/api/v1/chat`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: msg, conversation_id: this.conversationId }),
                });
                const data = await res.json();
                this.conversationId = data.conversation_id;
                this.chatMessages.pop(); // remove typing indicator
                this.chatMessages.push({ type: 'system', text: data.response || 'Done.' });
                this.showToast('success', 'Task Complete', msg.slice(0, 60));
                this.notificationCount++;
                this.fetchState();
            } catch (e) {
                this.chatMessages.pop();
                this.chatMessages.push({ type: 'system', text: '❌ Error communicating with ecosystem.' });
                this.showToast('error', 'Error', e.message);
                this.systemStatusText = 'System error';
                this.systemStatusColor = 'red';
                this.systemStatusLabel = 'Error';
            }
        },

        // ── Data Fetching ────────────────────────
        async fetchState() {
            try {
                const [status, collab, auto] = await Promise.all([
                    authFetch(`${API_BASE}/api/v1/status`).then(r => r.json()),
                    authFetch(`${API_BASE}/api/v1/collaboration`).then(r => r.json()).catch(() => null),
                    authFetch(`${API_BASE}/api/v1/autonomous`).then(r => r.json()).catch(() => null),
                ]);
                this.agents = status.agents || [];
                const active = status.active_workflows || [];
                const completed = status.completed_workflows || [];
                this.workflows = [...active, ...completed];
                this.workflowRunning = active.length > 0;
                if (this.workflowRunning) {
                    this.systemStatusText = 'Workflow executing...';
                    this.systemStatusColor = 'cyan';
                    this.systemStatusLabel = 'Executing';
                } else {
                    this.systemStatusText = 'All systems ready';
                    this.systemStatusColor = 'green';
                    this.systemStatusLabel = 'Online';
                }
                if (collab) this.collabMessages = (collab.message_history || []).slice(-30).reverse();
                if (auto) { this.autoTasks = auto.tasks || []; this.autoRunning = auto.is_running; }
                
                // Populate system info for settings
                const eco = status.ecosystem || {};
                const sys = status.system_state || {};
                this.systemInfo = {
                    version: eco.version || '3.0.0',
                    llm_provider: eco.llm_provider || 'Ollama (local)',
                    agents_active: (status.agents || []).length,
                    memory_entries: sys.total_memory_entries || eco.memory_entries || '0',
                    total_workflows: (sys.total_workflows_completed || 0) + (active.length || 0),
                };
                
                this.dataLoaded = true;
            } catch {}
        },

        // ── WebSocket ────────────────────────────
        connectWebSocket() {
            const host = window.location.host || 'localhost:8003';
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            try {
                const ws = new WebSocket(`${protocol}//${host}/ws`);
                ws.onmessage = (e) => {
                    try {
                        const { type, data } = JSON.parse(e.data);
                        if (type === 'state_update') this.fetchState();
                    } catch {}
                };
                ws.onclose = () => setTimeout(() => this.connectWebSocket(), 5000);
            } catch {}
        },

        // ── History ──────────────────────────────
        async loadHistory() {
            try {
                const res = await authFetch(`${API_BASE}/api/v1/workflows`);
                this.historyData = await res.json();
            } catch { this.historyData = []; }
        },
        get filteredHistory() {
            const q = this.historySearch.toLowerCase();
            if (!q) return this.historyData;
            return this.historyData.filter(h => (h.name || '').toLowerCase().includes(q));
        },

        // ── Theme ────────────────────────────────
        toggleTheme() {
            this.theme = this.theme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', this.theme);
            localStorage.setItem('mintuu_theme', this.theme);
            authFetch(`${API_BASE}/auth/me`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ theme_preference: this.theme }) }).catch(() => {});
        },

        // ── Account Actions ──────────────────────
        async exportData() {
            try {
                const res = await authFetch(`${API_BASE}/auth/data/export`);
                const data = await res.json();
                const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a'); a.href = url; a.download = 'mintuu_data_export.json'; a.click();
                this.showToast('success', 'Export Complete', 'Your data has been downloaded.');
            } catch { this.showToast('error', 'Export Failed', 'Could not export data.'); }
        },
        async clearData() {
            try {
                await authFetch(`${API_BASE}/auth/data/clear`, { method: 'POST' });
                this.showToast('success', 'Data Cleared', 'All your data has been wiped.');
            } catch { this.showToast('error', 'Error', 'Could not clear data.'); }
        },
        logout() { clearTokens(); window.location.href = '/'; },

        // ── Toast Notifications ──────────────────
        showToast(type, title, message) {
            const container = document.getElementById('toast-container');
            if (!container) return;
            const toast = document.createElement('div');
            toast.className = `toast ${type}`;
            const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
            toast.innerHTML = `<span class="toast-icon">${icons[type] || 'ℹ️'}</span><div class="toast-content"><div class="toast-title">${title}</div><div class="toast-message">${message}</div></div><button class="toast-close" onclick="this.parentElement.remove()">×</button>`;
            container.appendChild(toast);
            toast.addEventListener('click', () => toast.remove());
            setTimeout(() => { if (toast.parentElement) toast.remove(); }, 5000);
        },

        // ── Helpers ──────────────────────────────
        escapeHtml(t) { const d = document.createElement('div'); d.textContent = t; return d.innerHTML; },
        formatTime(iso) { try { return new Date(iso).toLocaleTimeString('en', { hour: '2-digit', minute: '2-digit' }); } catch { return ''; } },
        formatDate(iso) { try { return new Date(iso).toLocaleDateString('en', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }); } catch { return ''; } },
        formatInterval(s) { if (s < 60) return s + 's'; if (s < 3600) return Math.round(s/60) + 'm'; return Math.round(s/3600) + 'h'; },
        formatUptime() {
            const ms = Date.now() - this.uptimeStart;
            const mins = Math.floor(ms / 60000);
            if (mins < 60) return mins + 'm';
            const hrs = Math.floor(mins / 60);
            return hrs + 'h ' + (mins % 60) + 'm';
        },
        getWorkflowType(wf) {
            const name = (wf.name || '').toLowerCase();
            if (name.includes('github') || name.includes('incident') || name.includes('issue')) return 'GitHub Incident';
            if (name.includes('launch') || name.includes('product') || name.includes('strategic')) return 'Strategic Launch';
            if (name.includes('competitor') || name.includes('analysis')) return 'Competitor Watch';
            if (name.includes('security') || name.includes('audit') || name.includes('infrastructure')) return 'Security Audit';
            if (name.includes('budget') || name.includes('finance') || name.includes('burn')) return 'Budget Review';
            if (name.includes('health') || name.includes('check') || name.includes('system')) return 'Health Check';
            return 'General Task';
        },
        getWorkflowDuration(wf) {
            if (!wf.started_at || !wf.completed_at) return 'N/A';
            const start = new Date(wf.started_at);
            const end = new Date(wf.completed_at);
            const diff = Math.max(0, end - start);
            const secs = Math.round(diff / 1000);
            if (secs < 60) return secs + 's';
            return Math.round(secs / 60) + 'm';
        },
        getAgentCount(wf) {
            if (!wf.steps) return 0;
            const agents = new Set(wf.steps.map(s => s.agent_type));
            return agents.size;
        },

        // ── Time Ago Helper ──────────────────────
        formatTimeAgo(iso) {
            try {
                const d = new Date(iso);
                const diff = (Date.now() - d.getTime()) / 1000;
                if (diff < 10) return 'just now';
                if (diff < 60) return `${Math.round(diff)}s ago`;
                if (diff < 3600) return `${Math.floor(diff/60)}m ago`;
                if (diff < 86400) return `${Math.floor(diff/3600)}h ago`;
                return `${Math.floor(diff/86400)}d ago`;
            } catch { return 'just now'; }
        },

        // ── Trigger Autonomous Task ───────────────
        async triggerTask(taskId) {
            try {
                await authFetch(`${API_BASE}/api/v1/autonomous/${taskId}/trigger`, { method: 'POST' });
                this.showToast('success', 'Task Triggered', `Autonomous task ${taskId} triggered.`);
                this.fetchState();
            } catch (e) {
                this.showToast('error', 'Trigger Failed', e.message || 'Could not trigger task.');
            }
        },
    };
}
