/**
 * Main game logic and state management
 */

const Game = {
    state: {
        player: null,
        gameState: null,
        doomClock: null,
        inCombat: false,
        currentScreen: 'menu' // menu, game, combat, inventory, travel, story
    },

    /**
     * Initialize the game
     */
    async init() {
        console.log('Initializing game...');
        UI.renderMainMenu(
            () => this.startNewGame(),
            () => this.showHelp()
        );
    },

    /**
     * Start a new game
     */
    async startNewGame() {
        try {
            UI.showMessage('Starting new game...', 'info');
            const response = await API.game.start();
            
            if (response.success) {
                this.state.player = response.player;
                this.state.gameState = response.game_state;
                this.state.doomClock = response.doom_clock;
                this.state.currentScreen = 'story';
                
                // Redirect to story page
                window.location.href = '/story';
            }
        } catch (error) {
            UI.showMessage('Failed to start game', 'error');
            console.error(error);
        }
    },

    /**
     * Render main game screen
     */
    renderGameScreen() {
        UI.clear();
        // TODO: Render main game interface
        // - HUD
        // - Action menu
        // - Current location info
    },

    /**
     * Show help/tutorial
     */
    showHelp() {
        UI.showMessage('Help section coming soon!', 'info');
        // TODO: Implement help screen
    },

    /**
     * Handle combat
     */
    async startCombat(enemies) {
        this.state.inCombat = true;
        this.state.currentScreen = 'combat';
        
        try {
            const response = await API.combat.start(enemies);
            if (response.success) {
                UI.renderCombat(response.data.player, response.data.enemies, []);
            }
        } catch (error) {
            UI.showMessage('Failed to start combat', 'error');
            console.error(error);
        }
    },

    /**
     * Handle travel
     */
    async openTravel() {
        this.state.currentScreen = 'travel';
        
        try {
            const response = await API.travel.getDestinations();
            if (response.success) {
                UI.renderTravel(response.data.destinations, response.data.current_location);
            }
        } catch (error) {
            UI.showMessage('Failed to load destinations', 'error');
            console.error(error);
        }
    },

    /**
     * Handle inventory
     */
    async openInventory() {
        this.state.currentScreen = 'inventory';
        
        try {
            const response = await API.inventory.get();
            if (response.success) {
                UI.renderInventory(response.data);
            }
        } catch (error) {
            UI.showMessage('Failed to load inventory', 'error');
            console.error(error);
        }
    },

    /**
     * Handle story progression
     */
    async continueStory(choiceIndex = null) {
        try {
            let response;
            if (choiceIndex !== null) {
                // Make a choice
                response = await API.story.makeChoice(choiceIndex);
            } else {
                // Continue with no choice (for linear story nodes)
                response = await API.story.continue();
            }
            
            if (response.success) {
                UI.renderStory(response.data);
                
                // Handle music changes
                if (response.data.music) {
                    const music = response.data.music;
                    if (music.action === 'play') {
                        AudioManager.playMusic(music.track, {
                            volume: music.volume,
                            loop: music.loop
                        });
                    } else if (music.action === 'stop') {
                        AudioManager.stopMusic();
                    }
                }

                // Handle combat triggers
                if (response.data.combat) {
                    await this.startCombat(response.data.combat.enemies);
                }
            }
        } catch (error) {
            UI.showMessage('Failed to progress story', 'error');
            console.error(error);
        }
    }
};
