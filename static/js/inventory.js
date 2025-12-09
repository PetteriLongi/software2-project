/**
 * inventory.js - Inventory system UI controller
 * 
 * Manages the inventory screen display and interactions.
 */

class InventoryManager {
    constructor() {
        this.inventory = [];
        this.weapons = [];
        this.equippedWeapon = null;
        this.playerStats = {};
        this.selectedSlot = null;
        
        this.initElements();
        this.initEventListeners();
    }

    initElements() {
        // UI Elements
        this.playerHp = document.getElementById('playerHp');
        this.playerMaxHp = document.getElementById('playerMaxHp');
        this.playerSanity = document.getElementById('playerSanity');
        this.playerMaxSanity = document.getElementById('playerMaxSanity');
        this.playerLevel = document.getElementById('playerLevel');
        this.levelDisplay = document.getElementById('levelDisplay');
        this.moneyAmount = document.getElementById('moneyAmount');
        
        this.weaponsGrid = document.getElementById('weaponsGrid');
        this.consumablesGrid = document.getElementById('consumablesGrid');
        this.gunRack = document.getElementById('gunRack');
        this.meleeRack = document.getElementById('meleeRack');
        
        this.backButton = document.getElementById('backButton');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.messageBox = document.getElementById('messageBox');
    }

    initEventListeners() {
        this.backButton.addEventListener('click', () => this.handleBack());
    }

    async init() {
        console.log('Initializing inventory manager...');
        
        // Initialize audio if available
        if (window.AudioManager) {
            await AudioManager.playEvent('menu_open');
        }
        
        // Load inventory data
        await this.loadInventory();
        
        // Render UI
        this.render();
    }

