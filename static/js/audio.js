/**
 * Audio management module for GameProjectSoftware2
 * Handles music and sound effects playback with catalog loading from backend
 */

const AudioManager = {
    musicPlayer: null,
    currentTrack: null,
    sfxCache: {},
    catalog: {},
    initialized: false,
    volume: {
        master: 1.0,
        music: 0.12,
        sfx: 0.15,
        ambient: 0.08
    },

    /**
     * Initialize audio system and load catalog from backend
     */
    async init() {
        if (this.initialized) return;

        this.musicPlayer = new Audio();
        this.musicPlayer.volume = this.volume.music * this.volume.master;
        this.musicPlayer.loop = true;

        // Load audio catalog from backend
        try {
            const response = await fetch('/api/audio/catalog');
            const data = await response.json();
            if (data.success) {
                this.catalog = data.catalog;
                console.log('[AudioManager] Loaded', Object.keys(this.catalog).length, 'audio tracks');
            }
        } catch (error) {
            console.error('[AudioManager] Failed to load audio catalog:', error);
        }

        this.initialized = true;
    },

    /**
     * Play audio track by ID (from catalog)
     */
    play(trackId, options = {}) {
        const track = this.catalog[trackId];
        if (!track) {
            console.warn(`[AudioManager] Track not found: ${trackId}`);
            return null;
        }

        const { forceRestart = false } = options;

        // Calculate volume based on category
        const categoryVolume = this.volume[track.category] || 1.0;
        const finalVolume = track.volume * categoryVolume * this.volume.master;

        // Handle music - stop previous track
        if (track.category === 'music' || track.category === 'ambient') {
            if (this.currentTrack === trackId && !this.musicPlayer.paused && !forceRestart) {
                // Same track already playing, just adjust volume
                this.musicPlayer.volume = finalVolume;
                return this.musicPlayer;
            }

            // Fade out and switch tracks
            if (!this.musicPlayer.paused) {
                this.fadeOut(this.musicPlayer, 800);
            }

            setTimeout(() => {
                this.musicPlayer.src = track.url;
                this.musicPlayer.volume = finalVolume;
                this.musicPlayer.loop = track.loop;
                this.currentTrack = trackId;
                
                this.musicPlayer.play().catch(err => {
                    console.warn('[AudioManager] Music playback failed:', err);
                });
            }, 800);

            return this.musicPlayer;
        }

        // Handle sound effects - create new Audio instance
        if (track.category === 'sfx') {
            const sfx = new Audio(track.url);
            sfx.volume = finalVolume;
            sfx.play().catch(err => {
                console.warn('[AudioManager] SFX playback failed:', err);
            });
            return sfx;
        }

        return null;
    },

    /**
     * Play audio for a game event
     */
    async playEvent(eventName) {
        try {
            const response = await fetch(`/api/audio/event/${eventName}`);
            const data = await response.json();
            
            if (data.success && data.audio && data.audio.length > 0) {
                // Play all tracks for this event
                data.audio.forEach(trackData => {
                    // Find track ID from catalog
                    const trackId = Object.keys(this.catalog).find(
                        id => this.catalog[id].url === trackData.url
                    );
                    if (trackId) {
                        this.play(trackId);
                    }
                });
                return true;
            } else {
                console.warn(`[AudioManager] No audio for event: ${eventName}`);
                return false;
            }
        } catch (error) {
            console.error(`[AudioManager] Failed to play event ${eventName}:`, error);
            return false;
        }
    },

    /**
     * Stop music
     */
    stopMusic() {
        if (!this.musicPlayer.paused) {
            this.fadeOut(this.musicPlayer, 800);
            setTimeout(() => {
                this.musicPlayer.pause();
                this.currentTrack = null;
            }, 800);
        }
    },

    /**
     * Stop all audio
     */
    stopAll() {
        this.stopMusic();
        // Clear SFX cache
        Object.values(this.sfxCache).forEach(sfx => {
            try {
                sfx.pause();
            } catch (e) {
                // Ignore errors
            }
        });
    },

    /**
     * Play sound effect (legacy method - uses catalog if available)
     */
    playSFX(sfxName, sfxPath = null) {
        // Try to find in catalog first
        if (this.catalog[sfxName]) {
            return this.play(sfxName);
        }

        // Fallback to legacy path-based method
        if (!sfxPath) {
            console.warn(`[AudioManager] SFX not found in catalog: ${sfxName}`);
            return;
        }

        // Check cache
        if (!this.sfxCache[sfxName]) {
            this.sfxCache[sfxName] = new Audio(sfxPath);
            this.sfxCache[sfxName].volume = this.volume.sfx * this.volume.master;
        }

        const sfx = this.sfxCache[sfxName].cloneNode();
        sfx.volume = this.volume.sfx * this.volume.master;
        sfx.play().catch(err => {
            console.warn('[AudioManager] SFX playback failed:', err);
        });
    },

    /**
     * Fade out audio element
     */
    fadeOut(audioElement, duration) {
        const startVolume = audioElement.volume;
        const steps = 20;
        const stepDuration = duration / steps;
        const volumeStep = startVolume / steps;

        let currentStep = 0;
        const fadeInterval = setInterval(() => {
            currentStep++;
            audioElement.volume = Math.max(0, startVolume - (volumeStep * currentStep));

            if (currentStep >= steps) {
                clearInterval(fadeInterval);
                audioElement.volume = startVolume; // Reset for next use
            }
        }, stepDuration);
    },

    /**
     * Set music volume
     */
    setMusicVolume(volume) {
        this.volume.music = Math.max(0, Math.min(1, volume));
        if (this.musicPlayer) {
            this.musicPlayer.volume = this.volume.music * this.volume.master;
        }
        this.saveSettings();
    },

    /**
     * Set SFX volume
     */
    setSFXVolume(volume) {
        this.volume.sfx = Math.max(0, Math.min(1, volume));
        this.saveSettings();
    },

    /**
     * Set master volume
     */
    setMasterVolume(volume) {
        this.volume.master = Math.max(0, Math.min(1, volume));
        if (this.musicPlayer) {
            const track = this.catalog[this.currentTrack];
            if (track) {
                const categoryVolume = this.volume[track.category] || 1.0;
                this.musicPlayer.volume = track.volume * categoryVolume * this.volume.master;
            }
        }
        this.saveSettings();
    },

    /**
     * Toggle mute
     */
    toggleMute() {
        const wasMuted = this.volume.master === 0;
        if (wasMuted) {
            this.setMasterVolume(this._previousMasterVolume || 1.0);
        } else {
            this._previousMasterVolume = this.volume.master;
            this.setMasterVolume(0);
        }
        return !wasMuted;
    },

    /**
     * Save volume settings to localStorage
     */
    saveSettings() {
        try {
            localStorage.setItem('audioSettings', JSON.stringify(this.volume));
        } catch (e) {
            console.warn('[AudioManager] Failed to save settings:', e);
        }
    },

    /**
     * Load volume settings from localStorage
     */
    loadSettings() {
        try {
            const saved = localStorage.getItem('audioSettings');
            if (saved) {
                const settings = JSON.parse(saved);
                this.volume = { ...this.volume, ...settings };
            }
        } catch (e) {
            console.warn('[AudioManager] Failed to load settings:', e);
        }
    }
};

// Make AudioManager globally accessible
window.AudioManager = AudioManager;

// Auto-initialize on page load (can be skipped if manually initialized)
document.addEventListener('DOMContentLoaded', async () => {
    AudioManager.loadSettings();
    if (!AudioManager.initialized) {
        await AudioManager.init();
    }
});
