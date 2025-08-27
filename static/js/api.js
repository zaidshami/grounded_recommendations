// API functions for Gemini Agent Tester

// Fetch reservation data from external API
async function fetchReservationData() {
    const reservationId = document.getElementById('shared-reservation-id').value.trim();
    if (!reservationId) {
        alert('Please enter a reservation ID');
        return;
    }

    const guestInfoArea = document.getElementById('guest-info');
    const guestInfoContent = document.getElementById('guest-info-content');

    guestInfoArea.style.display = 'block';
    
    // Show loading state directly in guest info content
    guestInfoContent.innerHTML = `
        <div style="text-align: center; padding: 40px;">
            <div class="loading-spinner" style="width: 50px; height: 50px; border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 20px;"></div>
            <p style="color: #666; font-size: 16px; margin: 0;">Fetching reservation and conversation data...</p>
            <p style="color: #999; font-size: 14px; margin: 10px 0 0 0;">Analyzing guest preferences and generating insights...</p>
        </div>
    `;

    try {
        const url = `${RESERVATION_API}?reservation_id=${reservationId}&secret=agentsecretnjzd7f89asa878d97asd&customPromptFieldType=static&returnDataOnly=true&truncateData=false&returnFields=reservation-info,comments-info&aiPromptType=summary&textformat=JSON`;
        
        const response = await fetch(url);
        const data = await response.json();

        if (response.ok) {
            // Store the data globally
            reservationData = data;
            
            // Show success message in guest info area
            const successMessage = `
                <div style="background: #d4edda; padding: 15px; border-radius: 8px; margin: 10px 0; border: 1px solid #c3e6cb;">
                    <h4 style="margin: 0 0 10px 0; color: #155724;"> Success</h4>
                    <p style="margin: 5px 0; color: #155724;">Reservation data fetched successfully! Now available for both Direct Recommendations and Chat Interface.</p>
                </div>
            `;
            
            // Analyze and display guest information
            const guestSummary = analyzeGuestData(data);
            guestInfoContent.innerHTML = successMessage + guestSummary;
            
        } else {
            guestInfoContent.innerHTML = `
                <div style="background: #f8d7da; padding: 15px; border-radius: 8px; margin: 10px 0; border: 1px solid #f5c6cb;">
                    <h4 style="margin: 0 0 10px 0; color: #721c24;"> Error</h4>
                    <p style="margin: 5px 0; color: #721c24;">Error: ${data.detail || 'Unknown error'}</p>
                </div>
            `;
        }
    } catch (error) {
        guestInfoContent.innerHTML = `
            <div style="background: #f8d7da; padding: 15px; border-radius: 8px; margin: 10px 0; border: 1px solid #f5c6cb;">
                <h4 style="margin: 0 0 10px 0; color: #721c24;"> Network Error</h4>
                <p style="margin: 5px 0; color: #721c24;">Network error: ${error.message}</p>
            </div>
        `;
    }
}

