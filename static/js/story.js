/**
 * Story Screen Handler - Typewriter Effect
 */

const StoryScreen = {
    elements: {
        storyText: null,
        choices: null,
        continueIndicator: null,
        typewriterSound: null,
        backgroundTypewriter: null,
        paperContainer: null
    },

    state: {
        isTyping: false,
        currentText: '',
        currentIndex: 0,
        typeSpeed: 30, // milliseconds per character
        skipTyping: false,
        currentStoryData: null,
        storyStarted: false
    },

    /**
     * Initialize story screen
     */
    init() {
        this.elements.storyText = document.getElementById('story-text');
        this.elements.choices = document.getElementById('story-choices');
        this.elements.continueIndicator = document.getElementById('continue-indicator');
        this.elements.typewriterSound = document.getElementById('typewriter-sound');
        this.elements.backgroundTypewriter = document.getElementById('background-typewriter');
        this.elements.paperContainer = document.querySelector('.paper-container');

        // Add click listener to background typewriter
        if (this.elements.backgroundTypewriter) {
            this.elements.backgroundTypewriter.addEventListener('click', () => {
                if (!this.state.storyStarted) {
                    this.startStory();
                }
            });
        }

        // Add keyboard listener for spacebar
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space' && this.state.storyStarted) {
                e.preventDefault();
                this.handleSpacePress();
            }
        });

        // Add click listener for continue
        this.elements.continueIndicator?.addEventListener('click', () => {
            this.handleContinue();
        });

        // Don't load story automatically - wait for typewriter click
    },

    /**
     * Start the story when typewriter is clicked
     */
    async startStory() {
        this.state.storyStarted = true;
        
        // Play story suspense music
        await AudioManager.playEvent('story_suspense');
        
        // Add story-active class to enable dark overlay and show main typewriter
        document.querySelector('.story-screen').classList.add('story-active');
        
        // Hide background typewriter and show paper
        this.elements.backgroundTypewriter.classList.add('clicked');
        setTimeout(() => {
            this.elements.backgroundTypewriter.style.display = 'none';
            this.elements.paperContainer.style.display = 'flex';
            
            // Load the story
            this.loadCurrentStory();
        }, 500);
    },

    /**
     * Load current story state from API
     */
    async loadCurrentStory() {
        try {
            const response = await API.story.getCurrent();
            if (response.success) {
                // Response data is at top level, not nested
                this.displayStory(response);
            }
        } catch (error) {
            console.error('Failed to load story:', error);
            this.showError('Failed to load story. Please try again.');
        }
    },

    /**
     * Display story with typewriter effect
     */
    displayStory(storyData) {
        this.state.currentStoryData = storyData;
        
        // Check for travel trigger BEFORE displaying text
        if (storyData.travel) {
            // Show the travel introduction text first
            let text = storyData.text || storyData.narrative || '';
            if (Array.isArray(text)) {
                text = text.join('\n\n');
            }
            
            this.state.currentText = text;
            this.state.currentIndex = 0;
            this.state.skipTyping = false;
            
            // Clear previous content
            this.elements.storyText.textContent = '';
            this.elements.choices.innerHTML = '';
            this.elements.continueIndicator.style.display = 'none';
            
            // Start typewriter, travel will trigger on completion
            this.startTypewriter();
            return;
        }
        
        // Check for combat trigger BEFORE displaying text
        if (storyData.combat && storyData.combat.enemies) {
            // Show just the combat intro text without the next node
            let text = storyData.text || storyData.narrative || '';
            if (Array.isArray(text)) {
                text = text.join('\n\n');
            }
            
            this.state.currentText = text;
            this.state.currentIndex = 0;
            this.state.skipTyping = false;
            
            // Clear previous content
            this.elements.storyText.textContent = '';
            this.elements.choices.innerHTML = '';
            this.elements.continueIndicator.style.display = 'none';
            
            // Start typewriter, combat will trigger on completion
            this.startTypewriter();
            return;
        }
        
        // Normal story flow
        // Handle text array or string
        let text = storyData.text || storyData.narrative || '';
        if (Array.isArray(text)) {
            text = text.join('\n\n');
        }
        
        this.state.currentText = text;
        this.state.currentIndex = 0;
        this.state.skipTyping = false;

        // Clear previous content
        this.elements.storyText.textContent = '';
        this.elements.choices.innerHTML = '';
        this.elements.continueIndicator.style.display = 'none';

        // Start typewriter effect
        this.startTypewriter();
    },

    /**
     * Typewriter effect
     */
    async startTypewriter() {
        this.state.isTyping = true;
        this.elements.storyText.classList.add('typing');

        // Type each character
        while (this.state.currentIndex < this.state.currentText.length) {
            // Check if user wants to skip
            if (this.state.skipTyping) {
                this.elements.storyText.textContent = this.state.currentText;
                break;
            }

            // Add next character
            const char = this.state.currentText[this.state.currentIndex];
            this.elements.storyText.textContent += char;

            // Play typing sound effect (if available)
            this.playTypeSound();

            // Scroll to bottom as text appears
            this.scrollToBottom();

            // Wait before next character
            await this.sleep(this.state.typeSpeed);

            this.state.currentIndex++;
        }

        // Typing complete
        this.state.isTyping = false;
        this.elements.storyText.classList.remove('typing');
        this.onTypingComplete();
    },

    /**
     * Handle typing completion
     */
    onTypingComplete() {
        const data = this.state.currentStoryData;

        // Check for travel trigger FIRST (before any continue indicators)
        if (data.travel) {
            // Hide continue indicator to prevent user clicking during transition
            this.elements.continueIndicator.style.display = 'none';
            setTimeout(() => {
                this.navigateToTravel();
            }, 1500);
            return;
        }

        // Check for combat trigger
        if (data.combat && data.combat.enemies) {
            setTimeout(() => {
                this.triggerCombat(data.combat);
            }, 1500);
            return;
        }

        // Show choices if available
        if (data.choices && data.choices.length > 0) {
            this.displayChoices(data.choices);
        } 
        // Show continue indicator if no choices and not ending
        else if (!data.is_ending && !data.quit_game) {
            this.showContinueIndicator();
        }
        // Handle game ending
        else if (data.is_ending || data.quit_game) {
            this.handleGameOver(data);
        }
    },

    /**
     * Display story choices
     */
    displayChoices(choices) {
        this.elements.choices.innerHTML = '';

        choices.forEach((choice, index) => {
            const button = document.createElement('button');
            button.className = 'story-choice';
            // Handle both string choices and object choices with label property
            button.textContent = typeof choice === 'string' ? choice : (choice.label || choice.text || choice.choice || '');
            button.addEventListener('click', () => this.makeChoice(index));
            this.elements.choices.appendChild(button);
        });
    },

    /**
     * Make a story choice
     */
    async makeChoice(choiceIndex) {
        try {
            // Disable all choice buttons
            const buttons = this.elements.choices.querySelectorAll('.story-choice');
            buttons.forEach(btn => btn.disabled = true);

            // Make choice via API
            const response = await API.story.makeChoice(choiceIndex);
            
            if (response.success) {
                // Handle special events
                if (response.event) {
                    await this.handleEvent(response.event);
                }

                // Display next story segment
                this.displayStory(response);
            }
        } catch (error) {
            console.error('Failed to make choice:', error);
            this.showError('Failed to process choice. Please try again.');
        }
    },

    /**
     * Handle spacebar press
     */
    handleSpacePress() {
        if (this.state.isTyping) {
            // Skip typing animation
            this.state.skipTyping = true;
        } else if (this.elements.continueIndicator.style.display !== 'none') {
            // Only continue if the continue indicator is showing
            this.handleContinue();
        }
        // If choices are showing, do nothing (user must click a choice)
    },

    /**
     * Handle continue action
     */
    async handleContinue() {
        if (this.state.isTyping) return;

        try {
            this.elements.continueIndicator.style.display = 'none';

            const response = await API.story.continue();
            
            if (response.success) {
                // Handle special events
                if (response.event) {
                    await this.handleEvent(response.event);
                }

                this.displayStory(response);
            }
        } catch (error) {
            console.error('Failed to continue story:', error);
            this.showError('Failed to continue. Please try again.');
        }
    },

    /**
     * Show continue indicator
     */
    showContinueIndicator() {
        this.elements.continueIndicator.style.display = 'flex';
    },

    /**
     * Handle special story events
     */
    async handleEvent(event) {
        switch (event.type) {
            case 'combat':
                // Redirect to combat
                window.location.href = '/combat';
                break;
            case 'travel':
                // Redirect to travel
                window.location.href = '/travel';
                break;
            case 'item_found':
                this.showNotification(`Item found: ${event.item}`);
                break;
            case 'sanity_loss':
                this.showNotification(`Sanity decreased by ${event.amount}`);
                break;
            default:
                console.log('Unknown event:', event);
        }
    },

    /**
     * Navigate to travel screen
     */
    async navigateToTravel() {
        try {
            // Play travel transition sound
            if (AudioManager) {
                await AudioManager.playEvent('location_change');
            }
            
            // Show transition message
            this.showNotification('Opening travel board...');

            // Prevent any further story progression
            this.state.isTyping = true;
            this.elements.continueIndicator.style.display = 'none';
            this.elements.choices.innerHTML = '';

            // Small delay before redirect
            setTimeout(() => {
                window.location.href = '/travel';
            }, 800);
        } catch (error) {
            console.error('Failed to navigate to travel:', error);
            this.state.isTyping = false;
            this.showError('Failed to open travel board: ' + error.message);
        }
    },

    /**
     * Trigger combat encounter
     */
    async triggerCombat(combatData) {
        try {
            // Stop story music
            AudioManager.stopMusic();
            
            // Show transition message
            this.showNotification('Combat initiated!');

            // Prevent any further story progression
            this.state.isTyping = true;
            this.elements.continueIndicator.style.display = 'none';
            this.elements.choices.innerHTML = '';

            // Start combat via API
            const response = await API.combat.start(combatData.enemies);
            
            // Combat API returns combat data directly (no success field)
            if (response && response.player) {
                // Small delay before redirect
                setTimeout(() => {
                    window.location.href = '/combat';
                }, 500);
            } else if (response.error) {
                this.state.isTyping = false;
                this.showError('Failed to start combat: ' + response.error);
            } else {
                this.state.isTyping = false;
                this.showError('Failed to start combat: Unknown error');
            }
        } catch (error) {
            console.error('Failed to trigger combat:', error);
            this.state.isTyping = false;
            this.showError('Failed to start combat: ' + error.message);
        }
    },

    /**
     * Handle game over
     */
    handleGameOver(data) {
        // Add game over choices
        const gameOverChoices = [
            { text: 'Return to Main Menu' },
            { text: 'Try Again' }
        ];

        setTimeout(() => {
            this.displayChoices(gameOverChoices);
        }, 2000);
    },

    /**
     * Play typing sound effect
     */
    playTypeSound() {
        // Use AudioManager for typing sounds
        if (Math.random() < 0.3) { // Only play sound 30% of the time to avoid spam
            AudioManager.play('sfx_type_key');
        }
    },

    /**
     * Scroll paper to bottom
     */
    scrollToBottom() {
        const paperContent = document.querySelector('.paper-content');
        if (paperContent) {
            paperContent.scrollTop = paperContent.scrollHeight;
        }
    },

    /**
     * Show notification
     */
    showNotification(message) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = 'story-notification';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(139, 92, 246, 0.9);
            color: white;
            padding: 15px 30px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            z-index: 1000;
            animation: slideDown 0.3s ease-out;
        `;

        document.body.appendChild(notification);

        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'fadeOut 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    },

    /**
     * Show error message
     */
    showError(message) {
        this.elements.storyText.textContent = `ERROR: ${message}`;
        this.elements.storyText.style.color = '#ef4444';
    },

    /**
     * Sleep utility
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
};

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => StoryScreen.init());
} else {
    StoryScreen.init();
}
