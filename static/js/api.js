/**
 * API communication module
 * Handles all HTTP requests to the Flask backend
 */

const API = {
    BASE_URL: window.location.origin,

    /**
     * Generic fetch wrapper with error handling
     */
    async request(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.BASE_URL}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    // Game endpoints
    game: {
        start: () => API.request('/api/game/start', { 
            method: 'POST',
            body: JSON.stringify({})
        }),
        getState: () => API.request('/api/game/state'),
        save: () => API.request('/api/game/save', { method: 'POST' }),
        load: (saveData) => API.request('/api/game/load', {
            method: 'POST',
            body: JSON.stringify(saveData)
        })
    },

    // Combat endpoints
    combat: {
        start: (enemies) => API.request('/api/combat/start', {
            method: 'POST',
            body: JSON.stringify({ enemy_types: enemies })
        }),
        action: (actionData) => API.request('/api/combat/action', {
            method: 'POST',
            body: JSON.stringify(actionData)
        }),
        getState: () => API.request('/api/combat/state')
    },

    // Travel endpoints
    travel: {
        getDestinations: () => API.request('/api/travel/destinations'),
        travelTo: (airportIndex) => API.request('/api/travel/to', {
            method: 'POST',
            body: JSON.stringify({ airport_index: airportIndex })
        }),
        rest: () => API.request('/api/travel/rest', { method: 'POST' }),
        closeConduit: (airportIndex) => API.request('/api/travel/conduit/close', {
            method: 'POST',
            body: JSON.stringify({ airport_index: airportIndex })
        })
    },

    // Inventory endpoints
    inventory: {
        get: () => API.request('/api/inventory'),
        use: (itemIndex) => API.request('/api/inventory/use', {
            method: 'POST',
            body: JSON.stringify({ item_index: itemIndex })
        }),
        equip: (itemIndex) => API.request('/api/inventory/equip', {
            method: 'POST',
            body: JSON.stringify({ item_index: itemIndex })
        }),
        unequip: () => API.request('/api/inventory/unequip', { method: 'POST' }),
        reload: () => API.request('/api/inventory/reload', { method: 'POST' })
    },

    // Story endpoints
    story: {
        getCurrent: () => API.request('/api/story/current'),
        makeChoice: (choiceIndex) => API.request('/api/story/choice', {
            method: 'POST',
            body: JSON.stringify({ choice_index: choiceIndex })
        }),
        continue: () => API.request('/api/story/continue', { method: 'POST' }),
        getNode: (nodeKey) => API.request(`/api/story/node/${nodeKey}`),
        listChapters: () => API.request('/api/story/chapters')
    }
};
