// Main JavaScript for Gemini Agent Tester

// Global variables - Force HTTPS for production, fallback to HTTP for development
const API_BASE = (window.location.protocol === 'https:' ? 'https:' : 'http:') + '//' + window.location.host + '/api/v1';
const RESERVATION_API = 'https://api.gptpricing.com/zendesk-comments/ai-summary';
let conversationHistory = [];
let reservationData = null;
console.log('Current API_BASE:', window.API_BASE);
console.log('Current protocol:', window.location.protocol);
console.log('Current host:', window.location.host);
// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    // Add initial message to history
    addToHistory();
    
    // Set up reservation ID sync
    setupReservationIdSync();
});

// Tab switching functionality
function switchTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Remove active class from all tabs
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected tab content
    document.getElementById(tabName).classList.add('active');
    
    // Add active class to selected tab
    event.target.classList.add('active');
}

// Status display utility
function showStatus(elementId, message, type) {
    const statusElement = document.getElementById(elementId);
    statusElement.textContent = message;
    statusElement.className = `status ${type}`;
}

// Global success message display
function showGlobalSuccess(message) {
    // Create or update global success message
    let successDiv = document.getElementById('global-success-message');
    if (!successDiv) {
        successDiv = document.createElement('div');
        successDiv.id = 'global-success-message';
        successDiv.className = 'global-success';
        successDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
            border-radius: 8px;
            padding: 15px 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 1000;
            max-width: 400px;
            animation: slideInRight 0.3s ease;
        `;
        document.body.appendChild(successDiv);
    }
    
    successDiv.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 18px;">✅</span>
            <span>${message}</span>
        </div>
    `;
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        if (successDiv) {
            successDiv.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                if (successDiv && successDiv.parentNode) {
                    successDiv.parentNode.removeChild(successDiv);
                }
            }, 300);
        }
    }, 5000);
}

