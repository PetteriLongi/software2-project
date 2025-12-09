/**
 * Universal Settings UI
 * Provides settings button and modal for volume control
 */

const SettingsUI = {
    modal: null,
    isOpen: false,

    /**
     * Initialize settings UI and inject into page
     */
    init() {
        if (document.getElementById('settings-ui')) return; // Already initialized

        // Create settings button
        const button = document.createElement('button');
        button.className = 'settings-button';
        button.id = 'settings-button';
        button.setAttribute('aria-label', 'Settings');
        button.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                <path d="M19.14,12.94c0.04-0.3,0.06-0.61,0.06-0.94c0-0.32-0.02-0.64-0.07-0.94l2.03-1.58c0.18-0.14,0.23-0.41,0.12-0.61 l-1.92-3.32c-0.12-0.22-0.37-0.29-0.59-0.22l-2.39,0.96c-0.5-0.38-1.03-0.7-1.62-0.94L14.4,2.81c-0.04-0.24-0.24-0.41-0.48-0.41 h-3.84c-0.24,0-0.43,0.17-0.47,0.41L9.25,5.35C8.66,5.59,8.12,5.92,7.63,6.29L5.24,5.33c-0.22-0.08-0.47,0-0.59,0.22L2.74,8.87 C2.62,9.08,2.66,9.34,2.86,9.48l2.03,1.58C4.84,11.36,4.8,11.69,4.8,12s0.02,0.64,0.07,0.94l-2.03,1.58 c-0.18,0.14-0.23,0.41-0.12,0.61l1.92,3.32c0.12,0.22,0.37,0.29,0.59,0.22l2.39-0.96c0.5,0.38,1.03,0.7,1.62,0.94l0.36,2.54 c0.05,0.24,0.24,0.41,0.48,0.41h3.84c0.24,0,0.44-0.17,0.47-0.41l0.36-2.54c0.59-0.24,1.13-0.56,1.62-0.94l2.39,0.96 c0.22,0.08,0.47,0,0.59-0.22l1.92-3.32c0.12-0.22,0.07-0.47-0.12-0.61L19.14,12.94z M12,15.6c-1.98,0-3.6-1.62-3.6-3.6 s1.62-3.6,3.6-3.6s3.6,1.62,3.6,3.6S13.98,15.6,12,15.6z"/>
            </svg>
        `;
        button.onclick = () => this.toggle();

        // Create settings modal
        const modal = document.createElement('div');
        modal.className = 'settings-modal';
        modal.id = 'settings-modal';
        modal.innerHTML = `
            <div class="settings-content">
                <div class="settings-header">
                    <div class="settings-title">⚙ Settings</div>
                    <button class="settings-close" id="settings-close" aria-label="Close">×</button>
                </div>
                
                <div class="volume-control">
                    <div class="volume-label">
                        <span>🎵 Music Volume</span>
                        <span class="volume-value" id="music-volume-value">50%</span>
                    </div>
                    <input type="range" min="0" max="100" value="50" class="volume-slider" id="music-volume-slider">
                </div>
                
                <div class="volume-control">
                    <div class="volume-label">
                        <span>🔊 SFX Volume</span>
                        <span class="volume-value" id="sfx-volume-value">50%</span>
                    </div>
                    <input type="range" min="0" max="100" value="50" class="volume-slider" id="sfx-volume-slider">
                </div>
                
                <div class="settings-footer">
                    Changes are saved automatically
                </div>
            </div>
        `;

        // Add to page
        document.body.appendChild(button);
        document.body.appendChild(modal);
        this.modal = modal;

        // Setup event listeners
        this.setupEventListeners();

        // Load current volumes
        this.updateDisplayValues();
    },

    /**
     * Setup all event listeners
     */
    setupEventListeners() {
        // Close button
        document.getElementById('settings-close').onclick = () => this.close();

        // Click outside to close
        this.modal.onclick = (e) => {
            if (e.target === this.modal) {
                this.close();
            }
        };

        // Music volume slider
        const musicSlider = document.getElementById('music-volume-slider');
        musicSlider.addEventListener('input', (e) => {
            const value = parseInt(e.target.value) / 100;
            AudioManager.setMusicVolume(value);
            this.updateDisplayValues();
        });

        // SFX volume slider
        const sfxSlider = document.getElementById('sfx-volume-slider');
        sfxSlider.addEventListener('input', (e) => {
            const value = parseInt(e.target.value) / 100;
            AudioManager.setSFXVolume(value);
            this.updateDisplayValues();
            
            // Play test sound on change
            if (AudioManager.catalog['ui_click']) {
                AudioManager.playEvent('ui_click');
            }
        });

        // ESC key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });
    },

    /**
     * Update display values from AudioManager
     */
    updateDisplayValues() {
        const musicPercent = Math.round(AudioManager.volume.music * 100);
        const sfxPercent = Math.round(AudioManager.volume.sfx * 100);

        document.getElementById('music-volume-value').textContent = `${musicPercent}%`;
        document.getElementById('sfx-volume-value').textContent = `${sfxPercent}%`;
        
        document.getElementById('music-volume-slider').value = musicPercent;
        document.getElementById('sfx-volume-slider').value = sfxPercent;

        // Update slider progress visual (CSS variable)
        document.getElementById('music-volume-slider').style.setProperty('--value', `${musicPercent}%`);
        document.getElementById('sfx-volume-slider').style.setProperty('--value', `${sfxPercent}%`);
    },

    /**
     * Open settings modal
     */
    open() {
        this.modal.classList.add('active');
        this.isOpen = true;
        this.updateDisplayValues();
    },

    /**
     * Close settings modal
     */
    close() {
        this.modal.classList.remove('active');
        this.isOpen = false;
    },

    /**
     * Toggle settings modal
     */
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }
};

// Initialize settings UI when audio manager is ready
document.addEventListener('DOMContentLoaded', () => {
    // Wait for AudioManager to initialize and load settings
    const initSettings = () => {
        if (AudioManager.initialized) {
            SettingsUI.init();
            
            // Force apply the loaded volumes
            AudioManager.setMusicVolume(AudioManager.volume.music);
            AudioManager.setSFXVolume(AudioManager.volume.sfx);
        } else {
            // Wait a bit longer if AudioManager isn't ready
            setTimeout(initSettings, 50);
        }
    };
    
    setTimeout(initSettings, 100);
});
