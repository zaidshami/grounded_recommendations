// UI functions for Gemini Agent Tester

// Display recommendations in the grid
function displayRecommendations(recommendations) {
    const gridElement = document.getElementById('recommendations-grid');
    
    if (recommendations.length === 0) {
        gridElement.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: #666;">No recommendations found</p>';
        return;
    }
    
    // Debug logging to help troubleshoot distance issues
    console.log('Raw recommendations data:', recommendations);
    recommendations.forEach((rec, index) => {
        console.log(`Recommendation ${index + 1}:`, {
            name: rec.name,
            distance: rec.distance,
            walking_duration: rec.walking_duration,
            distance_status: rec.distance_status,
            address: rec.address
        });
    });

    gridElement.innerHTML = recommendations.map(rec => {
        return `
            <div class="recommendation-card">
                <div class="image-container">
                    ${rec.image_url ? 
                        `<img src="${rec.image_url}" alt="${rec.name}" class="recommendation-image" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" />
                         <div class="no-image" style="display: none;">${rec.name}</div>` :
                        `<div class="no-image">${rec.name}</div>`
                    }
                </div>
                <h4>${rec.name || 'Unknown'}</h4>
                <p><strong>Type:</strong> ${rec.type || 'N/A'}</p>
                <p><strong>Category:</strong> ${rec.category || 'N/A'}</p>
                <p><strong>Description:</strong> ${rec.description || 'No description available'}</p>
                ${rec.rating ? `<p class="rating">Rating: ${rec.rating}/5</p>` : ''}
                ${rec.address ? `<p><strong>Address:</strong> ${rec.address}</p>` : ''}
                ${rec.personalization_reason ? `<p><strong>Why Recommended:</strong> ${rec.personalization_reason}</p>` : ''}
                ${rec.distance && rec.walking_duration ? 
                    `<p class="distance">${rec.distance} • 🚶 ${rec.walking_duration} walk from hotel</p>` : 
                    rec.distance_status ? 
                        `<p class="distance-status" style="color: #dc3545; font-style: italic; background: #f8d7da; padding: 8px 12px; border-radius: 6px; border-left: 3px solid #dc3545; margin: 10px 0; display: inline-block; font-size: 13px;">⚠️ ${rec.distance_status}</p>` : 
                        ''
                }
            </div>
        `;
    }).join('');
}

// Chat conversation management
function addToHistory() {
    const message = document.getElementById('chat-message').value.trim();
    if (!message) {
        alert('Please enter a message first');
        return;
    }

    // Add message to conversation history without sending to API
    const messageObj = {
        message_id: `msg_${Date.now()}`,
        role: 'user',
        content: message,
        timestamp: new Date().toISOString(),
        metadata: { reservation_id: document.getElementById('shared-reservation-id').value }
    };

    conversationHistory.push(messageObj);
    
    // Display the message in conversation history
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user';
    messageDiv.innerHTML = `
        <div class="sender">User</div>
        <div class="content">${message}</div>
        <div class="timestamp">${new Date().toLocaleString()}</div>
    `;
    
    const container = document.getElementById('conversation-history');
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
    
    // Clear input
    document.getElementById('chat-message').value = '';
    
    console.log('Message added to history:', messageObj);
    console.log('Current conversation history:', conversationHistory);
}

function updateConversationHistory() {
    const container = document.getElementById('conversation-history');
    container.innerHTML = '';

    conversationHistory.forEach(msg => {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${msg.role}`;
        messageDiv.innerHTML = `
            <div class="sender">${msg.role === 'user' ? 'User' : 'Assistant'}</div>
            <div class="content">${msg.content}</div>
            <div class="timestamp">${new Date(msg.timestamp).toLocaleString()}</div>
        `;
        container.appendChild(messageDiv);
    });

    container.scrollTop = container.scrollHeight;
}

function clearHistory() {
    conversationHistory = [];
    updateConversationHistory();
}