// Guest data analysis
function analyzeGuestData(data) {
    let summary = '';
    
    try {
        console.log('Raw API data:', data);
        
        // Extract key reservation info
        let guestName = '';
        let propertyName = '';
        let propertyCity = '';
        let checkInDate = '';
        let checkOutDate = '';
        let guestCount = '';
        let building = '';
        let guestAge = '';
        let guestVehicle = '';
        
        // Parse reservationInfos array
        if (data.reservationInfos && Array.isArray(data.reservationInfos) && data.reservationInfos.length > 0) {
            const reservation = data.reservationInfos[0];
            
            guestName = reservation.name || '';
            propertyName = reservation.listing_name || '';
            propertyCity = reservation.city || '';
            checkInDate = reservation.date_from || '';
            checkOutDate = reservation.date_to || '';
            guestCount = reservation.number_of_guests || '';
            building = reservation.building || '';
            
            // Extract additional guest insights
            if (reservation.background_check_results && reservation.background_check_results.length > 0) {
                const bg = reservation.background_check_results[0];
                guestAge = bg.age || '';
                guestVehicle = reservation.vehicle_type || '';
            }
        }
        
        // Intelligent comment analysis for personality insights
        let personalityTraits = [];
        let travelStyle = [];
        let preferences = [];
        
        if (data.comments && Array.isArray(data.comments)) {
            data.comments.forEach(comment => {
                if (comment.body) {
                    const text = comment.body.toLowerCase();
                    const author = comment.author || '';
                    const role = comment.sender_role || '';
                    
                    // Analyze guest personality from their own messages
                    if (role === 'guest' && author.toLowerCase().includes('benjamin')) {
                        if (text.includes('thank you') || text.includes('appreciate') || text.includes('grateful')) {
                            personalityTraits.push('Polite and appreciative');
                        }
                        if (text.includes('looking forward') || text.includes('excited')) {
                            personalityTraits.push('Enthusiastic about travel');
                        }
                        if (text.includes('clarify') || text.includes('confused') || text.includes('misleading')) {
                            personalityTraits.push('Detail-oriented and expects accuracy');
                        }
                        if (text.includes('parking') || text.includes('access') || text.includes('fob')) {
                            travelStyle.push('Plans ahead for practical logistics');
                        }
                        if (text.includes('check-in') || text.includes('check-out')) {
                            travelStyle.push('Values flexible timing');
                        }
                        if (text.includes('bedroom') || text.includes('apartment')) {
                            preferences.push('Prefers spacious accommodations');
                        }
                    }
                    
                    // Analyze host feedback about guest
                    if (role === 'host' && text.includes('benjamin')) {
                        if (text.includes('positive') || text.includes('amazing') || text.includes('grateful')) {
                            personalityTraits.push('Leaves positive feedback');
                        }
                        if (text.includes('easygoing') || text.includes('understanding')) {
                            personalityTraits.push('Easygoing and understanding');
                        }
                    }
                }
            });
        }
        
        // Remove duplicates and create unique insights
        personalityTraits = [...new Set(personalityTraits)];
        travelStyle = [...new Set(travelStyle)];
        preferences = [...new Set(preferences)];
        
        // Calculate stay duration
        let stayDuration = '';
        if (checkInDate && checkOutDate) {
            try {
                const checkIn = new Date(checkInDate);
                const checkOut = new Date(checkOutDate);
                const nights = Math.ceil((checkOut - checkIn) / (1000 * 60 * 60 * 24));
                stayDuration = `${nights} night${nights !== 1 ? 's' : ''}`;
            } catch (e) {
                console.error('Error parsing dates:', e);
            }
        }
        
        // SMART AGENT SUMMARY - Intelligent and personalized
        summary += `<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">`;
        summary += `<h4 style="margin: 0 0 10px 0; color: #2c3e50;">🎯 Guest Profile Summary</h4>`;
        
        if (guestName) {
            summary += `<p style="margin: 5px 0;"><strong>Guest:</strong> ${guestName}${guestAge ? ` (${guestAge} years old)` : ''}</p>`;
        }
        
        if (building && propertyName) {
            summary += `<p style="margin: 5px 0;"><strong>Property:</strong> ${building} - ${propertyName}</p>`;
        }
        
        if (propertyCity) {
            summary += `<p style="margin: 5px 0;"><strong>Location:</strong> ${propertyCity}</p>`;
        }
        
        if (checkInDate && checkOutDate) {
            summary += `<p style="margin: 5px 0;"><strong>Stay:</strong> ${checkInDate} to ${checkOutDate} (${stayDuration})</p>`;
        }
        
        if (guestCount) {
            summary += `<p style="margin: 5px 0;"><strong>Guests:</strong> ${guestCount} adult${guestCount !== '1' ? 's' : ''}</p>`;
        }
        
        if (guestVehicle) {
            summary += `<p style="margin: 5px 0;"><strong>Vehicle:</strong> ${guestVehicle}</p>`;
        }
        summary += `</div>`;
        
        // Personality & Travel Style Insights
        if (personalityTraits.length > 0 || travelStyle.length > 0) {
            summary += `<div style="background: #e8f4fd; padding: 15px; border-radius: 8px; margin: 10px 0;">`;
            summary += `<h4 style="margin: 0 0 10px 0; color: #2980b9;">🧠 Guest Personality & Travel Style</h4>`;
            
            if (personalityTraits.length > 0) {
                summary += `<p style="margin: 5px 0;"><strong>Personality:</strong> ${personalityTraits.join(', ')}</p>`;
            }
            
            if (travelStyle.length > 0) {
                summary += `<p style="margin: 5px 0;"><strong>Travel Style:</strong> ${travelStyle.join(', ')}</p>`;
            }
            
            if (preferences.length > 0) {
                summary += `<p style="margin: 5px 0;"><strong>Accommodation Preferences:</strong> ${preferences.join(', ')}</p>`;
            }
            summary += `</div>`;
        }
        
        // Personalized AI Recommendation Prompt
        summary += `<div style="background: #fff3cd; padding: 15px; border-radius: 8px; margin: 10px 0;">`;
        summary += `<h4 style="margin: 0 0 10px 0; color: #856404;">🤖 Personalized AI Recommendation Prompt</h4>`;
        
        let promptText = '';
        if (guestName) {
            promptText += `${guestName} is a ${guestAge ? `${guestAge}-year-old ` : ''}`;
        }
        
        if (personalityTraits.length > 0) {
            promptText += `${personalityTraits.slice(0, 2).join(' and ')} guest `;
        }
        
        promptText += `staying at ${building ? building + ' - ' : ''}${propertyName} in ${propertyCity}`;
        
        if (checkInDate && checkOutDate) {
            promptText += ` from ${checkInDate} to ${checkOutDate} (${stayDuration})`;
        }
        
        promptText += '.';
        
        if (travelStyle.length > 0) {
            promptText += ` They are ${travelStyle.slice(0, 2).join(' and ')}.`;
        }
        
        if (guestVehicle) {
            promptText += ` They have a ${guestVehicle} for transportation.`;
        }
        
        summary += `<p style="margin: 5px 0; font-style: italic;">"${promptText}"</p>`;
        summary += `<p style="margin: 5px 0;"><strong>Request:</strong> Based on this guest's personality and travel style, provide 3-5 highly personalized recommendations for activities, restaurants, and attractions in ${propertyCity}. Consider their age, vehicle access, and preferences for a warm, concierge-style response that feels tailored specifically to them.</p>`;
        summary += `</div>`;
        
    } catch (error) {
        console.error('Error analyzing data:', error);
        summary = `<div style="background: #f8d7da; padding: 15px; border-radius: 8px; margin: 10px 0;">`;
        summary += `<h4 style="margin: 0 0 10px 0; color: #721c24;"> Error</h4>`;
        summary += `<p style="margin: 5px 0;">Error analyzing data: ${error.message}</p>`;
        summary += `</div>`;
    }
    
    return summary || '<p>No guest information available</p>';
}

// Sync reservation ID across all inputs
function setupReservationIdSync() {
    const sharedInput = document.getElementById('shared-reservation-id');
    if (sharedInput) {
        sharedInput.addEventListener('input', function() {
            // Update any other reservation ID inputs if they exist
            const otherInputs = document.querySelectorAll('input[id*="reservation-id"]');
            otherInputs.forEach(input => {
                if (input !== sharedInput) {
                    input.value = sharedInput.value;
                }
            });
        });
    }
}
