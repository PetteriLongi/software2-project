/**
 * travel.js - Travel system UI controller
 * 
 * Handles airport selection, travel actions, and travel board display.
 */

/**
 * LeafletMapManager - Handles map visualization using Leaflet.js and OpenStreetMap
 * 
 * Manages airport placement on an interactive map and animates plane movements.
 */
class LeafletMapManager {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.map = null;
        this.markers = {};
        this.plane = null;
        this.routeLine = null;
        this.planeAnimId = null;
        this.isFlying = false;
        
        this.initMap();
    }

    initMap() {
        // Initialize Leaflet map centered on Europe
        this.map = L.map(this.container, {
            center: [20, 20],
            zoom: 3,
            zoomControl: true,
            scrollWheelZoom: true,
            attributionControl: true
        });

        // Add OpenStreetMap tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(this.map);

        console.log('LeafletMapManager initialized');
    }

    /**
     * Add airports to the map
     * @param {Array} airports - Array of airport objects with IATA codes and lat/lon
     * @param {String} currentIata - IATA code of current location
     */
    addAirports(airports, currentIata) {
        console.log('Adding airports to map:', {
            count: airports.length,
            current: currentIata,
            airports: airports.map(a => a.iata)
        });

        // Clear existing markers
        Object.values(this.markers).forEach(marker => {
            this.map.removeLayer(marker);
        });
        this.markers = {};

        // Add markers for each airport
        airports.forEach((airport) => {
            if (!airport.lat || !airport.lon) {
                console.warn(`No coordinates for airport ${airport.iata}`);
                return;
            }

            const isCurrent = airport.iata === currentIata;
            
            // Create custom icon
            const iconColor = isCurrent ? '#00ff00' : '#00ffff';
            const iconSize = isCurrent ? 24 : 14;

            const customIcon = L.divIcon({
                html: `<div style="
                    width: ${iconSize}px;
                    height: ${iconSize}px;
                    background: ${iconColor};
                    border-radius: 50%;
                    border: 2px solid ${iconColor};
                    box-shadow: 0 0 8px ${iconColor};
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    opacity: ${airport.visited ? 0.6 : 1};
                "></div>`,
                iconSize: [iconSize, iconSize],
                iconAnchor: [iconSize / 2, iconSize / 2],
                popupAnchor: [0, -15]
            });

            const marker = L.marker([airport.lat, airport.lon], {
                icon: customIcon,
                title: `${airport.iata} - ${airport.name}`
            });

            marker.bindPopup(`
                <strong>${airport.iata}</strong><br/>
                ${airport.name}<br/>
                ${airport.country}
            `);

            marker.addTo(this.map);
            
            // Store map position as percentage for animation
            airport._mapPos = {
                lat: airport.lat,
                lon: airport.lon
            };

            this.markers[airport.iata] = marker;

            console.log(`Placed airport ${airport.iata} at (${airport.lat}, ${airport.lon})`);
        });

        // Fit map bounds to show all airports
        if (airports.length > 0) {
            const bounds = L.latLngBounds(
                airports
                    .filter(a => a.lat && a.lon)
                    .map(a => [a.lat, a.lon])
            );
            this.map.fitBounds(bounds, { padding: [50, 50], maxZoom: 5 });
        }
    }

    /**
     * Animate plane movement from source to destination airport
     * @param {Object} fromAirport - Source airport with lat/lon
     * @param {Object} toAirport - Destination airport with lat/lon
     * @param {Function} onComplete - Callback when animation completes
     */
    animateFlight(fromAirport, toAirport, onComplete = null) {
        if (this.isFlying) {
            console.log('Already flying, ignoring flight request');
            return;
        }
        if (!fromAirport._mapPos || !toAirport._mapPos) {
            console.error('Airport positions not set', { 
                from: fromAirport.iata, 
                to: toAirport.iata
            });
            return;
        }

        console.log('Starting flight animation:', {
            from: fromAirport.iata,
            to: toAirport.iata
        });

        this.isFlying = true;

        // Draw route line
        const routeLatLngs = [
            [fromAirport._mapPos.lat, fromAirport._mapPos.lon],
            [toAirport._mapPos.lat, toAirport._mapPos.lon]
        ];

        if (this.routeLine) {
            this.map.removeLayer(this.routeLine);
        }

        this.routeLine = L.polyline(routeLatLngs, {
            color: '#1e90ff',
            weight: 3,
            opacity: 0.8,
            dashArray: '10, 6'
        }).addTo(this.map);

        // Create plane marker - using canvas for proper rotation
        if (this.plane) {
            this.map.removeLayer(this.plane);
        }

        // Helper function to create rotated plane icon using SVG
        const createPlaneIcon = (angle) => {
            const svg = `
                <svg width="32" height="32" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
                    <g transform="translate(16,16) rotate(${angle}) translate(-16,-16)">
                        <text x="16" y="24" font-size="28" fill="#1e90ff" text-anchor="middle" font-weight="bold">✈</text>
                    </g>
                </svg>
            `;
            
            const svgBlob = new Blob([svg], { type: 'image/svg+xml' });
            const url = URL.createObjectURL(svgBlob);
            
            return L.icon({
                iconUrl: url,
                iconSize: [32, 32],
                iconAnchor: [16, 16],
                popupAnchor: [0, -16]
            });
        };

        this.plane = L.marker([fromAirport._mapPos.lat, fromAirport._mapPos.lon], {
            icon: createPlaneIcon(0)
        }).addTo(this.map);

        // Animate plane along route using screen-space interpolation for accurate heading
        const duration = 1600;
        const startTime = performance.now();
        let frameCount = 0;

        const from = fromAirport._mapPos;
        const to = toAirport._mapPos;

        // Project lat/lon to map layer points so rotation follows the drawn line
        const fromPt = this.map.latLngToLayerPoint([from.lat, from.lon]);
        const toPt = this.map.latLngToLayerPoint([to.lat, to.lon]);
        const dx = toPt.x - fromPt.x;
        const dy = toPt.y - fromPt.y;

        const step = (now) => {
            frameCount++;
            const elapsed = now - startTime;
            const t = Math.min(1, elapsed / duration);

            // Linear interpolation in screen space, then convert back to lat/lon
            const currentX = fromPt.x + dx * t;
            const currentY = fromPt.y + dy * t;
            const currentLatLng = this.map.layerPointToLatLng([currentX, currentY]);

            // Heading based on screen-space delta (y increases downward in Leaflet)
            let angle = Math.atan2(dy, dx) * 180 / Math.PI;
            angle = (angle + 360) % 360;

            // Update plane position and rotation
            this.plane.setLatLng(currentLatLng);
            this.plane.setIcon(createPlaneIcon(angle));

            if (frameCount % 10 === 0) {
                console.log(`Animation frame ${frameCount}, t=${t.toFixed(3)}, angle=${angle.toFixed(1)}`);
            }

            if (t < 1) {
                this.planeAnimId = requestAnimationFrame(step);
            } else {
                console.log('Animation complete');
                this.map.removeLayer(this.plane);
                this.map.removeLayer(this.routeLine);
                this.plane = null;
                this.routeLine = null;
                this.isFlying = false;
                if (onComplete) onComplete();
            }
        };

        this.planeAnimId = requestAnimationFrame(step);
    }

    /**
     * Update current location highlight on map
     */
    updateCurrentLocation(currentIata) {
        // Leaflet will handle this when we redraw airports
    }
}