    async loadInventory() {
        try {
            this.showLoading(true);
            
            const response = await API.inventory.get();
            
            if (response.success) {
                this.inventory = response.inventory || [];
                this.weapons = response.weapons || [];
                this.equippedWeapon = response.equipped_weapon;
                this.playerStats = response.player_stats || {};
                
                // Store ammo separately for easier access
                if (response.ammo) {
                    this.playerStats.ammo = response.ammo;
                }
                
                console.log('Inventory loaded:', this.inventory);
                console.log('Weapons:', this.weapons);
                console.log('Ammo:', this.playerStats.ammo);
            } else {
                this.showMessage(response.error || 'Failed to load inventory', 'error');
            }
        } catch (error) {
            console.error('Failed to load inventory:', error);
            this.showMessage('Error loading inventory', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    render() {
        this.renderStats();
        this.renderWeaponsGrid();
        this.renderConsumablesGrid();
        this.renderWeaponRacks();
    }

    renderStats() {
        // Update player stats display
        console.log('Rendering stats:', this.playerStats);
        
        if (this.playerStats.hp !== undefined) {
            this.playerHp.textContent = this.playerStats.hp;
            this.playerMaxHp.textContent = this.playerStats.max_hp;
        }
        
        if (this.playerStats.sanity !== undefined) {
            this.playerSanity.textContent = this.playerStats.sanity;
            this.playerMaxSanity.textContent = this.playerStats.max_sanity;
        }
        
        if (this.playerStats.level !== undefined) {
            this.playerLevel.textContent = this.playerStats.level;
            this.levelDisplay.textContent = `Level ${this.playerStats.level}`;
        }
        
        if (this.playerStats.markka !== undefined) {
            console.log('Setting markka to:', this.playerStats.markka);
            this.moneyAmount.textContent = this.playerStats.markka.toLocaleString();
        } else {
            console.warn('Markka is undefined in playerStats');
        }
    }

    renderWeaponsGrid() {
        this.weaponsGrid.innerHTML = '';
        
        // Filter weapons from inventory
        const weapons = this.inventory.filter(item => item.weapon_type);
        
        // Display weapons in grid
        for (let i = 0; i < weapons.length; i++) {
            const item = weapons[i];
            const slot = document.createElement('div');
            slot.className = 'inventory_slot occupied';
            slot.dataset.index = this.inventory.indexOf(item);
            
            // Add ammo count for guns at the top
            if (item.weapon_type === 'gun' && item.ammo_type) {
                const ammoLabel = document.createElement('div');
                ammoLabel.className = 'ammo_count';
                // Look up ammo in the ammo pool
                const ammoAmount = this.playerStats.ammo && this.playerStats.ammo[item.ammo_type] 
                    ? this.playerStats.ammo[item.ammo_type] 
                    : (item.current_mag || 0);
                ammoLabel.textContent = `${ammoAmount}x`;
                slot.appendChild(ammoLabel);
            }
            
            const img = document.createElement('img');
            img.src = this.getWeaponIcon(item);
            img.alt = item.name;
            slot.appendChild(img);
            
            // Add item name label
            const nameLabel = document.createElement('div');
            nameLabel.className = 'item_name';
            nameLabel.textContent = item.name;
            slot.appendChild(nameLabel);
            
            // Add tooltip
            const tooltip = document.createElement('div');
            tooltip.className = 'item_tooltip';
            tooltip.innerHTML = this.getItemTooltip(item);
            slot.appendChild(tooltip);
            
            // Add click handler
            slot.addEventListener('click', () => this.handleItemClick(item, this.inventory.indexOf(item)));
            
            this.weaponsGrid.appendChild(slot);
        }
    }

    renderConsumablesGrid() {
        this.consumablesGrid.innerHTML = '';
        
        // Filter consumables from inventory, excluding ammo (type = 'ammo')
        const consumables = this.inventory.filter(item => !item.weapon_type && item.type !== 'ammo');
        
        // Display consumables in grid
        for (let i = 0; i < consumables.length; i++) {
            const item = consumables[i];
            const slot = document.createElement('div');
            slot.className = 'inventory_slot occupied';
            slot.dataset.index = this.inventory.indexOf(item);
            
            const img = document.createElement('img');
            img.src = this.getItemIcon(item);
            img.alt = item.name;
            slot.appendChild(img);
            
            // Add item name label
            const nameLabel = document.createElement('div');
            nameLabel.className = 'item_name';
            nameLabel.textContent = item.name;
            slot.appendChild(nameLabel);
            
            // Add stack count if applicable
            if (item.quantity && item.quantity > 1) {
                const count = document.createElement('div');
                count.className = 'item_count';
                count.textContent = item.quantity;
                slot.appendChild(count);
            }
            
            // Add tooltip
            const tooltip = document.createElement('div');
            tooltip.className = 'item_tooltip';
            tooltip.innerHTML = this.getItemTooltip(item);
            slot.appendChild(tooltip);
            
            // Add click handler
            slot.addEventListener('click', () => this.handleItemClick(item, this.inventory.indexOf(item)));
            
            this.consumablesGrid.appendChild(slot);
        }
    }

    renderWeaponRacks() {
        // Render gun rack (ranged weapons)
        this.gunRack.innerHTML = '';
        const rangedWeapons = this.weapons.filter(w => w.weapon_type === 'ranged');
        
        for (let i = 0; i < 4; i++) {
            const hook = document.createElement('div');
            hook.className = 'gun_hook';
            
            const hookImg = document.createElement('img');
            hookImg.className = 'hook';
            hookImg.src = '/static/images/inventory/weapon_RACK.png';
            hook.appendChild(hookImg);
            
            if (i < rangedWeapons.length) {
                const weapon = rangedWeapons[i];
                const weaponImg = document.createElement('img');
                weaponImg.className = 'weapon';
                weaponImg.src = this.getWeaponIcon(weapon);
                weaponImg.alt = weapon.name;
                hook.appendChild(weaponImg);
                
                hook.addEventListener('click', () => this.handleWeaponClick(weapon));
            } else {
                hook.classList.add('empty');
            }
            
            this.gunRack.appendChild(hook);
        }
        
        // Render melee rack
        this.meleeRack.innerHTML = '';
        const meleeWeapons = this.weapons.filter(w => w.weapon_type === 'melee');
        
        for (let i = 0; i < 2; i++) {
            const slot = document.createElement('div');
            slot.className = 'melee_slot';
            
            if (i < meleeWeapons.length) {
                const weapon = meleeWeapons[i];
                const weaponImg = document.createElement('img');
                weaponImg.src = this.getWeaponIcon(weapon);
                weaponImg.alt = weapon.name;
                slot.appendChild(weaponImg);
                
                slot.addEventListener('click', () => this.handleWeaponClick(weapon));
            }
            
            this.meleeRack.appendChild(slot);
        }
    }

    getItemIcon(item) {
        // Map specific item names to their sprite paths
        const itemNameMap = {
            'Karelian pie': '/static/images/consumables/karelian-pie.png',
            'Rye Bread': '/static/images/consumables/rye-bread.png',
            'Small coffee': '/static/images/consumables/small-coffee.png',
            'Large coffee': '/static/images/consumables/large-coffee.png',
            'Makkara': '/static/images/consumables/makkara.png',
        };
        
        // Check if this item has a specific sprite
        if (itemNameMap[item.name]) {
            return itemNameMap[item.name];
        }
        
        // Map item types to icons (placeholder implementation)
        const typeIconMap = {
            'health_potion': '/static/images/consumables/health-potion.png',
            'sanity_potion': '/static/images/consumables/sanity-potion.png',
            'ammo': '/static/images/consumables/ammo.png',
            'key': '/static/images/consumables/key.png',
        };
        
        return typeIconMap[item.type] || '/static/images/consumables/default.png';
    }

    getWeaponIcon(weapon) {
        // Map weapon names to their sprite paths
        const weaponIconMap = {
            'AR-15': '/static/images/weapons/AR-15.png',
            'MP7': '/static/images/weapons/mp-7.png',
            'Basic dagger': '/static/images/weapons/basicDagger.png',
            'Ulfberht sword': '/static/images/weapons/sword.png',
            'Old revolver': '/static/images/weapons/revolver.png',
            'Jack\'s hammer': '/static/images/weapons/hammer.png',
        };
        
        // Use specific weapon sprite if available, otherwise use weapon_type as fallback
        if (weaponIconMap[weapon.name]) {
            return weaponIconMap[weapon.name];
        }
        
        // Fallback: try to use weapon_type (gun, melee, etc.)
        const typeIconMap = {
            'gun': '/static/images/weapons/gun.png',
            'rifle': '/static/images/weapons/rifle.png',
            'melee': '/static/images/weapons/melee.png',
            'sword': '/static/images/weapons/sword.png',
            'knife': '/static/images/weapons/knife.png'
        };
        
        return typeIconMap[weapon.weapon_type] || '/static/images/weapons/default.png';
    }

    getItemTooltip(item) {
        let tooltip = `<strong>${item.name}</strong><br>`;
        
        if (item.description) {
            tooltip += `${item.description}<br>`;
        }
        
        if (item.effect) {
            tooltip += `<em>${item.effect}</em>`;
        }
        
        return tooltip;
    }

    async handleItemClick(item, index) {
        console.log('Item clicked:', item);
        
        // Check if item is a weapon (has weapon_type property)
        if (item.weapon_type) {
            const confirmed = confirm(`Equip ${item.name}?`);
            if (confirmed) {
                await this.equipWeaponByIndex(index);
            }
        }
        // For consumable items, use them (has quantity property)
        else if (item.quantity !== undefined) {
            const confirmed = confirm(`Use ${item.name}?`);
            if (confirmed) {
                await this.useItem(index);
            }
        } else {
            this.showMessage(`${item.name} - ${item.description || 'Quest item'}`, 'info');
        }
    }

    async handleWeaponClick(weapon) {
        console.log('Weapon clicked:', weapon);
        
        const confirmed = confirm(`Equip ${weapon.name}?`);
        if (confirmed) {
            await this.equipWeapon(weapon);
        }
    }

    async useItem(itemIndex) {
        try {
            this.showLoading(true);
            
            const response = await API.inventory.use(itemIndex);
            
            if (response.success) {
                this.showMessage(response.message, 'success');
                
                // Play sound effect if provided
                if (response.sfx && window.AudioManager) {
                    // Map sfx names to audio events
                    const sfxMap = {
                        'Eating': 'consume_food',
                        'Drinking': 'consume_potion'
                    };
                    const audioEvent = sfxMap[response.sfx];
                    if (audioEvent) {
                        await AudioManager.playEvent(audioEvent);
                    }
                }
                
                // Reload inventory
                await this.loadInventory();
                this.render();
            } else {
                this.showMessage(response.error || 'Cannot use item', 'error');
            }
        } catch (error) {
            console.error('Failed to use item:', error);
            this.showMessage('Error using item', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async equipWeapon(weapon) {
        try {
            this.showLoading(true);
            
            console.log('Attempting to equip weapon:', weapon);
            console.log('Full inventory:', this.inventory);
            
            // Find weapon index in the FULL inventory
            // Weapons don't have a 'type' field - they have weapon_type, mag_size, etc.
            const weaponIndex = this.inventory.findIndex(item => 
                item.name === weapon.name
            );
            
            console.log('Found weapon at index:', weaponIndex);
            
            if (weaponIndex === -1) {
                this.showMessage(`Weapon ${weapon.name} not found in inventory`, 'error');
                return;
            }
            
            await this.equipWeaponByIndex(weaponIndex);
            
        } catch (error) {
            console.error('Failed to equip weapon:', error);
            this.showMessage('Error equipping weapon: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    async equipWeaponByIndex(weaponIndex) {
        try {
            this.showLoading(true);
            
            console.log('Equipping weapon at index:', weaponIndex);
            
            const response = await API.inventory.equip(weaponIndex);
            
            console.log('Equip response:', response);
            
            if (response.success) {
                const weaponName = this.inventory[weaponIndex]?.name || 'weapon';
                this.showMessage(`Equipped ${weaponName}`, 'success');
                
                // Play sound effect
                if (window.AudioManager) {
                    await AudioManager.playEvent('weapon_equip');
                }
                
                // Reload inventory
                await this.loadInventory();
                this.render();
            } else {
                this.showMessage(response.error || response.message || 'Cannot equip weapon', 'error');
            }
        } catch (error) {
            console.error('Failed to equip weapon:', error);
            this.showMessage('Error equipping weapon: ' + error.message, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    handleBack() {
        // Navigate back to where we came from
        const referrer = this.backButton.dataset.referrer || 'story';
        
        const routeMap = {
            'story': '/story',
            'travel': '/travel',
            'combat': '/combat'
        };
        
        window.location.href = routeMap[referrer] || '/story';
    }

    showLoading(show) {
        if (show) {
            this.loadingOverlay.classList.add('active');
        } else {
            this.loadingOverlay.classList.remove('active');
        }
    }

    showMessage(message, type = 'success') {
        this.messageBox.textContent = message;
        this.messageBox.className = 'message_box visible';
        
        if (type === 'error') {
            this.messageBox.classList.add('error');
        }
        
        setTimeout(() => {
            this.messageBox.classList.remove('visible');
        }, 3000);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    const manager = new InventoryManager();
    await manager.init();
});
