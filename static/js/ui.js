/**
 * UI rendering module
 * Handles all DOM manipulation and UI components
 */

const UI = {
    /**
     * Clear the main app container
     */
    clear() {
        document.getElementById('app').innerHTML = '';
    },

    /**
     * Render main menu
     */
    renderMainMenu(onStart, onHelp) {
        this.clear();
        const app = document.getElementById('app');
        
        // Store callbacks globally so the menu can access them
        window.menuCallbacks = {
            onStart: onStart,
            onHelp: onHelp
        };
        
        // Fetch and load the mainMenu.html template
        fetch('/menu')
            .then(response => response.text())
            .then(async (html) => {
                // Extract just the content without the HTML wrapper
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const mainMenuWrapper = doc.querySelector('.main-menu-wrapper');
                const styleTag = doc.querySelector('style');
                
                // Inject the content
                app.innerHTML = mainMenuWrapper.outerHTML;
                
                // Inject styles if they exist
                if (styleTag && !document.getElementById('main-menu-styles')) {
                    const style = document.createElement('style');
                    style.id = 'main-menu-styles';
                    style.textContent = styleTag.textContent;
                    document.head.appendChild(style);
                }
                
                // Ensure the shared help modal is available
                await this.initializeHelpModal();

                // Re-attach event listeners after injecting HTML
                const startBtn = document.getElementById('btn-start');
                const helpBtn = document.getElementById('btn-help');
                
                if (startBtn) {
                    startBtn.addEventListener('click', onStart);
                }
                
                if (helpBtn) {
                    helpBtn.addEventListener('click', (e) => {
                        e.preventDefault();
                        if (typeof onHelp === 'function') {
                            onHelp();
                        }
                    });
                }
            })
            .catch(error => {
                console.error('Failed to load menu:', error);
                // Fallback to simple menu
                app.innerHTML = `
                    <div class="main-menu text-center">
                        <h1 class="text-purple">RITES OF TRANSIT</h1>
                        <p class="text-dim">A Lovecraftian Horror RPG</p>
                        <div class="menu-options">
                            <button id="btn-start" class="btn">Descend into the Unknown</button>
                            <button id="btn-help" class="btn">Whispers of Guidance</button>
                        </div>
                    </div>
                `;
                
                document.getElementById('btn-start').addEventListener('click', onStart);
                document.getElementById('btn-help').addEventListener('click', onHelp);
            });
    },

    /**
     * Render game HUD (HP, Sanity, Doom Clock, etc.)
     */
    renderHUD(player, doomClock) {
        // TODO: Implement HUD rendering
        // - HP bar
        // - Sanity bar
        // - XP bar
        // - Doom clock
        // - Markka display
    },

    /**
     * Render status bars
     */
    renderStatusBar(current, max, type = 'hp') {
        const percentage = (current / max) * 100;
        const color = type === 'hp' ? 'red' : type === 'sanity' ? 'purple' : 'yellow';
        
        return `
            <div class="status-bar">
                <div class="status-bar-fill status-bar-${color}" style="width: ${percentage}%"></div>
                <span class="status-bar-text">${current}/${max}</span>
            </div>
        `;
    },

    /**
     * Render typewriter text effect
     */
    async typewriterText(element, text, speed = 30) {
        element.textContent = '';
        for (let char of text) {
            element.textContent += char;
            await new Promise(resolve => setTimeout(resolve, speed));
        }
    },

    /**
     * Show message/notification
     */
    showMessage(message, type = 'info') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${type}`;
        messageDiv.textContent = message;
        
        document.getElementById('app').appendChild(messageDiv);
        
        setTimeout(() => {
            messageDiv.remove();
        }, 3000);
    },

    /**
     * Render combat UI
     */
    renderCombat(player, enemies, combatLog) {
        // TODO: Implement combat UI
        // - Enemy list with HP bars
        // - Action buttons
        // - Combat log
        // - Player status
    },

    /**
     * Render inventory UI
     */
    renderInventory(inventoryData) {
        // TODO: Implement inventory UI
        // - Weapons list
        // - Consumables list
        // - Ammo display
        // - Equipment section
    },

    /**
     * Render travel/airport selection UI
     */
    renderTravel(destinations, currentLocation) {
        // TODO: Implement travel UI
        // - Airport list with distances and costs
        // - Current location display
        // - Travel button
    },

    /**
     * Initialize help modal functionality for any page
     * Loads help modal from help_modal.html template and sets up event listeners
     */
    async initializeHelpModal() {
        // Check if modal already exists
        if (document.getElementById('helpModal')) {
            this.attachHelpModalListeners();
            return;
        }

        try {
            // Fetch the help modal template
            const response = await fetch('/help_modal');
            const modalHTML = await response.text();

            // Create a container for the modal if it doesn't exist
            let container = document.getElementById('help-modal-container');
            if (!container) {
                container = document.createElement('div');
                container.id = 'help-modal-container';
                document.body.appendChild(container);
            }

            // Inject the modal HTML
            container.innerHTML = modalHTML;

            // Inject CSS if not already present
            if (!document.getElementById('help-modal-styles')) {
                const style = document.createElement('style');
                style.id = 'help-modal-styles';
                style.textContent = `
                    /* Help Modal Styles */
                    .help-modal {
                        position: fixed;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        background: rgba(0, 0, 0, 0.9);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        z-index: 1000;
                        padding: 20px;
                    }

                    .help-modal-content {
                        background: rgba(20, 20, 20, 0.95);
                        border: 2px solid #66ffcc;
                        border-radius: 10px;
                        padding: 40px 50px;
                        max-width: 800px;
                        max-height: 85vh;
                        overflow-y: auto;
                        box-shadow: 0 0 40px rgba(102, 255, 204, 0.3);
                        color: #fff;
                        font-family: 'Courier New', monospace;
                        position: relative;
                    }

                    .help-close-btn {
                        position: absolute;
                        top: 15px;
                        right: 20px;
                        background: none;
                        border: none;
                        color: #66ffcc;
                        font-size: 32px;
                        cursor: pointer;
                        transition: 0.3s;
                    }

                    .help-close-btn:hover {
                        color: #ff66cc;
                        transform: scale(1.2);
                    }

                    .help-title {
                        color: #ff66cc;
                        text-align: center;
                        margin-bottom: 30px;
                        margin-top: 10px;
                        font-size: 24px;
                        font-family: 'Press Start 2P', cursive;
                        text-shadow: 0 0 10px #ff66cc;
                    }

                    .help-section {
                        margin-bottom: 25px;
                    }

                    .help-section h3 {
                        color: #66ffcc;
                        margin-bottom: 12px;
                        font-size: 16px;
                        text-shadow: 0 0 5px #66ffcc;
                    }

                    .help-section p {
                        line-height: 1.6;
                        margin-bottom: 12px;
                        font-size: 13px;
                    }

                    .doom-text {
                        color: #ff3333;
                        font-weight: bold;
                    }

                    .controls-grid {
                        display: grid;
                        grid-template-columns: 1fr 1fr;
                        gap: 20px;
                        margin-bottom: 15px;
                    }

                    .control-item {
                        background: rgba(50, 50, 50, 0.8);
                        border-left: 3px solid #66ffcc;
                        padding: 15px;
                        border-radius: 5px;
                    }

                    .control-item strong {
                        color: #66ffcc;
                        display: block;
                        margin-bottom: 8px;
                    }

                    .control-item ul {
                        list-style: none;
                        padding: 0;
                        margin: 0;
                    }

                    .control-item li {
                        margin: 6px 0;
                        font-size: 12px;
                        color: #ddd;
                    }

                    kbd {
                        background: #333;
                        border: 1px solid #666;
                        border-radius: 3px;
                        padding: 2px 6px;
                        font-family: monospace;
                        color: #66ffcc;
                    }

                    .key-concepts {
                        list-style: none;
                        padding: 0;
                        margin: 0;
                    }

                    .key-concepts li {
                        background: rgba(50, 50, 50, 0.8);
                        border-left: 3px solid #ff66cc;
                        padding: 12px;
                        margin-bottom: 10px;
                        border-radius: 5px;
                        font-size: 13px;
                    }

                    .key-concepts strong {
                        color: #66ffcc;
                    }

                    .help-footer {
                        text-align: center;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #333;
                    }

                    .flavor-text {
                        color: #ff66cc;
                        font-style: italic;
                        font-size: 14px;
                        text-shadow: 0 0 5px #ff66cc;
                    }

                    .help-button {
                        position: fixed;
                        top: 20px;
                        right: 20px;
                        width: 40px;
                        height: 40px;
                        border-radius: 50%;
                        background: rgba(102, 255, 204, 0.1);
                        border: 2px solid #66ffcc;
                        color: #66ffcc;
                        font-size: 24px;
                        font-weight: bold;
                        cursor: pointer;
                        z-index: 100;
                        transition: all 0.3s;
                        font-family: 'Courier New', monospace;
                    }

                    .help-button:hover {
                        background: rgba(102, 255, 204, 0.2);
                        box-shadow: 0 0 15px #66ffcc;
                        transform: scale(1.1);
                    }
                `;
                document.head.appendChild(style);
            }

            // Attach event listeners
            this.attachHelpModalListeners();
        } catch (error) {
            console.error('Failed to load help modal:', error);
        }
    },

    /**
     * Attach event listeners to help modal elements
     */
    attachHelpModalListeners() {
        const helpBtn = document.getElementById('btn-help');
        const helpModal = document.getElementById('helpModal');
        const helpCloseBtn = document.getElementById('helpCloseBtn');
        
        if (helpBtn) {
            helpBtn.addEventListener('click', (e) => {
                e.preventDefault();
                if (helpModal) {
                    helpModal.style.display = 'flex';
                }
            });
        }
        
        // Close help modal when close button is clicked
        if (helpCloseBtn) {
            helpCloseBtn.addEventListener('click', (e) => {
                e.preventDefault();
                if (helpModal) {
                    helpModal.style.display = 'none';
                }
            });
        }
        
        // Close help modal when clicking outside the modal content
        if (helpModal) {
            helpModal.addEventListener('click', (e) => {
                if (e.target === helpModal) {
                    helpModal.style.display = 'none';
                }
            });
        }
    },

    /**
     * Render story text and choices
     */
    renderStory(storyNode) {
        // TODO: Implement story UI
        // - Story text display
        // - Choice buttons
        // - Continue button
    }
};
