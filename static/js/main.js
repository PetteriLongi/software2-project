/**
 * Application entry point
 * Initializes the game when the page loads
 */

document.addEventListener('DOMContentLoaded', async () => {
    console.log('Rites of Transit - Loading...');
    
    // Initialize audio system first
    await AudioManager.init();
    
    // Play menu ambient music
    await AudioManager.playEvent('travel_airport');
    
    // Initialize the game
    Game.init();
});

// Handle page visibility changes (pause audio when tab is hidden)
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        if (AudioManager.musicPlayer && !AudioManager.musicPlayer.paused) {
            AudioManager.musicPlayer.pause();
        }
    } else {
        if (AudioManager.musicPlayer && AudioManager.currentTrack) {
            AudioManager.musicPlayer.play().catch(err => {
                console.warn('Could not resume audio:', err);
            });
        }
    }
});
