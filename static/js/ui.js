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
            .then(html => {
                app.innerHTML = html;
                
                // Re-attach event listeners after injecting HTML
                const startBtn = document.getElementById('btn-start');
                const helpBtn = document.getElementById('btn-help');
                
                if (startBtn) {
                    startBtn.addEventListener('click', onStart);
                }
                if (helpBtn) {
                    helpBtn.addEventListener('click', onHelp);
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
     * Render story text and choices
     */
    renderStory(storyNode) {
        // TODO: Implement story UI
        // - Story text display
        // - Choice buttons
        // - Continue button
    }
};