class TravelManager {
    constructor() {
        this.selectedAirportIndex = null;
        this.destinations = [];
        this.currentLocation = null;
        this.markka = 0;
        this.conduitData = { found: 0, closed: 0 };
        
        this.initElements();
        this.initEventListeners();
        
        // Initialize map manager using Leaflet
        this.mapManager = new LeafletMapManager('leafletMap');
    }

    initElements() {
        // UI Elements
        this.currentLocationName = document.getElementById('currentLocationName');
        this.currentLocationIata = document.getElementById('currentLocationIata');
        this.markkaDisplay = document.getElementById('markkaDisplay');
        this.hpDisplay = document.getElementById('hpDisplay');
        this.sanityDisplay = document.getElementById('sanityDisplay');
        this.travelDoomValue = document.getElementById('travelDoomValue');
        this.conduitProgress = document.getElementById('conduitProgress');
        this.messageBox = document.getElementById('messageBox');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        this.destinationsTable = document.getElementById('destinationsTable');
        this.destinationsBody = document.getElementById('destinationsBody');
        
        // Buttons
        this.travelButton = document.getElementById('travelButton');
        this.restButton = document.getElementById('restButton');
        this.closeConduitButton = document.getElementById('closeConduitButton');
    }

    initEventListeners() {
        this.travelButton.addEventListener('click', () => this.handleTravel());
        this.restButton.addEventListener('click', () => this.handleRest());
        this.closeConduitButton.addEventListener('click', () => this.handleCloseConduit());
    }

    async init() {
        console.log('Initializing travel manager...');
        
        // Initialize audio if available
        if (window.AudioManager) {
            await AudioManager.playEvent('menu_open');
        }
        
        // Load player data
        await this.loadPlayerData();
        
        // Load destinations
        await this.loadDestinations();
    }

