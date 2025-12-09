/**
 * Combat Renderer
 * Handles all visual rendering, animations, and UI updates for combat screen
 */

export const CombatRenderer = {
    /**
     * Render player sprite based on chapter
     */
    renderPlayerSprite(player, chapter) {
        const sprite = document.getElementById('player-sprite');
        
        // Use single sprite image
        sprite.style.backgroundImage = `url('/static/images/player/protagChapter1.png')`;
        sprite.style.backgroundSize = 'contain';
        sprite.style.backgroundPosition = 'center';
        sprite.style.backgroundRepeat = 'no-repeat';
        sprite.style.transform = 'scaleX(-1)'; // Flip horizontally
        
        // Add player name label
        sprite.innerHTML = '';
        const nameLabel = document.createElement('div');
        nameLabel.className = 'player-name-label';
        nameLabel.textContent = player.name || 'Hero';
        nameLabel.style.cssText = 'position: absolute; bottom: -25px; left: 50%; transform: translateX(-50%) scaleX(-1); font-size: 14px; font-weight: bold; color: #c792ea; text-shadow: 2px 2px 4px #000; background: rgba(0,0,0,0.8); padding: 5px 10px; border-radius: 4px; border: 1px solid #c792ea;';
        sprite.appendChild(nameLabel);
    },

    /**
     * Render enemy sprites
     */
    renderEnemySprites(enemies, onTargetClick) {
        const container = document.getElementById('enemies-container');
        container.innerHTML = '';

        enemies.forEach((enemy, index) => {
            // Skip dead enemies - don't render them at all
            if (enemy.hp <= 0) return;

            const enemyDiv = document.createElement('div');
            enemyDiv.className = 'enemy-sprite';
            enemyDiv.id = `enemy-${index}`;
            
            // Map enemy type to sprite
            const enemyType = enemy.type || enemy.name || 'unknown';
            
            const nameMapping = {
                'High Priest': 'highPriest',
                'Apostle': 'apostle',
                'Cultist': 'cultist',
                'Whisperer': 'whisperer',
                'Anatomist': 'anatomist',
                'Wounded Cultist': 'cultist'
            };
            
            const heightMapping = {
                'High Priest': 300,
                'Apostle': 300,
                'Cultist': 300,
                'Whisperer': 300,
                'Anatomist': 350
            };
            
            const fileName = nameMapping[enemyType] || enemyType.toLowerCase().replace(/\s+/g, '_');
            const spriteUrl = `/static/images/enemies/${fileName}.png`;
            const enemyHeight = heightMapping[enemyType] || 300;
            
            // Store data for hurt animation
            enemyDiv.dataset.normalSprite = spriteUrl;
            enemyDiv.dataset.enemyType = enemyType;
            
            // Set background
            enemyDiv.style.backgroundImage = `url('${spriteUrl}')`;
            enemyDiv.style.height = `${enemyHeight}px`;
            
            // Add name label
            const nameLabel = document.createElement('div');
            nameLabel.className = 'enemy-name-label';
            nameLabel.textContent = enemy.name;
            nameLabel.style.cssText = 'position: absolute; top: 5px; left: 50%; transform: translateX(-50%) scaleX(-1); font-size: 12px; font-weight: bold; color: #c792ea; text-shadow: 2px 2px 4px #000; background: rgba(0,0,0,0.7); padding: 4px 8px; border-radius: 4px; white-space: nowrap;';
            enemyDiv.appendChild(nameLabel);
            
            // Add HP indicator
            const hpIndicator = document.createElement('div');
            hpIndicator.className = 'enemy-hp-indicator';
            const hpBar = document.createElement('div');
            hpBar.className = 'enemy-hp-bar';
            hpBar.style.width = `${(enemy.hp / enemy.max_hp) * 100}%`;
            hpIndicator.appendChild(hpBar);
            enemyDiv.appendChild(hpIndicator);
            
            // Click handler for targeting
            if (enemy.hp > 0) {
                enemyDiv.onclick = () => onTargetClick(index);
            }
            
            container.appendChild(enemyDiv);
        });
    },

    /**
     * Update player stats display
     */
    updatePlayerStats(player, xpBarState) {
        // Update HP
        document.getElementById('player-hp').textContent = player.hp;
        document.getElementById('player-max-hp').textContent = player.max_hp;
        const hpPercent = (player.hp / player.max_hp) * 100;
        document.getElementById('hp-bar').style.width = `${hpPercent}%`;
        
        // Update Sanity
        document.getElementById('player-sanity').textContent = player.sanity;
        document.getElementById('player-max-sanity').textContent = player.max_sanity;
        const sanityPercent = (player.sanity / player.max_sanity) * 100;
        document.getElementById('sanity-bar').style.width = `${sanityPercent}%`;
        
        // Update XP
        const exp = player.exp || player.xp || 0;
        const expNext = player.exp_to_next || 50;
        document.getElementById('player-xp').textContent = exp;
        document.getElementById('player-xp-next').textContent = expNext;
        
        // Generate cryptic XP bar
        const ratio = exp / expNext;
        const barLength = 20;
        const filled = Math.floor(ratio * barLength);
        const empty = barLength - filled;
        
        // Store XP bar state for animation
        const newState = {
            filled: filled,
            empty: empty,
            ratio: ratio
        };
        
        // Update cryptic hint
        let hint = '';
        if (ratio > 0.90) {
            hint = 'The veil is threadbare. Revelation is imminent';
        } else if (ratio > 0.75) {
            hint = 'Eyes unseen turn in your direction';
        } else if (ratio > 0.5) {
            hint = 'The veil stirs with whispered secrets';
        } else if (ratio > 0.25) {
            hint = 'A faint ripple disturbs the void';
        } else {
            hint = 'The void is patient';
        }
        document.getElementById('xp-hint').textContent = hint;
        
        return newState;
    },

    /**
     * Update enemy stats panel
     */
    updateEnemyStats(enemies) {
        const container = document.getElementById('enemy-stats-list');
        container.innerHTML = '';

        enemies.forEach((enemy, index) => {
            // Skip dead enemies - don't show them in the stats panel
            if (enemy.hp <= 0) return;

            const row = document.createElement('div');
            row.className = 'enemy-stat-row';
            
            const hpPercent = (enemy.hp / enemy.max_hp) * 100;
            
            row.innerHTML = `
                <div class="enemy-name">${enemy.name}</div>
                <div class="enemy-hp-display">
                    <div class="enemy-hp-bar-container">
                        <div class="enemy-hp-fill" style="width: ${hpPercent}%"></div>
                    </div>
                    <div class="enemy-hp-text">${enemy.hp}/${enemy.max_hp}</div>
                </div>
            `;
            
            container.appendChild(row);
        });
    },

    /**
     * Update doom clock display
     */
    updateDoomClock(doomClock) {
        const value = doomClock.ticks || 100;
        const max = doomClock.start || 100;
        
        document.getElementById('doom-value').textContent = value;
        const percent = (value / max) * 100;
        document.getElementById('doom-bar').style.width = `${percent}%`;
        
        // Update warning message
        const warning = document.getElementById('doom-warning');
        if (percent <= 25) {
            warning.textContent = 'The end is near!';
            warning.style.color = '#ff0000';
        } else if (percent <= 50) {
            warning.textContent = 'Reality fractures...';
            warning.style.color = '#ff6b6b';
        } else {
            warning.textContent = 'The veil grows thinner...';
            warning.style.color = '#ff6b6b';
        }
    },

    /**
     * Add message to combat log
     */
    addCombatLog(message, type = 'normal') {
        const logContent = document.getElementById('combat-log-content');
        const logContainer = document.getElementById('combat-log');
        const entry = document.createElement('div');
        entry.className = `log-entry log-${type}`;
        entry.textContent = message;
        logContent.appendChild(entry);
        
        // Auto-scroll to bottom
        if (logContainer) {
            logContainer.scrollTop = logContainer.scrollHeight;
        }
    },

    /**
     * Show manifestation animation
     */
    showManifestation(manifestationType) {
        const sprite = document.getElementById('manifestation-sprite');
        const spriteUrl = `/static/images/manifestations/${manifestationType.toLowerCase()}.png`;
        sprite.style.backgroundImage = `url('${spriteUrl}')`;
        sprite.classList.add('active');
        
        setTimeout(() => {
            sprite.classList.remove('active');
        }, 2000);
    },

    /**
     * Show enemy hurt animation
     */
    async showEnemyHurt(enemyIndex) {
        const enemyDiv = document.getElementById(`enemy-${enemyIndex}`);
        if (!enemyDiv) return;
        
        const enemyType = enemyDiv.dataset.enemyType;
        const normalSprite = enemyDiv.dataset.normalSprite;
        
        // Map enemy types to hurt sprites
        const hurtSpriteMapping = {
            'Cultist': 'cultistHurt',
            'Wounded Cultist': 'cultistHurt',
            'high_priest': 'highPriestHurt',
            'Apostle': 'apostleHurt',
        };
        
        const hurtFileName = hurtSpriteMapping[enemyType];
        if (!hurtFileName) return; // No hurt sprite available
        
        const hurtSpriteUrl = `/static/images/enemies/${hurtFileName}.png`;
        
        // Switch to hurt sprite
        enemyDiv.style.backgroundImage = `url('${hurtSpriteUrl}')`;
        enemyDiv.classList.add('enemy-hurt');
        
        // Revert after 500ms
        await new Promise(resolve => {
            setTimeout(() => {
                enemyDiv.style.backgroundImage = `url('${normalSprite}')`;
                enemyDiv.classList.remove('enemy-hurt');
                resolve();
            }, 500);
        });
    },

    /**
     * Enable targeting mode visuals
     */
    enableTargetingMode(enemies) {
        enemies.forEach((enemy, index) => {
            if (enemy.hp > 0) {
                const enemyDiv = document.getElementById(`enemy-${index}`);
                if (enemyDiv) {
                    enemyDiv.classList.add('targetable');
                    enemyDiv.style.cursor = 'crosshair';
                }
            }
        });
    },

    /**
     * Disable targeting mode visuals
     */
    disableTargetingMode(enemies) {
        enemies.forEach((enemy, index) => {
            const enemyDiv = document.getElementById(`enemy-${index}`);
            if (enemyDiv) {
                enemyDiv.classList.remove('targetable');
                enemyDiv.style.cursor = enemy.hp > 0 ? 'pointer' : 'not-allowed';
            }
        });
    },

    /**
     * Show manifestation selection modal
     */
    showManifestationModal(player, onSelect, onCancel) {
        const modal = document.getElementById('manifestation-modal');
        const manifestList = document.getElementById('manifestation-list');
        manifestList.innerHTML = '';
        
        const manifestations = player.manifestations || [];
        manifestations.forEach((manifest, index) => {
            const btn = document.createElement('button');
            btn.className = 'manifest-btn';
            btn.textContent = `${manifest.name} (Cost: ${manifest.sanity_cost} sanity)`;
            btn.disabled = player.sanity < manifest.sanity_cost;
            btn.onclick = () => onSelect(index);
            manifestList.appendChild(btn);
        });
        
        modal.style.display = 'flex';
    },

    /**
     * Hide manifestation modal
     */
    hideManifestationModal() {
        document.getElementById('manifestation-modal').style.display = 'none';
    },

    /**
     * Show inventory modal
     */
    showInventoryModal(player, onItemClick) {
        const modal = document.getElementById('inventory-modal');
        const grid = document.getElementById('inventory-grid');
        grid.innerHTML = '';
        
        player.inventory.forEach((item, index) => {
            const itemDiv = document.createElement('div');
            itemDiv.className = `inventory-item ${item.name === player.weapon?.name ? 'equipped' : ''}`;
            itemDiv.innerHTML = `
                <div class="item-name">${item.name}</div>
                <div class="item-quantity">${item.quantity ? `x${item.quantity}` : 'Weapon'}</div>
            `;
            itemDiv.onclick = () => onItemClick(index);
            grid.appendChild(itemDiv);
        });
        
        modal.style.display = 'flex';
    },

    /**
     * Hide inventory modal
     */
    hideInventoryModal() {
        document.getElementById('inventory-modal').style.display = 'none';
    },

    /**
     * Update action button states
     */
    updateActionButtons(player) {
        const reloadBtn = document.getElementById('reload-btn');
        const hasGun = player.weapon && player.weapon.weapon_type === 'gun';
        reloadBtn.disabled = !hasGun;
        
        const manifestBtn = document.getElementById('manifest-btn');
        manifestBtn.disabled = player.sanity <= 0;
    },

    /**
     * Disable all action buttons
     */
    disableAllButtons() {
        document.querySelectorAll('.action-button').forEach(btn => {
            btn.disabled = true;
        });
    },

    /**
     * Enable all action buttons
     */
    enableAllButtons() {
        document.querySelectorAll('.action-button').forEach(btn => {
            btn.disabled = false;
        });
    },

    /**
     * Animate XP bar with shifting glyphs
     */
    animateXPBar(xpBarState) {
        const glyphs = ['⟁', '⌖', 'Ϟ', 'ᛝ', '☍', '⌇', '◈', '⋇', '◍', '⌠', '⌡'];
        const obscured = ['░', '▒', '▓'];
        
        const updateBar = () => {
            if (!xpBarState) return;
            
            const { filled, empty } = xpBarState;
            
            let filledBar = '';
            for (let i = 0; i < filled; i++) {
                filledBar += glyphs[Math.floor(Math.random() * glyphs.length)];
            }
            
            let emptyBar = '';
            for (let i = 0; i < empty; i++) {
                emptyBar += obscured[Math.floor(Math.random() * obscured.length)];
            }
            
            const barElement = document.getElementById('xp-eldritch-bar');
            if (barElement) {
                barElement.innerHTML = 
                    `<span style="color: #9b59b6; font-weight: bold;">${filledBar}</span>` +
                    `<span style="color: #555; opacity: 0.5;">${emptyBar}</span>`;
            }
            
            setTimeout(() => requestAnimationFrame(updateBar), 10000 + Math.random() * 100);
        };
        
        updateBar();
    }
};
