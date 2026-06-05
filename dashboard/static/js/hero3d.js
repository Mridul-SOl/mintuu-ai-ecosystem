/**
 * Mintuu AI — Hero 3D Particle Network
 * Three.js scene: floating nodes (agents) connected by pulsing edges.
 * Responds to mouse movement with parallax tilt. Auto-degrades on mobile.
 * Self-contained module — initialized by landing page.
 */
(function () {
    'use strict';

    const PARTICLE_COUNT_DESKTOP = 60;
    const PARTICLE_COUNT_MOBILE = 0; // 2D fallback used instead
    const EDGE_DISTANCE = 3.2;
    const COLORS = {
        purple: 0x7C3AED,
        cyan: 0x06B6D4,
        white: 0xF8FAFC,
        dimPurple: 0x4C1D95,
    };

    let scene, camera, renderer, particles, edges, clock;
    let mouseX = 0, mouseY = 0;
    let targetRotX = 0, targetRotY = 0;
    let animFrameId = null;
    let frameCount = 0, lastFpsCheck = 0, currentFps = 60;
    let particleCount = PARTICLE_COUNT_DESKTOP;
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function isMobile() { return window.innerWidth < 768; }

    function init(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        if (isMobile() || reducedMotion) {
            // 2D SVG fallback — no Three.js
            container.innerHTML = buildSVGFallback();
            return;
        }

        // Dynamic Three.js import
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js';
        script.async = true;
        script.onload = () => initScene(container);
        document.head.appendChild(script);
    }

    function initScene(container) {
        const W = container.clientWidth;
        const H = container.clientHeight;

        scene = new THREE.Scene();
        camera = new THREE.PerspectiveCamera(60, W / H, 0.1, 100);
        camera.position.z = 8;

        renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(W, H);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.setClearColor(0x000000, 0);
        container.appendChild(renderer.domElement);

        clock = new THREE.Clock();
        createParticles();
        createEdges();

        // Mouse parallax
        document.addEventListener('mousemove', onMouseMove, { passive: true });
        window.addEventListener('resize', () => onResize(container), { passive: true });

        lastFpsCheck = performance.now();
        animate();
    }

    function createParticles() {
        particles = [];
        const group = new THREE.Group();
        group.name = 'particles';
        scene.add(group);

        const geo = new THREE.SphereGeometry(0.06, 12, 12);
        const glowGeo = new THREE.SphereGeometry(0.15, 12, 12);

        for (let i = 0; i < particleCount; i++) {
            const isPrimary = i < 9; // First 9 = agent nodes (larger)
            const size = isPrimary ? 0.1 : 0.04;
            const color = isPrimary
                ? (i % 2 === 0 ? COLORS.purple : COLORS.cyan)
                : COLORS.white;

            const mat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: isPrimary ? 1 : 0.4 });
            const mesh = new THREE.Mesh(
                isPrimary ? new THREE.SphereGeometry(size, 16, 16) : geo,
                mat
            );

            // Random position in a sphere
            const r = 3 + Math.random() * 2;
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.acos(2 * Math.random() - 1);
            mesh.position.set(
                r * Math.sin(phi) * Math.cos(theta),
                r * Math.sin(phi) * Math.sin(theta),
                r * Math.cos(phi)
            );

            // Glow for primary nodes
            if (isPrimary) {
                const glowMat = new THREE.MeshBasicMaterial({
                    color, transparent: true, opacity: 0.12
                });
                const glow = new THREE.Mesh(new THREE.SphereGeometry(0.25, 12, 12), glowMat);
                mesh.add(glow);
            }

            // Store velocity for orbital motion
            mesh.userData = {
                orbitSpeed: 0.1 + Math.random() * 0.15,
                orbitOffset: Math.random() * Math.PI * 2,
                baseY: mesh.position.y,
                floatSpeed: 0.3 + Math.random() * 0.5,
                floatAmp: 0.1 + Math.random() * 0.2,
                isPrimary,
            };

            group.add(mesh);
            particles.push(mesh);
        }
    }

    function createEdges() {
        edges = [];
        const edgeGroup = new THREE.Group();
        edgeGroup.name = 'edges';
        scene.add(edgeGroup);

        // Connect nearby particles
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const d = particles[i].position.distanceTo(particles[j].position);
                if (d < EDGE_DISTANCE) {
                    const geom = new THREE.BufferGeometry().setFromPoints([
                        particles[i].position.clone(),
                        particles[j].position.clone()
                    ]);
                    const mat = new THREE.LineBasicMaterial({
                        color: COLORS.purple,
                        transparent: true,
                        opacity: 0.08,
                    });
                    const line = new THREE.Line(geom, mat);
                    line.userData = { i, j, baseOpacity: 0.08, pulsePhase: Math.random() * Math.PI * 2 };
                    edgeGroup.add(line);
                    edges.push(line);
                }
            }
        }
    }

    function animate() {
        animFrameId = requestAnimationFrame(animate);
        const t = clock.getElapsedTime();

        // FPS monitoring — degrade if needed
        frameCount++;
        const now = performance.now();
        if (now - lastFpsCheck > 1000) {
            currentFps = frameCount;
            frameCount = 0;
            lastFpsCheck = now;
            if (currentFps < 45 && particleCount > 30) {
                // Reduce particles
                degradeScene();
            }
        }

        // Rotate particles group slowly
        const pGroup = scene.getObjectByName('particles');
        if (pGroup) {
            pGroup.rotation.y = t * 0.05;
            pGroup.rotation.x = Math.sin(t * 0.03) * 0.1;
        }

        // Float individual particles
        particles.forEach(p => {
            const ud = p.userData;
            p.position.y = ud.baseY + Math.sin(t * ud.floatSpeed + ud.orbitOffset) * ud.floatAmp;
        });

        // Pulse edges
        edges.forEach(edge => {
            const ud = edge.userData;
            const pulse = 0.5 + 0.5 * Math.sin(t * 1.5 + ud.pulsePhase);
            edge.material.opacity = ud.baseOpacity + pulse * 0.06;

            // Update positions
            const positions = edge.geometry.attributes.position.array;
            const pi = particles[ud.i].position;
            const pj = particles[ud.j].position;
            // Transform to world coords
            const worldI = new THREE.Vector3();
            const worldJ = new THREE.Vector3();
            particles[ud.i].getWorldPosition(worldI);
            particles[ud.j].getWorldPosition(worldJ);
            positions[0] = worldI.x; positions[1] = worldI.y; positions[2] = worldI.z;
            positions[3] = worldJ.x; positions[4] = worldJ.y; positions[5] = worldJ.z;
            edge.geometry.attributes.position.needsUpdate = true;
        });

        // Mouse parallax tilt
        targetRotX = mouseY * 0.15;
        targetRotY = mouseX * 0.15;
        camera.rotation.x += (targetRotX - camera.rotation.x) * 0.03;
        camera.rotation.y += (targetRotY - camera.rotation.y) * 0.03;

        renderer.render(scene, camera);
    }

    function degradeScene() {
        // Remove non-primary particles to maintain FPS
        const pGroup = scene.getObjectByName('particles');
        const toRemove = [];
        particles.forEach((p, idx) => {
            if (!p.userData.isPrimary && idx > 30) toRemove.push(idx);
        });
        toRemove.reverse().forEach(idx => {
            pGroup.remove(particles[idx]);
            particles.splice(idx, 1);
        });
        particleCount = particles.length;
    }

    function onMouseMove(e) {
        mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
        mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
    }

    function onResize(container) {
        if (!renderer || !camera) return;
        const W = container.clientWidth;
        const H = container.clientHeight;
        camera.aspect = W / H;
        camera.updateProjectionMatrix();
        renderer.setSize(W, H);
    }

    function buildSVGFallback() {
        // Animated 2D particle network for mobile / reduced-motion
        let circles = '';
        let lines = '';
        const nodes = [];
        for (let i = 0; i < 15; i++) {
            const x = 10 + Math.random() * 80;
            const y = 10 + Math.random() * 80;
            const r = i < 5 ? 3 : 1.5;
            const color = i < 5 ? (i % 2 === 0 ? '#7C3AED' : '#06B6D4') : '#475569';
            const opacity = i < 5 ? 0.8 : 0.3;
            const dur = 6 + Math.random() * 8;
            const anim = reducedMotion ? '' : `<animateTransform attributeName="transform" type="translate" values="0,0;${(Math.random()-0.5)*4},${(Math.random()-0.5)*4};0,0" dur="${dur}s" repeatCount="indefinite"/>`;
            circles += `<circle cx="${x}%" cy="${y}%" r="${r}" fill="${color}" opacity="${opacity}">${anim}</circle>`;
            nodes.push({ x, y });
        }
        // Connect close nodes
        for (let i = 0; i < nodes.length; i++) {
            for (let j = i + 1; j < nodes.length; j++) {
                const dx = nodes[i].x - nodes[j].x;
                const dy = nodes[i].y - nodes[j].y;
                if (Math.sqrt(dx * dx + dy * dy) < 30) {
                    const pulseAnim = reducedMotion ? '' : `<animate attributeName="opacity" values="0.05;0.15;0.05" dur="${4+Math.random()*4}s" repeatCount="indefinite"/>`;
                    lines += `<line x1="${nodes[i].x}%" y1="${nodes[i].y}%" x2="${nodes[j].x}%" y2="${nodes[j].y}%" stroke="#7C3AED" stroke-width="0.5" opacity="0.08">${pulseAnim}</line>`;
                }
            }
        }
        return `<svg width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="none" style="position:absolute;inset:0;pointer-events:none">${lines}${circles}</svg>`;
    }

    function destroy() {
        if (animFrameId) cancelAnimationFrame(animFrameId);
        if (renderer) renderer.dispose();
        document.removeEventListener('mousemove', onMouseMove);
    }

    // Expose
    window.MintHero3D = { init, destroy };
})();