// Generate recommendations using our API
async function generateRecommendations() {
    if (!reservationData) {
        alert('Please fetch reservation data first');
        return;
    }

    const maxRecommendations = parseInt(document.getElementById('rec-max-recommendations').value);
    const categories = document.getElementById('rec-categories').value.trim();
    const radius = parseFloat(document.getElementById('rec-radius').value);

    const responseArea = document.getElementById('rec-response');
    const statusElement = document.getElementById('rec-status');
    const contentElement = document.getElementById('rec-content');
    const gridElement = document.getElementById('recommendations-grid');

    responseArea.style.display = 'block';
    showStatus('rec-status', 'Generating recommendations...', 'loading');
    
    // Show loading indicator in the grid
    gridElement.innerHTML = `
        <div style="grid-column: 1/-1; text-align: center; padding: 40px;">
            <div class="loading-spinner" style="width: 50px; height: 50px; border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 20px;"></div>
            <p style="color: #666; font-size: 16px; margin: 0;">Calculating personalized recommendations...</p>
            <p style="color: #999; font-size: 14px; margin: 10px 0 0 0;">This may take a few moments as we analyze your preferences and calculate distances.</p>
        </div>
    `;

    try {
        const response = await fetch(`${API_BASE}/recommendations/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                reservation_id: document.getElementById('shared-reservation-id').value,
                preferences: null,
                max_recommendations: maxRecommendations,
                categories: categories ? categories.split(',').map(c => c.trim()) : null,
                radius_miles: radius
            })
        });

        const data = await response.json();

        if (response.ok) {
            showStatus('rec-status', 'Recommendations generated successfully!', 'success');
            
            // Display recommendations in grid
            displayRecommendations(data.recommendations || []);
        } else {
            showStatus('rec-status', `Error: ${data.detail || 'Unknown error'}`, 'error');
            gridElement.innerHTML = '';
        }
    } catch (error) {
        showStatus('rec-status', `Network error: ${error.message}`, 'error');
        gridElement.innerHTML = '';
    }
}

// Send chat message to API
async function sendMessage() {
    const message = document.getElementById('chat-message').value.trim();
    if (!message) {
        alert('Please enter a message first');
        return;
    }

    if (!reservationData) {
        alert('Please fetch reservation data first');
        return;
    }

    const messageContainer = document.getElementById('conversation-history');
    
    // Add user message to conversation history
    const userMessageObj = {
        message_id: `msg_${Date.now()}`,
        role: 'user',
        content: message,
        timestamp: new Date().toISOString()
    };
    conversationHistory.push(userMessageObj);
    
    // Display user message
    const userMessageDiv = document.createElement('div');
    userMessageDiv.className = 'message user';
    userMessageDiv.innerHTML = `
        <div class="sender">User</div>
        <div class="content">${message}</div>
        <div class="timestamp">${new Date().toLocaleString()}</div>
    `;
    messageContainer.appendChild(userMessageDiv);

    // Add loading message
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message assistant';
    loadingDiv.id = 'loading-message';
    loadingDiv.innerHTML = `
        <div class="sender">Assistant</div>
        <div class="content">
            <div style="text-align: center; padding: 20px;">
                <div class="loading-spinner" style="width: 30px; height: 30px; border: 3px solid #f3f3f3; border-top: 3px solid #3498db; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 10px;"></div>
                <p style="color: #666; font-size: 14px; margin: 0;">Processing your request...</p>
            </div>
        </div>
        <div class="timestamp">${new Date().toISOString().replace('T', ' ').substring(0, 19)}</div>
    `;
    messageContainer.appendChild(loadingDiv);

    // Scroll to bottom
    messageContainer.scrollTop = messageContainer.scrollHeight;

    // Clear input
    document.getElementById('chat-message').value = '';

    try {
        // Call the CHAT API endpoint with full conversation context
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                reservation_id: document.getElementById('shared-reservation-id').value,
                message: message,
                conversation_history: conversationHistory
            })
        });

        const data = await response.json();

        // Remove loading message
        const loadingMessage = document.getElementById('loading-message');
        if (loadingMessage) {
            loadingMessage.remove();
        }

        if (response.ok) {
            // Add assistant response to conversation history
            const assistantMessageObj = {
                message_id: `msg_${Date.now()}_assistant`,
                role: 'assistant',
                content: data.response,
                timestamp: new Date().toISOString()
            };
            conversationHistory.push(assistantMessageObj);
            
            // Display assistant response
            const assistantDiv = document.createElement('div');
            assistantDiv.className = 'message assistant';
            assistantDiv.innerHTML = `
                <div class="sender">Assistant</div>
                <div class="content">${data.response}</div>
                <div class="timestamp">${new Date().toISOString().replace('T', ' ').substring(0, 19)}</div>
            `;
            messageContainer.appendChild(assistantDiv);
        } else {
            // Add error message
            const errorDiv = document.createElement('div');
            errorDiv.className = 'message assistant error';
            errorDiv.innerHTML = `
                <div class="sender">Assistant</div>
                <div class="content">Error: ${data.detail || 'Unknown error occurred'}</div>
                <div class="timestamp">${new Date().toISOString().replace('T', ' ').substring(0, 19)}</div>
            `;
            messageContainer.appendChild(errorDiv);
        }

        // Scroll to bottom
        messageContainer.scrollTop = messageContainer.scrollHeight;

    } catch (error) {
        // Remove loading message
        const loadingMessage = document.getElementById('loading-message');
        if (loadingMessage) {
            loadingMessage.remove();
        }

        // Add error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'message assistant error';
        errorDiv.innerHTML = `
            <div class="sender">Assistant</div>
            <div class="content">Network error: ${error.message}</div>
            <div class="timestamp">${new Date().toISOString().replace('T', ' ').substring(0, 19)}</div>
        `;
        messageContainer.appendChild(errorDiv);

        // Scroll to bottom
        messageContainer.scrollTop = messageContainer.scrollHeight;
    }
}