    async loadPlayerData() {
        try {
            const response = await API.game.getState();
            if (response.success && response.player) {
                this.updatePlayerDisplay(response.player);
            }
        } catch (error) {
            console.error('Failed to load player data:', error);
        }
    }

    async loadDestinations() {
        try {
            this.showLoading(true);
            
            const response = await API.travel.getDestinations();
            
            if (response.success) {
                this.currentLocation = response.current_location;
                this.markka = response.markka;
                this.destinations = response.destinations;
                this.conduitData = {
                    found: response.conduits_found,
                    closed: response.conduits_closed
                };
                
                // Store doom clock if present
                if (response.doom_clock) {
                    this.doomClock = response.doom_clock;
                }
                
                this.renderDestinations();
                this.updateLocationDisplay();
                this.updateConduitProgress();
                this.updateDoomDisplay();
                this.checkCurrentLocationConduit();
                
                // Update map with airports
                this.updateMap();
            } else {
                this.showMessage('Failed to load destinations', 'error');
            }
            
            this.showLoading(false);
        } catch (error) {
            console.error('Error loading destinations:', error);
            this.showMessage('Error connecting to server', 'error');
            this.showLoading(false);
        }
    }

    /**
     * Update map with current airports and current location
     */
    updateMap() {
        // Create airport data array including the current location
        const airportsData = this.destinations.map(dest => dest.airport);
        
        // Add current location to the airports if not already in the list
        const currentLocationExists = airportsData.some(a => a.iata === this.currentLocation.iata);
        if (!currentLocationExists) {
            airportsData.unshift({
                iata: this.currentLocation.iata,
                name: this.currentLocation.name,
                country: this.currentLocation.country,
                lat: this.currentLocation.lat,
                lon: this.currentLocation.lon,
                visited: true
            });
        }

        this.mapManager.addAirports(airportsData, this.currentLocation.iata);
        
        // Store map positions back in destinations for animation reference
        this.destinations.forEach(dest => {
            const airport = airportsData.find(a => a.iata === dest.airport.iata);
            if (airport && airport._mapPos) {
                dest.airport._mapPos = airport._mapPos;
            }
        });
    }

    renderDestinations() {
        this.destinationsBody.innerHTML = '';
        
        this.destinations.forEach((dest, index) => {
            const row = document.createElement('tr');
            row.className = 'destination-row';
            row.dataset.index = index;
            
            const airport = dest.airport;
            
            // Add status classes
            if (airport.visited) row.classList.add('visited');
            if (airport.conduit && airport.entered_terminal) row.classList.add('conduit-found');
            if (airport.conduit_closed) row.classList.add('conduit-closed');
            
            // Status indicator
            let statusIcon = '';
            if (airport.conduit_closed) {
                statusIcon = '<span class="conduit-indicator conduit-closed">⊗ Sealed</span>';
            } else if (airport.conduit && airport.entered_terminal) {
                statusIcon = '<span class="conduit-indicator conduit-open">⚠ Conduit!</span>';
            } else if (airport.visited) {
                statusIcon = '<span style="color: #aaa;">✓ Visited</span>';
            } else {
                statusIcon = '<span style="color: #666;">—</span>';
            }
            
            row.innerHTML = `
                <td>
                    <div class="airport-name">${airport.name}</div>
                    <div class="airport-iata">${airport.iata}</div>
                </td>
                <td>${airport.country}</td>
                <td class="distance">${dest.distance.toFixed(0)} km</td>
                <td class="cost">₥${dest.cost.toLocaleString()}</td>
                <td>${statusIcon}</td>
            `;
            
            row.addEventListener('click', () => this.selectAirport(index));
            
            this.destinationsBody.appendChild(row);
        });
        
        this.destinationsTable.style.display = 'table';
    }

    selectAirport(index) {
        // Remove previous selection
        const rows = this.destinationsBody.querySelectorAll('.destination-row');
        rows.forEach(r => r.classList.remove('selected'));
        
        // Select new airport
        this.selectedAirportIndex = index;
        rows[index].classList.add('selected');
        
        // Update button states
        this.updateButtons();
    }

