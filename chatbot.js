// Fieldwise — Smart Construction Chatbot
// Drop this script into any page to activate the floating chat widget

(function() {
    // ── Styles ──────────────────────────────────────────────────────────────
    const style = document.createElement('style');
    style.textContent = `
        :root {
            --fw-bg: #0a0c0f;
            --fw-surface: #111418;
            --fw-surface2: #181d24;
            --fw-border: #1e2530;
            --fw-accent: #f0a500;
            --fw-text: #e8eaed;
            --fw-muted: #6b7280;
            --fw-green: #22c55e;
            --fw-red: #ef4444;
        }

        /* Floating Button */
        #fw-chat-btn {
            position: fixed;
            bottom: 28px;
            right: 28px;
            z-index: 9999;
            width: 56px;
            height: 56px;
            background: var(--fw-accent);
            border: none;
            cursor: pointer;
            clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 4px 24px rgba(240,165,0,0.4);
        }

        #fw-chat-btn:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 32px rgba(240,165,0,0.6);
        }

        #fw-chat-btn.open {
            clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
            background: var(--fw-surface2);
            box-shadow: none;
        }

        /* Notification dot */
        #fw-chat-dot {
            position: fixed;
            bottom: 72px;
            right: 24px;
            z-index: 10000;
            width: 10px;
            height: 10px;
            background: var(--fw-green);
            border-radius: 50%;
            border: 2px solid var(--fw-bg);
            animation: fw-pulse 2s infinite;
        }

        @keyframes fw-pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.6; transform: scale(0.8); }
        }

        /* Chat Drawer */
        #fw-chat-drawer {
            position: fixed;
            bottom: 0;
            right: 0;
            z-index: 9998;
            width: 420px;
            height: 620px;
            max-height: 85vh;
            background: var(--fw-bg);
            border: 1px solid var(--fw-border);
            border-bottom: none;
            border-radius: 12px 12px 0 0;
            display: flex;
            flex-direction: column;
            transform: translateY(100%);
            transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            overflow: hidden;
            box-shadow: 0 -20px 60px rgba(0,0,0,0.6);
        }

        #fw-chat-drawer.open {
            transform: translateY(0);
        }

        @media (max-width: 480px) {
            #fw-chat-drawer {
                width: 100%;
                height: 80vh;
                border-radius: 16px 16px 0 0;
                border-left: none;
                border-right: none;
            }
            #fw-chat-btn {
                bottom: 20px;
                right: 20px;
            }
        }

        /* Header */
        .fw-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 16px 20px;
            border-bottom: 1px solid var(--fw-border);
            background: var(--fw-surface);
            flex-shrink: 0;
        }

        .fw-header-left {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .fw-header-icon {
            width: 32px;
            height: 32px;
            background: var(--fw-accent);
            clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
            flex-shrink: 0;
        }

        .fw-header-title {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 18px;
            letter-spacing: 1px;
            color: var(--fw-text);
        }

        .fw-header-sub {
            font-size: 11px;
            color: var(--fw-green);
            font-family: 'DM Mono', monospace;
            letter-spacing: 1px;
        }

        .fw-close-btn {
            background: none;
            border: none;
            color: var(--fw-muted);
            font-size: 20px;
            cursor: pointer;
            padding: 4px;
            transition: color 0.2s;
        }

        .fw-close-btn:hover { color: var(--fw-text); }

        /* Suggested prompts */
        .fw-suggestions {
            display: flex;
            gap: 6px;
            padding: 10px 16px;
            overflow-x: auto;
            flex-shrink: 0;
            border-bottom: 1px solid var(--fw-border);
            scrollbar-width: none;
        }

        .fw-suggestions::-webkit-scrollbar { display: none; }

        .fw-chip {
            white-space: nowrap;
            font-size: 11px;
            padding: 5px 10px;
            background: var(--fw-surface2);
            border: 1px solid var(--fw-border);
            border-radius: 20px;
            color: var(--fw-muted);
            cursor: pointer;
            transition: all 0.2s;
            font-family: 'DM Sans', sans-serif;
            flex-shrink: 0;
        }

        .fw-chip:hover {
            border-color: var(--fw-accent);
            color: var(--fw-accent);
        }

        /* Messages */
        .fw-messages {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            scrollbar-width: thin;
            scrollbar-color: var(--fw-border) transparent;
        }

        .fw-msg {
            display: flex;
            flex-direction: column;
            gap: 4px;
            max-width: 85%;
            animation: fw-msg-in 0.2s ease;
        }

        @keyframes fw-msg-in {
            from { opacity: 0; transform: translateY(6px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .fw-msg.user { align-self: flex-end; }
        .fw-msg.assistant { align-self: flex-start; }

        .fw-bubble {
            padding: 10px 14px;
            border-radius: 8px;
            font-size: 14px;
            line-height: 1.6;
            font-family: 'DM Sans', sans-serif;
        }

        .fw-msg.user .fw-bubble {
            background: var(--fw-accent);
            color: #000;
            font-weight: 500;
        }

        .fw-msg.assistant .fw-bubble {
            background: var(--fw-surface);
            border: 1px solid var(--fw-border);
            color: var(--fw-text);
        }

        .fw-msg-image {
            max-width: 200px;
            border-radius: 6px;
            border: 1px solid var(--fw-border);
        }

        /* Cart / Supplier actions */
        .fw-actions {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 8px;
        }

        .fw-action-btn {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            font-size: 12px;
            padding: 6px 12px;
            border-radius: 4px;
            border: none;
            cursor: pointer;
            font-family: 'DM Sans', sans-serif;
            font-weight: 600;
            transition: all 0.2s;
            text-decoration: none;
        }

        .fw-action-cart {
            background: var(--fw-accent);
            color: #000;
        }

        .fw-action-cart:hover { background: #d49300; }

        .fw-action-supplier {
            background: var(--fw-surface2);
            color: var(--fw-text);
            border: 1px solid var(--fw-border);
        }

        .fw-action-supplier:hover {
            border-color: var(--fw-accent);
            color: var(--fw-accent);
        }

        /* Typing indicator */
        .fw-typing {
            display: flex;
            align-items: center;
            gap: 4px;
            padding: 10px 14px;
            background: var(--fw-surface);
            border: 1px solid var(--fw-border);
            border-radius: 8px;
            align-self: flex-start;
        }

        .fw-typing span {
            width: 6px;
            height: 6px;
            background: var(--fw-muted);
            border-radius: 50%;
            animation: fw-bounce 1.2s infinite;
        }

        .fw-typing span:nth-child(2) { animation-delay: 0.2s; }
        .fw-typing span:nth-child(3) { animation-delay: 0.4s; }

        @keyframes fw-bounce {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-6px); background: var(--fw-accent); }
        }

        /* Input area */
        .fw-input-area {
            padding: 12px 16px;
            border-top: 1px solid var(--fw-border);
            background: var(--fw-surface);
            flex-shrink: 0;
        }

        /* Image preview */
        .fw-img-preview {
            display: none;
            position: relative;
            margin-bottom: 8px;
            width: fit-content;
        }

        .fw-img-preview img {
            height: 60px;
            border-radius: 4px;
            border: 1px solid var(--fw-border);
        }

        .fw-img-remove {
            position: absolute;
            top: -6px;
            right: -6px;
            width: 18px;
            height: 18px;
            background: var(--fw-red);
            border: none;
            border-radius: 50%;
            color: #fff;
            font-size: 10px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .fw-input-row {
            display: flex;
            align-items: flex-end;
            gap: 8px;
        }

        .fw-input-box {
            flex: 1;
            background: var(--fw-surface2);
            border: 1px solid var(--fw-border);
            color: var(--fw-text);
            padding: 10px 14px;
            font-family: 'DM Sans', sans-serif;
            font-size: 14px;
            border-radius: 6px;
            outline: none;
            resize: none;
            min-height: 40px;
            max-height: 100px;
            line-height: 1.5;
            transition: border-color 0.2s;
        }

        .fw-input-box:focus { border-color: var(--fw-accent); }
        .fw-input-box::placeholder { color: var(--fw-muted); }

        .fw-img-btn {
            width: 40px;
            height: 40px;
            background: var(--fw-surface2);
            border: 1px solid var(--fw-border);
            border-radius: 6px;
            color: var(--fw-muted);
            font-size: 18px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
            flex-shrink: 0;
        }

        .fw-img-btn:hover {
            border-color: var(--fw-accent);
            color: var(--fw-accent);
        }

        .fw-send-btn {
            width: 40px;
            height: 40px;
            background: var(--fw-accent);
            border: none;
            border-radius: 6px;
            color: #000;
            font-size: 18px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s;
            flex-shrink: 0;
        }

        .fw-send-btn:hover { background: #d49300; }
        .fw-send-btn:disabled { opacity: 0.4; cursor: not-allowed; }

        .fw-file-input { display: none; }

        /* Cart sidebar */
        .fw-cart-badge {
            position: fixed;
            bottom: 96px;
            right: 28px;
            z-index: 9997;
            background: var(--fw-red);
            color: #fff;
            font-size: 11px;
            font-weight: 700;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: none;
            align-items: center;
            justify-content: center;
            font-family: 'DM Mono', monospace;
        }
    `;
    document.head.appendChild(style);

    // ── HTML ─────────────────────────────────────────────────────────────────
    const html = `
        <div id="fw-chat-dot"></div>
        <div id="fw-cart-badge" style="display:none"></div>

        <button id="fw-chat-btn" onclick="fwToggle()" title="Ask Fieldwise">🔧</button>

        <div id="fw-chat-drawer">
            <div class="fw-header">
                <div class="fw-header-left">
                    <div class="fw-header-icon"></div>
                    <div>
                        <div class="fw-header-title">FIELDWISE ENGINEER</div>
                        <div class="fw-header-sub">● ONLINE — 20+ YRS CONSTRUCTION</div>
                    </div>
                </div>
                <button class="fw-close-btn" onclick="fwToggle()">✕</button>
            </div>

            <div class="fw-suggestions">
                <div class="fw-chip" onclick="fwPrompt('What wire size for a 20A circuit?')">⚡ Wire sizing</div>
                <div class="fw-chip" onclick="fwPrompt('How many labor hours to rough in a panel?')">⏱ Labor hours</div>
                <div class="fw-chip" onclick="fwPrompt('Draft an RFI for missing electrical specs')">📋 Draft RFI</div>
                <div class="fw-chip" onclick="fwPrompt('What conduit size for 4 x #12 THHN?')">🔧 Conduit fill</div>
                <div class="fw-chip" onclick="fwPrompt('NEC code for GFCI requirements in bathrooms')">📖 NEC code</div>
                <div class="fw-chip" onclick="fwPrompt('Help me identify this material from a photo')">📸 ID material</div>
            </div>

            <div class="fw-messages" id="fw-messages">
                <div class="fw-msg assistant">
                    <div class="fw-bubble">
                        Hey — I'm your Fieldwise engineer. Ask me anything about electrical, HVAC, plumbing, or fire protection.<br><br>
                        📸 <strong>Send a photo</strong> and I'll identify any material, fitting, or equipment and help you source it.
                    </div>
                </div>
            </div>

            <div class="fw-input-area">
                <div class="fw-img-preview" id="fw-img-preview">
                    <img id="fw-preview-img" src="" alt="">
                    <button class="fw-img-remove" onclick="fwRemoveImg()">✕</button>
                </div>
                <div class="fw-input-row">
                    <button class="fw-img-btn" onclick="document.getElementById('fw-file-input').click()" title="Upload photo">📷</button>
                    <textarea class="fw-input-box" id="fw-input" placeholder="Ask anything… or send a photo to ID materials" rows="1"
                        onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();fwSend()}"></textarea>
                    <button class="fw-send-btn" id="fw-send" onclick="fwSend()">→</button>
                </div>
                <input type="file" id="fw-file-input" class="fw-file-input" accept="image/*" onchange="fwHandleImg(this)">
            </div>
        </div>
    `;

    const container = document.createElement('div');
    container.innerHTML = html;
    document.body.appendChild(container);

    // ── State ────────────────────────────────────────────────────────────────
    let isOpen = false;
    let isLoading = false;
    let pendingImageB64 = null;
    let pendingImageType = null;
    let cart = [];
    const history = [];

    const SYSTEM_PROMPT = `You are a senior construction engineer embedded in the Fieldwise platform with 20+ years of hands-on experience across electrical, HVAC, plumbing, and fire protection trades. You work like a trusted field engineer — direct, practical, no fluff.

Your expertise:
- Electrical: NEC code compliance, panel sizing, wire sizing, conduit fill, load calculations, grounding, GFCI/AFCI requirements
- HVAC: equipment sizing, ductwork, refrigerant lines, controls, ventilation requirements
- Plumbing: pipe sizing, fixture units, UPC/IPC code, drain/waste/vent
- Fire Protection: NFPA 13, sprinkler head selection, pipe sizing, hydraulic calculations

When answering:
- Be specific and give real numbers (wire sizes, conduit sizes, quantities)
- Reference applicable codes (NEC article numbers, NFPA sections)
- If asked for labor hours, give realistic field estimates
- If asked to draft an RFI, produce a professional, complete RFI document
- Keep responses concise — field workers need fast answers

When a user sends a photo:
1. Identify the equipment, material, or fitting precisely (brand/model if visible)
2. Give the proper trade name and spec
3. List compatible materials needed
4. ALWAYS end with: "Want me to find this for you?" with supplier options

IMPORTANT: When identifying materials from photos, always suggest purchasing options. Format like:
[MATERIAL_IDENTIFIED: {name}, {spec}, {estimated_price}]

You are not a general AI — you are a construction specialist. If asked about non-construction topics, redirect politely.`;

    // ── Functions ────────────────────────────────────────────────────────────
    window.fwToggle = function() {
        isOpen = !isOpen;
        document.getElementById('fw-chat-drawer').classList.toggle('open', isOpen);
        document.getElementById('fw-chat-btn').classList.toggle('open', isOpen);
        document.getElementById('fw-chat-dot').style.display = isOpen ? 'none' : 'block';
        if (isOpen) {
            setTimeout(() => document.getElementById('fw-input').focus(), 300);
        }
    };

    window.fwPrompt = function(text) {
        document.getElementById('fw-input').value = text;
        fwSend();
    };

    window.fwHandleImg = function(input) {
        const file = input.files[0];
        if (!file) return;

        // Compress before sending
        const reader = new FileReader();
        reader.onload = (e) => {
            const img = new Image();
            img.onload = () => {
                const canvas = document.createElement('canvas');
                let w = img.width, h = img.height;
                const maxPx = 1600;
                if (w > maxPx || h > maxPx) {
                    const ratio = Math.min(maxPx/w, maxPx/h);
                    w = Math.round(w * ratio);
                    h = Math.round(h * ratio);
                }
                canvas.width = w;
                canvas.height = h;
                canvas.getContext('2d').drawImage(img, 0, 0, w, h);
                const compressed = canvas.toDataURL('image/jpeg', 0.8);
                pendingImageB64 = compressed.split(',')[1];
                pendingImageType = 'image/jpeg';

                document.getElementById('fw-preview-img').src = compressed;
                document.getElementById('fw-img-preview').style.display = 'block';
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
    };

    window.fwRemoveImg = function() {
        pendingImageB64 = null;
        pendingImageType = null;
        document.getElementById('fw-img-preview').style.display = 'none';
        document.getElementById('fw-preview-img').src = '';
        document.getElementById('fw-file-input').value = '';
    };

    window.fwAddToCart = function(name, spec, price) {
        // Load current cart from localStorage
        const stored = JSON.parse(localStorage.getItem('fw_cart') || '[]');
        stored.push({ name, spec, price, qty: 1 });
        localStorage.setItem('fw_cart', JSON.stringify(stored));

        // Update badge
        updateCartBadge(stored.length);

        // Show confirmation in chat
        appendMsg('assistant',
            `✅ Added <strong>${name}</strong> to your cart.\n\nYou have ${stored.length} item(s) ready to order. <a href="/cart" style="color:#f0a500;">View Cart →</a>`,
            null, []
        );
    };

    function updateCartBadge(count) {
        const badge = document.getElementById('fw-cart-badge');
        if (!badge) return;
        if (count > 0) {
            badge.textContent = count;
            badge.style.display = 'flex';
        } else {
            badge.style.display = 'none';
        }
    }

    // Init badge on load
    const initCart = JSON.parse(localStorage.getItem('fw_cart') || '[]');
    if (initCart.length > 0) updateCartBadge(initCart.length);

    window.fwSend = async function() {
        if (isLoading) return;
        const input = document.getElementById('fw-input');
        const text = input.value.trim();
        if (!text && !pendingImageB64) return;

        isLoading = true;
        document.getElementById('fw-send').disabled = true;
        input.value = '';

        // Build user message content
        const userContent = [];
        let displayImg = null;

        if (pendingImageB64) {
            displayImg = document.getElementById('fw-preview-img').src;
            userContent.push({
                type: 'image',
                source: { type: 'base64', media_type: pendingImageType, data: pendingImageB64 }
            });
            fwRemoveImg();
        }

        if (text) {
            userContent.push({ type: 'text', text });
        } else if (pendingImageB64) {
            userContent.push({ type: 'text', text: 'Please identify this material/equipment and help me source it.' });
        }

        // Show user message
        appendMsg('user', text || 'Identify this material for me', displayImg);

        // Add to history
        history.push({ role: 'user', content: userContent });

        // Show typing
        const typingEl = appendTyping();

        try {
          const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        system: SYSTEM_PROMPT,
        messages: history
    })
});

const data = await response.json();
            typingEl.remove();

const reply = data.content || 'Sorry, something went wrong.';
            history.push({ role: 'assistant', content: reply });

            // Parse for material identification
            const materialMatch = reply.match(/\[MATERIAL_IDENTIFIED: ([^,]+), ([^,]+), ([^\]]+)\]/);
            const cleanReply = reply.replace(/\[MATERIAL_IDENTIFIED:[^\]]+\]/, '').trim();

            const actions = [];
            if (materialMatch) {
                const [_, name, spec, price] = materialMatch;
                actions.push({
                    type: 'cart',
                    label: `🛒 Add to Cart — ${name}`,
                    onclick: `fwAddToCart('${name}', '${spec}', '${price}')`
                });
                actions.push({
                    type: 'supplier',
                    label: '🏪 Find at Graybar',
                    href: `https://www.graybar.com/search?q=${encodeURIComponent(name)}`
                });
                actions.push({
                    type: 'supplier',
                    label: '🏪 Find at Rexel',
                    href: `https://www.rexelusa.com/search?q=${encodeURIComponent(name)}`
                });
            } else if (reply.toLowerCase().includes('material') || reply.toLowerCase().includes('supplier') || displayImg) {
                actions.push({
                    type: 'supplier',
                    label: '🏪 Search Graybar',
                    href: `https://www.graybar.com`
                });
                actions.push({
                    type: 'supplier',
                    label: '🏪 Search Rexel',
                    href: `https://www.rexelusa.com`
                });
            }

            appendMsg('assistant', cleanReply, null, actions);

        } catch (err) {
            typingEl.remove();
            appendMsg('assistant', 'Connection error — please try again.');
        }

        isLoading = false;
        document.getElementById('fw-send').disabled = false;
    };

    function appendMsg(role, text, imgSrc, actions) {
        const messages = document.getElementById('fw-messages');
        const div = document.createElement('div');
        div.className = `fw-msg ${role}`;

        let inner = '';
        if (imgSrc) {
            inner += `<img src="${imgSrc}" class="fw-msg-image" alt="Photo">`;
        }
        if (text) {
            inner += `<div class="fw-bubble">${text.replace(/\n/g, '<br>')}</div>`;
        }
        if (actions && actions.length) {
            inner += `<div class="fw-actions">`;
            actions.forEach(a => {
                if (a.type === 'cart') {
                    inner += `<button class="fw-action-btn fw-action-cart" onclick="${a.onclick}">${a.label}</button>`;
                } else {
                    inner += `<a class="fw-action-btn fw-action-supplier" href="${a.href}" target="_blank">${a.label}</a>`;
                }
            });
            inner += `</div>`;
        }

        div.innerHTML = inner;
        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
        return div;
    }

    function appendTyping() {
        const messages = document.getElementById('fw-messages');
        const div = document.createElement('div');
        div.className = 'fw-typing';
        div.innerHTML = '<span></span><span></span><span></span>';
        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
        return div;
    }

    // Auto-resize textarea
    document.getElementById('fw-input').addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 100) + 'px';
    });

})();
