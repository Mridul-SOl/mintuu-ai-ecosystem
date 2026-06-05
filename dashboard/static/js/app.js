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
        uptimeStart: Date.now(),
        uptimeText: '0m',

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
            'CEO Dept':           { icon: '👑', color: '#7C3AED', label: 'Strategy' },
            'Research Dept':      { icon: '🔬', color: '#06B6D4', label: 'Research' },
            'Marketing Dept':     { icon: '📣', color: '#EC4899', label: 'Growth' },
            'Finance Dept':       { icon: '📊', color: '#10B981', label: 'Finance' },
            'Operations Dept':    { icon: '⚙️', color: '#F59E0B', label: 'Ops' },
            'Production Dept':    { icon: '🏭', color: '#8B5CF6', label: 'Build' },
            'HR Dept':            { icon: '🧑‍💼', color: '#14B8A6', label: 'People' },
            'Security Dept':      { icon: '🛡️', color: '#EF4444', label: 'Security' },
            'Infrastructure Dept':{ icon: '🌐', color: '#3B82F6', label: 'Infra' },
        },

        getAgentMeta(agentType) {
            return this.agentMeta[agentType] || { icon: '🤖', color: '#7C3AED', label: agentType };
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
            }, 4000);

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
            this.systemStatusColor = 'purple';
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
    };
}
