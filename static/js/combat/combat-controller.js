/**
 * Combat Controller
 * Handles combat state management, action processing, and game logic coordination
 */

import { CombatRenderer } from './combat-renderer.js';

export const CombatController = {
    state: {
        currentAction: null,
        targetIndex: null,
        manifestIndex: null,
        player: null,
        enemies: [],
        combatState: null,
        chapter: 1,
        xpBarState: null,
        xpBarAnimationRunning: false
    },

    /**
     * Initialize combat screen with data from API
     */
    async init(combatData) {
        this.state.player = combatData.player;
        this.state.enemies = combatData.enemies;
        this.state.combatState = combatData;
        this.state.chapter = combatData.chapter || 1;

        // Play combat music
        await AudioManager.playEvent('combat_start');

        // Render UI elements
        CombatRenderer.renderPlayerSprite(this.state.player, this.state.chapter);
        CombatRenderer.renderEnemySprites(this.state.enemies, (index) => this.selectTarget(index));
        this.updatePlayerStats();
        this.updateEnemyStats();
        CombatRenderer.updateDoomClock(combatData.doom_clock || { ticks: 100, start: 100 });
        CombatRenderer.addCombatLog('Combat begins!');
        CombatRenderer.updateActionButtons(this.state.player);
    },

    /**
     * Update player stats and start XP animation
     */
    updatePlayerStats() {
        this.state.xpBarState = CombatRenderer.updatePlayerStats(this.state.player, this.state.xpBarState);
        
        if (!this.state.xpBarAnimationRunning) {
            this.state.xpBarAnimationRunning = true;
            CombatRenderer.animateXPBar(this.state.xpBarState);
        }
    },

    /**
     * Update enemy stats display
     */
    updateEnemyStats() {
        CombatRenderer.updateEnemyStats(this.state.enemies);
    },

    /**
     * Handle action button click
     */
    async selectAction(action) {
        this.state.currentAction = action;
        
        switch (action) {
            case 'attack':
                CombatRenderer.enableTargetingMode(this.state.enemies);
                CombatRenderer.addCombatLog('Click an enemy to attack...', 'normal');
                break;
            case 'defend':
                await this.executeAction({ action: 'defend' });
                break;
            case 'manifest':
                this.showManifestationSelection();
                break;
            case 'reload':
                const weaponType = this.state.player.weapon?.weapon_type;
                if (weaponType === 'gun') {
                    await AudioManager.playEvent('reload_gun');
                }
                await this.executeAction({ action: 'reload' });
                break;
        }
    },

    /**
     * Select enemy target (click on sprite)
     */
    selectTarget(index) {
        if (this.state.currentAction === 'attack' || this.state.currentAction === 'manifest') {
            const enemy = this.state.enemies[index];
            if (enemy && enemy.hp > 0) {
                this.confirmTarget(index);
            }
        }
    },

    /**
     * Confirm target selection
     */
    async confirmTarget(index) {
        const action = this.state.currentAction;
        CombatRenderer.disableTargetingMode(this.state.enemies);
        this.state.targetIndex = index;
        
        await this.executeAction({
            action: action,
            target_index: index
        });
    },

    /**
     * Show manifestation selection
     */
    showManifestationSelection() {
        CombatRenderer.showManifestationModal(
            this.state.player,
            (index) => this.confirmManifestation(index),
            () => this.cancelManifestSelection()
        );
    },

    /**
     * Confirm manifestation selection
     */
    async confirmManifestation(index) {
        CombatRenderer.hideManifestationModal();
        
        this.state.manifestIndex = index;
        this.state.currentAction = 'manifest';
        CombatRenderer.enableTargetingMode(this.state.enemies);
        CombatRenderer.addCombatLog('Click an enemy to target with manifestation...', 'normal');
    },

    /**
     * Cancel manifestation selection
     */
    cancelManifestSelection() {
        CombatRenderer.hideManifestationModal();
        this.state.currentAction = null;
    },

    /**
     * Open inventory
     */
    openInventory() {
        // Navigate to full inventory page with combat referrer
        window.location.href = '/inventory?from=combat';
    },

    /**
     * Close inventory (no longer used - kept for compatibility)
     */
    closeInventory() {
        // No-op - inventory page has its own back button
    },

    /**
     * Use inventory item
     */
    async useInventoryItem(index) {
        try {
            const response = await fetch('/api/inventory/use', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ item_index: index })
            });
            
            const result = await response.json();
            
            if (result.success) {
                const item = this.state.player.inventory[index];
                if (item) {
                    const itemName = item.name?.toLowerCase() || '';
                    if (itemName.includes('potion') || itemName.includes('drink')) {
                        await AudioManager.playEvent('consume_potion');
                    } else if (itemName.includes('food') || itemName.includes('bread') || itemName.includes('meat')) {
                        await AudioManager.playEvent('consume_food');
                    }
                }
                
                CombatRenderer.addCombatLog(result.message, 'player');
                this.state.player = result.player;
                this.updatePlayerStats();
                this.closeInventory();
            } else {
                CombatRenderer.addCombatLog(`Error: ${result.error}`, 'enemy');
            }
        } catch (error) {
            console.error('Inventory use error:', error);
            CombatRenderer.addCombatLog('Failed to use item', 'enemy');
        }
    },

    /**
     * Execute combat action via API
     */
    async executeAction(actionData) {
        CombatRenderer.disableAllButtons();
        
        try {
            if (this.state.manifestIndex !== null) {
                actionData.item_index = this.state.manifestIndex;
                this.state.manifestIndex = null;
            }
            
            const response = await fetch('/api/combat/action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(actionData)
            });
            
            const result = await response.json();
            
            if (result.error) {
                CombatRenderer.addCombatLog(`Error: ${result.error}`, 'enemy');
                CombatRenderer.enableAllButtons();
                CombatRenderer.updateActionButtons(this.state.player);
                return;
            }
            
            const previousEnemyHP = actionData.target_index !== undefined && this.state.enemies[actionData.target_index]
                ? this.state.enemies[actionData.target_index].hp
                : null;
            
            // Update state
            this.state.player = result.player;
            this.state.enemies = result.enemies;
            this.state.combatState = result;
            
            // Update UI
            this.updatePlayerStats();
            this.updateEnemyStats();
            
            // Update doom clock if provided
            if (result.doom_clock) {
                CombatRenderer.updateDoomClock(result.doom_clock);
            }
            
            // Play weapon sound (BEFORE animation) - only if sfx is provided
            if (actionData.action === 'attack' && result.sfx) {
                // Backend returns sfx only when attack was successful (gun had ammo)
                this.playWeaponSound(result.player.weapon);
            }
            
            // Play manifestation sound (BEFORE animation)
            if (actionData.action === 'manifest' && result.manifestation_used) {
                const manifestName = result.manifestation_used.toLowerCase();
                AudioManager.playEvent(`manifestation_${manifestName}`);
                CombatRenderer.showManifestation(result.manifestation_used);
            }
            
            // Show hurt animation
            if (actionData.target_index !== undefined && result.enemies) {
                const targetEnemy = result.enemies[actionData.target_index];
                if (previousEnemyHP !== null && targetEnemy && targetEnemy.hp < previousEnemyHP) {
                    await CombatRenderer.showEnemyHurt(actionData.target_index);
                }
            }
            
            // Render sprites after animation
            CombatRenderer.renderEnemySprites(this.state.enemies, (index) => this.selectTarget(index));
            
            // Show combat log
            if (result.combat_log) {
                result.combat_log.forEach(msg => {
                    const type = msg.includes('You') ? 'player' : 'enemy';
                    CombatRenderer.addCombatLog(msg, type);
                });
            }
            
            // Check combat end
            if (result.combat_over) {
                this.handleCombatEnd(result);
            }
        } catch (error) {
            console.error('Combat action error:', error);
            CombatRenderer.addCombatLog('Action failed', 'enemy');
        } finally {
            CombatRenderer.enableAllButtons();
            CombatRenderer.updateActionButtons(this.state.player);
        }
    },

    /**
     * Play weapon sound based on weapon type
     */
    playWeaponSound(weapon) {
        if (!weapon) return;
        
        const weaponType = weapon.weapon_type;
        if (weaponType === 'gun') {
            const weaponName = weapon.name?.toLowerCase() || '';
            if (weaponName.includes('revolver')) {
                AudioManager.playEvent('attack_revolver');
            } else if (weaponName.includes('rifle') || weaponName.includes('ar-')) {
                AudioManager.playEvent('attack_rifle');
            } else if (weaponName.includes('mp') || weaponName.includes('submachine')) {
                AudioManager.playEvent('attack_submachine');
            } else {
                AudioManager.playEvent('attack_rifle');
            }
        } else if (weaponType === 'melee') {
            const weaponName = weapon.name?.toLowerCase() || '';
            if (weaponName.includes('sword')) {
                AudioManager.playEvent('attack_sword');
            } else {
                AudioManager.playEvent('attack_knife');
            }
        }
    },

    /**
     * Handle combat end
     */
    async handleCombatEnd(result) {
        if (result.game_over) {
            // Doom reached zero - instant loss
            AudioManager.stopMusic();
            CombatRenderer.addCombatLog('💀 THE DOOM REACHES ZERO. REALITY COLLAPSES. 💀', 'enemy');
            setTimeout(() => {
                alert('GAME OVER\n\nThe Doom Clock struck zero. The fabric of reality tears apart.\n\nThe world ends in eternal darkness.');
                window.location.href = '/';
            }, 3000);
        } else if (result.victory) {
            AudioManager.stopMusic();
            await AudioManager.playEvent('level_up');
            
            CombatRenderer.addCombatLog('VICTORY! You have defeated your enemies!', 'player');
            setTimeout(() => {
                alert(`Victory! Gained ${result.xp_gained || 0} XP`);
                window.location.href = '/story';
            }, 2000);
        } else if (result.player_died) {
            AudioManager.stopMusic();
            
            CombatRenderer.addCombatLog('You have been defeated...', 'enemy');
            setTimeout(() => {
                alert('Game Over');
                window.location.href = '/';
            }, 2000);
        }
    },

    /**
     * Show help modal
     */
    showHelp() {
        alert(`Combat Controls:
        
Attack - Attack an enemy with your equipped weapon
Defend - Reduce damage from next attack by 50%
Manifest - Use a manifestation power (costs sanity)
Reload - Reload your firearm (if equipped)
Inventory - Use items or change weapons

Click on enemies to target them!`);
    }
};

// Expose to global scope for HTML onclick handlers
window.CombatUI = CombatController;