    updateButtons() {
        const selected = this.destinations[this.selectedAirportIndex];
        
        // Travel button - enabled if airport selected and player can afford it
        if (selected) {
            const canAfford = this.markka >= selected.cost;
            this.travelButton.disabled = !canAfford;
            
            // Check if current location has an open conduit
            const currentAirport = this.destinations.find(d => 
                d.airport.iata === this.currentLocation.iata
            );
            
            if (currentAirport) {
                const hasOpenConduit = currentAirport.airport.conduit && 
                                     currentAirport.airport.entered_terminal && 
                                     !currentAirport.airport.conduit_closed;
                this.closeConduitButton.disabled = !hasOpenConduit;
            } else {
                this.closeConduitButton.disabled = true;
            }
        } else {
            this.travelButton.disabled = true;
            this.closeConduitButton.disabled = true;
        }
    }

    async handleTravel() {
        if (this.selectedAirportIndex === null) return;
        
        const selected = this.destinations[this.selectedAirportIndex];
        const airport = selected.airport;
        
        console.log('handleTravel called for:', airport.iata);
        
        try {
            this.travelButton.disabled = true;
            
            // Play travel sound
            if (window.AudioManager) {
                await AudioManager.playEvent('location_change');
            }

            // Find current airport in destinations for animation
            let currentAirport = this.destinations.find(d => 
                d.airport.iata === this.currentLocation.iata
            );
            
            // If current location not in destinations, create an airport object from currentLocation
            if (!currentAirport) {
                console.log('Current location not in destinations, creating airport object from currentLocation');
                currentAirport = {
                    airport: {
                        iata: this.currentLocation.iata,
                        name: this.currentLocation.name,
                        country: this.currentLocation.country,
                        lat: this.currentLocation.lat,
                        lon: this.currentLocation.lon,
                        _mapPos: {
                            lat: this.currentLocation.lat,
                            lon: this.currentLocation.lon
                        }
                    }
                };
            }
            
            console.log('Current location:', this.currentLocation.iata);
            console.log('Current airport data:', currentAirport);
            console.log('Selected airport data:', selected);
            
            // Check if we have map positions before calling API
            const hasMapPositions = currentAirport && currentAirport.airport._mapPos && selected.airport._mapPos;
            
            console.log('Has map positions:', hasMapPositions);
            console.log('Current map pos:', currentAirport?.airport._mapPos);
            console.log('Selected map pos:', selected.airport._mapPos);
            
            // Make API call to travel FIRST
            const response = await API.travel.travelTo(this.selectedAirportIndex);
            
            console.log('Travel API response:', response);
            
            if (response.success) {
                // NOW animate the plane after the API call succeeds
                if (hasMapPositions) {
                    console.log('Starting flight animation...');
                    // Create a promise that resolves when animation is complete
                    await new Promise((resolve) => {
                        this.mapManager.animateFlight(
                            currentAirport.airport,
                            selected.airport,
                            () => {
                                console.log('Flight animation callback triggered');
                                resolve();
                            }
                        );
                    });
                    console.log('Animation complete');
                } else {
                    console.log('Skipping animation - no map positions available');
                }

                // Show travel message
                let message = response.message;
                if (response.conduit_found) {
                    message += ' 🌀 You sense a conduit nearby!';
                }
                this.showMessage(message, 'success');

                // Update location
                this.currentLocation = response.current_location;
                this.updateLocationDisplay();
                
                // Update doom clock if present
                if (response.doom_clock) {
                    this.doomClock = response.doom_clock;
                    this.updateDoomDisplay();
                }
                
                // Check for game over
                if (response.game_over) {
                    this.showMessage('💀 The doom reached zero! The world ends!', 'error');
                    this.travelButton.disabled = true;
                    this.restButton.disabled = true;
                    this.closeConduitButton.disabled = true;
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 3000);
                    return;
                }

                // Reload destinations to update visited status and map
                console.log('Reloading destinations...');
                await this.loadDestinations();

                // Play conduit discovery sound if found
                if (response.conduit_found && window.AudioManager) {
                    await AudioManager.playEvent('conduit_discovered');
                }
            } else {
                this.showMessage(response.error || response.message, 'error');
                this.travelButton.disabled = false;
            }
        } catch (error) {
            console.error('Travel error:', error);
            this.showMessage('Failed to travel', 'error');
            this.travelButton.disabled = false;
        }
    }

    async handleRest() {
        try {
            this.restButton.disabled = true;
            
            // Play rest sound
            if (window.AudioManager) {
                await AudioManager.playEvent('rest_start');
            }
            
            const response = await API.travel.rest();
            
            if (response.success) {
                this.showMessage(response.message, 'success');
                
                // Update player stats
                this.updatePlayerDisplay({
                    hp: response.hp,
                    sanity: response.sanity
                });
                
                // Update doom clock if present
                if (response.doom_clock) {
                    this.doomClock = response.doom_clock;
                    this.updateDoomDisplay();
                }
                
                // Check for game over
                if (response.game_over) {
                    this.showMessage('💀 The doom reached zero! The world ends!', 'error');
                    this.travelButton.disabled = true;
                    this.restButton.disabled = true;
                    this.closeConduitButton.disabled = true;
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 3000);
                    return;
                }
            } else {
                this.showMessage(response.error || 'Failed to rest', 'error');
            }
            
            this.restButton.disabled = false;
        } catch (error) {
            console.error('Rest error:', error);
            this.showMessage('Failed to rest', 'error');
            this.restButton.disabled = false;
        }
    }

    async handleCloseConduit() {
        if (this.selectedAirportIndex === null) return;
        
        try {
            this.closeConduitButton.disabled = true;
            
            // Play conduit close sound
            if (window.AudioManager) {
                await AudioManager.playEvent('conduit_closed');
            }
            
            const response = await API.travel.closeConduit(this.selectedAirportIndex);
            
            if (response.success) {
                this.showMessage(response.message, 'success');
                
                // Update markka and conduit progress
                this.markka = response.markka;
                this.conduitData.closed = response.conduits_closed;
                
                this.markkaDisplay.textContent = this.markka.toLocaleString();
                this.updateConduitProgress();
                
                // If story is available, wait a moment then transition to story
                if (response.story) {
                    console.log('Conduit closed, transitioning to story node:', response.story.node_key);
                    await new Promise(resolve => setTimeout(resolve, 1000)); // 1 second delay for dramatic effect
                    window.location.href = '/story';
                } else {
                    // Reload destinations to update conduit status
                    await this.loadDestinations();
                }
            } else {
                this.showMessage(response.error || response.message, 'error');
                this.closeConduitButton.disabled = false;
            }
        } catch (error) {
            console.error('Conduit close error:', error);
            this.showMessage('Failed to close conduit', 'error');
            this.closeConduitButton.disabled = false;
        }
    }



    updateLocationDisplay() {
        if (this.currentLocation) {
            this.currentLocationName.textContent = this.currentLocation.name;
            this.currentLocationIata.textContent = `(${this.currentLocation.iata}) ${this.currentLocation.country}`;
        }
        this.markkaDisplay.textContent = this.markka.toLocaleString();
    }

    checkCurrentLocationConduit() {
        // Check if the current location has an open conduit and enable button if so
        const currentAirport = this.destinations.find(d => 
            d.airport.iata === this.currentLocation.iata
        );
        
        if (currentAirport) {
            const hasOpenConduit = currentAirport.airport.conduit && 
                                 currentAirport.airport.entered_terminal && 
                                 !currentAirport.airport.conduit_closed;
            this.closeConduitButton.disabled = !hasOpenConduit;
        } else {
            this.closeConduitButton.disabled = true;
        }
    }

    updatePlayerDisplay(player) {
        if (player.hp !== undefined) {
            this.hpDisplay.textContent = player.hp;
        }
        if (player.sanity !== undefined) {
            this.sanityDisplay.textContent = player.sanity;
        }
    }

    updateConduitProgress() {
        // Show closed out of total conduits (5)
        const totalConduits = 5;
        this.conduitProgress.textContent = 
            `Conduits: ${this.conduitData.closed}/${totalConduits} Sealed`;
    }

    updateDoomDisplay() {
        if (this.doomClock && this.travelDoomValue) {
            const ticks = this.doomClock.ticks;
            const start = this.doomClock.start;
            const percentage = this.doomClock.percentage || ((ticks / start) * 100);
            
            // Update text
            this.travelDoomValue.textContent = `${ticks}/${start}`;
            
            // Change color based on doom level
            if (percentage <= 25) {
                this.travelDoomValue.style.color = '#ff0000';  // Red - critical
            } else if (percentage <= 50) {
                this.travelDoomValue.style.color = '#ff6b6b';  // Light red - danger
            } else if (percentage <= 75) {
                this.travelDoomValue.style.color = '#ffaa00';  // Orange - warning
            } else {
                this.travelDoomValue.style.color = '#00ff00';  // Green - safe
            }
        }
    }

    showMessage(text, type = 'info') {
        this.messageBox.textContent = text;
        this.messageBox.className = `message-box ${type}`;
        this.messageBox.style.display = 'block';
        
        setTimeout(() => {
            this.messageBox.style.display = 'none';
        }, 5000);
    }

    showLoading(show) {
        this.loadingIndicator.style.display = show ? 'block' : 'none';
        this.destinationsTable.style.display = show ? 'none' : 'table';
    }
}

// Initialize when page loads
let travelManager;

// DOMContentLoaded listener removed - now handled in travel.html
