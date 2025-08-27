import json
import hashlib
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel

from app.core.config import settings
from app.services.reservation_service import ReservationService
from app.services.conversation_service import ConversationService
from app.schemas.chat import ChatMessage
from app.schemas.recommendations import RecommendationItem

import logging
logger = logging.getLogger(__name__)


class RecommendationService:
    """Service for generating personalized recommendations using AI."""
    
    def __init__(self):
        """Initialize the recommendation service."""
        try:
            self.llm = ChatVertexAI(
                model_name=settings.GEMINI_MODEL,
                temperature=settings.GEMINI_TEMPERATURE,
                max_output_tokens=settings.GEMINI_MAX_TOKENS,
                location=settings.GOOGLE_CLOUD_LOCATION,
                project=settings.GOOGLE_CLOUD_PROJECT
            )
            logger.info(f"Vertex AI model initialized successfully: {settings.GEMINI_MODEL}")
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI model: {e}", exc_info=True)
            self.llm = None
            
        self.reservation_service = ReservationService()
        self.conversation_service = ConversationService()
    
    async def test_model_connection(self) -> bool:
        """Test if the Vertex AI model is working."""
        if not self.llm:
            logger.error("Vertex AI model not initialized")
            return False
            
        try:
            test_prompt = ChatPromptTemplate.from_template("Say 'Hello, I am working!'")
            chain = test_prompt | self.llm
            result = await chain.ainvoke({})
            if result and hasattr(result, 'content') and 'working' in result.content.lower():
                logger.info("Vertex AI model connection test successful")
                return True
            else:
                logger.warning("Vertex AI model connection test failed - unexpected response")
                return False
        except Exception as e:
            logger.error(f"Vertex AI model connection test failed: {e}", exc_info=True)
            return False
    
    async def generate_recommendations(
        self, 
        reservation_data: Dict[str, Any],
        user_message: str = None
    ) -> Dict[str, Any]:
        """Generate personalized recommendations for a guest."""
        try:
            # Extract guest information
            guest_info = self.reservation_service.extract_relevant_fields(reservation_data)
            
            # Generate AI recommendations
            ai_recommendations = await self._generate_ai_recommendations(guest_info)
            
            # Enrich with Google Places data
            enriched_recommendations = await self.enrich_with_google_places(
                ai_recommendations.get('recommendations', []),
                guest_info.get('property_city', 'New Haven')
            )
            
            return {
                "guest_name": guest_info.get('guest_name', 'Guest'),
                "destination": guest_info.get('property_city', 'New Haven'),
                "stay_dates": f"{guest_info.get('date_from', 'N/A')} to {guest_info.get('date_to', 'N/A')}",
                "recommendations": enriched_recommendations,
                "ai_analysis": ai_recommendations.get('ai_analysis', ''),
                "personalization_reason": ai_recommendations.get('personalization_reason', '')
            }
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            # Return fallback recommendations
            return {
                "guest_name": "Guest",
                "destination": "New Haven",
                "stay_dates": "N/A",
                "recommendations": self._generate_fallback_recommendations(),
                "ai_analysis": "Unable to generate personalized recommendations at this time.",
                "personalization_reason": "Based on general preferences for the area."
            }
    
    async def _generate_ai_recommendations(self, guest_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered recommendations using Vertex AI."""
        try:
            prompt = ChatPromptTemplate.from_template("""
            You are a knowledgeable local concierge for New Haven, CT. Based on the guest information below, 
            generate personalized recommendations for restaurants, activities, and attractions.
            
            Guest Information:
            - Name: {guest_name}
            - Group Size: {group_size} guests
            - Stay Duration: {stay_duration} nights
            - City: {city}
            - Building: {building}
            - Guest Preferences: {preferences}
            
            Generate exactly 5 diverse recommendations including:
            1. A local restaurant (consider cuisine type, price range, atmosphere)
            2. A cultural activity or attraction
            3. An outdoor activity or park
            4. A shopping or entertainment option
            5. A unique local experience
            
            For each recommendation, provide:
            - name: Specific business/place name
            - type: restaurant, activity, attraction, etc.
            - category: cuisine type, activity type, etc.
            - description: 2-3 sentences explaining why this is recommended
            - personalization_reason: Why this specific recommendation fits this guest
            
            Format your response as a JSON object with this structure:
            {{
                "recommendations": [
                    {{
                        "name": "Business Name",
                        "type": "restaurant",
                        "category": "Italian",
                        "description": "Description here...",
                        "personalization_reason": "Why this fits the guest..."
                    }}
                ],
                "ai_analysis": "Brief summary of why these recommendations were chosen",
                "personalization_reason": "Overall personalization strategy"
            }}
            
            Focus on places that are within walking distance or a short drive from the hotel area.
            Make recommendations specific and actionable, not generic.
            """)
            
            chain = prompt | self.llm | JsonOutputParser()
            
            result = await chain.ainvoke({
                "guest_name": guest_info.get('guest_name', 'Guest'),
                "group_size": guest_info.get('number_of_guests', '1'),
                "stay_duration": guest_info.get('length_of_stay', '1'),
                "city": guest_info.get('property_city', 'New Haven'),
                "building": guest_info.get('building', 'Hotel'),
                "preferences": guest_info.get('guest_preferences', 'No specific preferences noted')
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating AI recommendations: {e}")
            return {
                "recommendations": self._generate_fallback_recommendations(),
                "ai_analysis": "Generated fallback recommendations due to AI service error.",
                "personalization_reason": "Based on general preferences for the area."
            }
    
    def _generate_fallback_recommendations(self) -> List[Dict[str, Any]]:
        """Generate fallback recommendations when AI service is unavailable."""
        return [
            {
                "name": "Modern Apizza",
                "type": "restaurant",
                "category": "Pizza",
                "description": "Famous New Haven-style pizza with thin crust and unique toppings. A local institution since 1934.",
                "personalization_reason": "Classic New Haven experience perfect for any visitor"
            },
            {
                "name": "Yale University Art Gallery",
                "type": "attraction",
                "category": "Museum",
                "description": "World-class art collection featuring European, American, and African art. Free admission.",
                "personalization_reason": "Cultural enrichment and free activity for guests"
            },
            {
                "name": "East Rock Park",
                "type": "activity",
                "category": "Outdoor",
                "description": "Beautiful park with hiking trails, scenic views of New Haven, and picnic areas.",
                "personalization_reason": "Outdoor recreation and nature experience"
            },
            {
                "name": "Chapel Street Shopping District",
                "type": "activity",
                "category": "Shopping",
                "description": "Historic shopping area with boutique stores, cafes, and street performers.",
                "personalization_reason": "Local shopping and entertainment district"
            },
            {
                "name": "Pepe's Pizza",
                "type": "restaurant",
                "category": "Pizza",
                "description": "Another legendary New Haven pizza spot, known for their white clam pizza.",
                "personalization_reason": "Must-try local cuisine experience"
            }
        ]
    
    async def enrich_with_google_places(
        self,
        recommendations: List[Dict[str, Any]],
        location: str
    ) -> List[Dict[str, Any]]:
        """Enrich recommendations with Google Places data including photos, hours, and real distances."""
        if not settings.GOOGLE_PLACES_API_KEY:
            logger.warning("Google Places API key not configured, returning basic recommendations")
            return [
                {
                    "name": rec["name"],
                    "type": rec["type"],
                    "category": rec.get("category", "General"),
                    "address": "Location details available on request",
                    "rating": None,
                    "description": rec["description"],
                    "personalization_reason": rec.get("personalization_reason", "Based on your location and preferences"),
                    "image_url": None,
                    "google_place_id": None,
                    "distance_status": "API key missing - cannot calculate distance",
                    "walking_duration": None
                }
                for rec in recommendations
            ]
        
        enriched_recommendations = []
        
        for rec in recommendations:
            try:
                # Search for the place using Google Places API
                search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
                
                # Try multiple search strategies for better results
                search_queries = [
                    f"{rec['name']} {location}",  # Full name + location
                    f"{rec['name']}",  # Just the name
                    f"{rec['name']} New Haven",  # Name + city
                ]
                
                place = None
                place_id = None
                
                for query in search_queries:
                    params = {
                        "query": query,
                        "key": settings.GOOGLE_PLACES_API_KEY,
                        # Don't restrict by type initially for better results
                    }
                    
                    logger.info(f"🔍 Searching Google Places with query: '{query}'")
                    response = requests.get(search_url, params=params, timeout=settings.GOOGLE_PLACES_TIMEOUT)
                    if response.status_code == 200:
                        places_data = response.json()
                        
                        logger.info(f"Google Places API response: {places_data.get('status')}")
                        if places_data.get('results'):
                            place = places_data["results"][0]
                            place_id = place.get("place_id")
                            logger.info(f" Found place '{place.get('name')}' for query '{query}'")
                            logger.info(f"Place coordinates: {place.get('geometry', {}).get('location', 'N/A')}")
                            break
                        else:
                            logger.warning(f" No results found for query '{query}'")
                    else:
                        logger.warning(f" Google Places API request failed: {response.status_code}")
                
                if not place:
                    # If no results, try with type restriction as fallback
                    logger.info(f" Trying fallback search with type restriction for '{rec['name']}'")
                    params = {
                        "query": f"{rec['name']} {location}",
                        "key": settings.GOOGLE_PLACES_API_KEY,
                        "type": rec['type']
                    }
                    
                    response = requests.get(search_url, params=params, timeout=settings.GOOGLE_PLACES_TIMEOUT)
                    if response.status_code == 200:
                        places_data = response.json()
                        
                        if places_data.get("results"):
                            place = places_data["results"][0]
                            place_id = place.get("place_id")
                            logger.info(f" Found place '{place.get('name')}' with type restriction")
                        else:
                            logger.warning(f" Fallback search also failed for '{rec['name']}'")
                    else:
                        logger.warning(f" Fallback search request failed: {response.status_code}")
                
                # Now process the place if we found one
                if place:
                    # Get additional details including photos
                    photo_url = None
                    if place.get("photos"):
                        photo_reference = place["photos"][0]["photo_reference"]
                        photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_reference}&key={settings.GOOGLE_PLACES_API_KEY}"
                    
                    # Calculate real distance using Google Maps Directions API
                    distance = None
                    walking_duration = None
                    
                    if place.get("geometry") and place["geometry"].get("location"):
                        try:
                            # Use Google Routes API for accurate distance and walking time
                            routes_url = "https://routes.googleapis.com/directions/v2:computeRoutes"
                            
                            # Use hotel location as origin (can be configured)
                            hotel_location = settings.HOTEL_LOCATION  # Configurable hotel location
                            destination = f"{place['geometry']['location']['lat']},{place['geometry']['location']['lng']}"
                            
                            logger.info(f" Calculating distance from {hotel_location} to {destination}")
                            
                            # Routes API requires POST with JSON body
                            routes_payload = {
                                "origin": {
                                    "address": hotel_location
                                },
                                "destination": {
                                    "location": {
                                        "latLng": {
                                            "latitude": place['geometry']['location']['lat'],
                                            "longitude": place['geometry']['location']['lng']
                                        }
                                    }
                                },
                                "travelMode": "WALK",
                                "routingPreference": "TRAFFIC_AWARE",
                                "computeAlternativeRoutes": False,
                                "routeModifiers": {
                                    "avoidTolls": False,
                                    "avoidHighways": False
                                },
                                "languageCode": "en-US",
                                "units": "IMPERIAL"
                            }
                            
                            headers = {
                                'Content-Type': 'application/json',
                                'X-Goog-Api-Key': settings.GOOGLE_PLACES_API_KEY,
                                'X-Goog-FieldMask': 'routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline'
                            }
                            
                            routes_response = requests.post(routes_url, json=routes_payload, headers=headers, timeout=settings.GOOGLE_PLACES_TIMEOUT)
                            if routes_response.status_code == 200:
                                routes_data = routes_response.json()
                                
                                logger.info(f"Routes API response: {routes_data.get('routes', [])}")
                                logger.info(f"Routes API params: origin={hotel_location}, destination={destination}")
                                
                                if routes_data.get('routes') and len(routes_data['routes']) > 0:
                                    route = routes_data['routes'][0]
                                    # Convert meters to miles and seconds to readable format
                                    distance_meters = route.get('distanceMeters', 0)
                                    duration_seconds = route.get('duration', '0s')
                                    
                                    # Convert meters to miles
                                    distance_miles = distance_meters * 0.000621371
                                    if distance_miles < 1:
                                        distance = f"{distance_miles * 5280:.0f} ft"
                                    else:
                                        distance = f"{distance_miles:.1f} mi"
                                    
                                    # Convert seconds to readable format
                                    if isinstance(duration_seconds, str) and duration_seconds.endswith('s'):
                                        try:
                                            seconds = int(duration_seconds[:-1])
                                        except ValueError:
                                            seconds = 0
                                    else:
                                        seconds = int(duration_seconds) if duration_seconds else 0
                                    
                                    if seconds < 60:
                                        walking_duration = f"{seconds} min"
                                    else:
                                        minutes = seconds // 60
                                        walking_duration = f"{minutes} min"
                                    
                                    logger.info(f" Successfully calculated distance: {distance}, walking time: {walking_duration}")
                                else:
                                    logger.warning(f" Routes API returned no routes")
                                    distance = None
                                    walking_duration = None
                            else:
                                logger.warning(f" Routes API request failed: {routes_response.status_code}")
                                if routes_response.text:
                                    logger.warning(f"Error response: {routes_response.text}")
                                distance = None
                                walking_duration = None
                                
                        except Exception as e:
                            logger.warning(f"Error calculating distance with Routes API: {e}")
                            distance = None
                            walking_duration = None
                    
                    # Convert price level to readable format
                    price_range = None
                    if place.get("price_level") is not None:
                        price_level = place["price_level"]
                        if price_level == 0: price_range = "$"
                        elif price_level == 1: price_range = "$$"
                        elif price_level == 2: price_range = "$$$"
                        elif price_level == 3: price_range = "$$$$"
                        elif price_level == 4: price_range = "$$$$$"
                    
                    # Create recommendation data
                    recommendation_data = {
                        "name": place.get("name", rec["name"]),
                        "type": rec["type"],
                        "category": rec.get("category", "General"),
                        "address": place.get("formatted_address", "Address available"),
                        "rating": place.get("rating"),
                        "description": rec["description"],
                        "personalization_reason": rec.get("personalization_reason", "Based on your location and preferences"),
                        "image_url": photo_url,
                        "google_place_id": place_id,
                        "walking_duration": walking_duration
                    }
                    
                    # Only include fields if they were calculated
                    if distance:
                        recommendation_data["distance"] = distance
                        logger.info(f" Final recommendation for '{rec['name']}': distance={distance}, walking_time={walking_duration}")
                    else:
                        recommendation_data["distance_status"] = "Distance calculation failed - API error"
                        logger.warning(f" Distance calculation failed for '{rec['name']}': {recommendation_data['distance_status']}")
                    
                    if price_range:
                        recommendation_data["price_range"] = price_range
                    
                    enriched_recommendations.append(recommendation_data)
                else:
                    # Fallback to basic recommendation if no place found
                    enriched_recommendations.append({
                        "name": rec["name"],
                        "type": rec["type"],
                        "category": rec.get("category", "General"),
                        "address": "Location details available on request",
                        "rating": None,
                        "description": rec["description"],
                        "personalization_reason": rec.get("personalization_reason", "Based on your location and preferences"),
                        "image_url": None,
                        "google_place_id": None,
                        "distance_status": "Google Places search failed - cannot calculate distance",
                        "walking_duration": None
                    })
                     
            except Exception as e:
                logger.warning(f"Error enriching recommendation with Google Places: {e}")
                # Fallback to basic recommendation
                enriched_recommendations.append({
                    "name": rec["name"],
                    "type": rec["type"],
                    "category": rec.get("category", "General"),
                    "address": "Location details available on request",
                    "rating": None,
                    "description": rec["description"],
                    "personalization_reason": rec.get("personalization_reason", "Based on your location and preferences"),
                    "image_url": None,
                    "google_place_id": None,
                    "distance_status": f"Error enriching recommendation: {str(e)}",
                    "walking_duration": None
                })
        
        # Log summary of distance calculation results
        successful_distances = sum(1 for rec in enriched_recommendations if rec.get('distance'))
        failed_distances = sum(1 for rec in enriched_recommendations if rec.get('distance_status'))
        total_recommendations = len(enriched_recommendations)
        
        logger.info(f" Distance calculation summary: {successful_distances}/{total_recommendations} successful, {failed_distances} failed")
        
        return enriched_recommendations
    
    def _build_chat_context(
        self, 
        reservation_data: Dict[str, Any],
        user_message: str, 
        conversation_history: List[ChatMessage],
        ai_recommendations: Dict[str, Any]
    ) -> str:
        """Build context for chat response generation."""
        
        relevant_fields = self.reservation_service.extract_relevant_fields(
            reservation_data
        )
        group_type = self.reservation_service.determine_group_type(reservation_data)
        
        context = f"""
        You are a helpful hotel concierge assistant for {relevant_fields.get('guest_name', 'Guest')} staying at {relevant_fields.get('building', 'Hotel')} in {relevant_fields.get('property_city', relevant_fields.get('city', 'N/A'))}.
        
        Guest Details:
        - Group: {relevant_fields.get('number_of_guests', '1')} guests ({group_type})
        - Stay: {relevant_fields.get('date_from', 'N/A')} to {relevant_fields.get('date_to', 'N/A')} ({relevant_fields.get('length_of_stay', 'N/A')} nights)
        - Check-in: {relevant_fields.get('checkin_time', 'N/A')}, Check-out: {relevant_fields.get('checkout_time', 'N/A')}
        """
        
        # Add property details (already extracted from reservations API)
        context += f"""
        Property Details:
        - Address: {relevant_fields.get('property_address', 'N/A')}
        - Neighborhood: {relevant_fields.get('property_neighborhood', 'N/A')}
        - Amenities: {', '.join(relevant_fields.get('property_amenities', []))}
        """
        
        context += f"""
        Available Recommendations:
        {json.dumps(ai_recommendations.get('recommendations', []), indent=2)}
        
        Conversation History:
        {self._format_conversation_history(conversation_history)}
        
        Current User Message: {user_message}
        
        Respond naturally as a helpful concierge. Use the available recommendations when relevant.
        Keep responses conversational and helpful. If the user asks for specific types of recommendations,
        suggest from the available list or offer to find more.
        """
        
        return context
    
    def _format_conversation_history(self, conversation_history: List[ChatMessage]) -> str:
        """Format conversation history for context."""
        if not conversation_history:
            return "No previous conversation."
        
        formatted = []
        for msg in conversation_history:
            formatted.append(f"{msg.role}: {msg.content}")
        
        return "\n".join(formatted)
    
    async def _generate_chat_response(self, context: str) -> str:
        """Generate chat response using Vertex AI."""
        try:
            if not self.llm:
                logger.error("Vertex AI model not available, using fallback")
                return self._generate_fallback_response(context)
                
            logger.info(f"Generating chat response with context length: {len(context)}")
            
            prompt = ChatPromptTemplate.from_template("""
            You are a helpful hotel concierge. Use this context to respond naturally to the guest:
            
            {context}
            
            Respond as a helpful, friendly concierge. Be conversational and use the available recommendations
            when relevant to the guest's request.
            """)
            
            chain = prompt | self.llm
            result = await chain.ainvoke({"context": context})
            
            if result and hasattr(result, 'content') and result.content:
                logger.info(f"Successfully generated chat response: {result.content[:100]}...")
                return result.content
            else:
                logger.warning("Vertex AI returned empty or invalid response")
                return self._generate_fallback_response(context)
            
        except Exception as e:
            logger.error(f"Error generating chat response with Vertex AI: {e}", exc_info=True)
            return self._generate_fallback_response(context)
    
    def _generate_fallback_response(self, context: str) -> str:
        """Generate an intelligent fallback response when AI fails."""
        try:
            # Extract key information from context for a personalized fallback
            if "Guest" in context:
                if "restaurant" in context.lower() or "food" in context.lower():
                    return "I'd be happy to help you find great restaurants! What type of cuisine are you interested in? I can recommend some excellent dining options in the area."
                elif "activity" in context.lower() or "attraction" in context.lower():
                    return "Great question! There are many wonderful attractions and activities nearby. Are you interested in cultural sites, outdoor activities, or something specific?"
                elif "transport" in context.lower() or "getting around" in context.lower():
                    return "Perfect! Let me help you with transportation options. What's your preferred way to get around, and where would you like to go?"
                else:
                    return "Hello! I'm your personal concierge assistant. I can help you find restaurants, activities, attractions, and provide local recommendations. What would you like to know about?"
            else:
                return "I'm here to help! I can assist with restaurant recommendations, local attractions, activities, transportation, and more. What specific information would you like?"
                
        except Exception as e:
            logger.error(f"Error generating fallback response: {e}")
            return "I'm here to help! I can assist with restaurant recommendations, local attractions, activities, transportation, and more. What would you like to know about?"
    
    def _generate_message_id(self, user_message: str) -> str:
        """Generate a unique message ID."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        message_hash = hashlib.md5(user_message.encode()).hexdigest()[:8]
        return f"msg_{timestamp}_{message_hash}"
    
    async def handle_chat_interaction(
        self,
        reservation_data: Dict[str, Any],
        user_message: str,
        conversation_history: List[ChatMessage]
    ) -> Dict[str, Any]:
        """Handle a chat interaction and generate a response."""
        try:
            # Generate recommendations if not already available
            recommendations = await self.generate_recommendations(reservation_data, user_message)
            
            # Build chat context
            context = self._build_chat_context(
                reservation_data, user_message, conversation_history, recommendations
            )
            
            # Generate response
            response = await self._generate_chat_response(context)
            
            # Create message ID
            message_id = self._generate_message_id(user_message)
            
            return {
                "message_id": message_id,
                "response": response,
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error handling chat interaction: {e}")
            return {
                "message_id": "error",
                "response": "I apologize, but I'm experiencing technical difficulties. Please try again later.",
                "recommendations": None,
                "timestamp": datetime.now().isoformat()
            }

    async def handle_chat_only_interaction(
        self,
        reservation_data: Dict[str, Any],
        user_message: str,
        conversation_history: List[ChatMessage]
    ) -> Dict[str, Any]:
        """Handle a chat-only interaction without regenerating recommendations - FAST."""
        try:
            # Extract basic guest info for context
            guest_info = self.reservation_service.extract_relevant_fields(reservation_data)
            
            # Build lightweight chat context (no expensive recommendation generation)
            context = self._build_lightweight_chat_context(
                guest_info, user_message, conversation_history
            )
            
            # Generate response using Vertex AI
            response = await self._generate_chat_response(context)
            
            # Create message ID
            message_id = self._generate_message_id(user_message)
            
            return {
                "message_id": message_id,
                "response": response,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error handling chat-only interaction: {e}")
            return {
                "message_id": "error",
                "response": "I apologize, but I'm experiencing technical difficulties. Please try again later.",
                "timestamp": datetime.now().isoformat()
            }

    def _build_lightweight_chat_context(
        self,
        guest_info: Dict[str, Any],
        user_message: str,
        conversation_history: List[ChatMessage]
    ) -> str:
        """Build lightweight chat context without expensive operations."""
        context = f"""
        You are a helpful hotel concierge for {guest_info.get('property_city', 'New Haven')}.
        
        Guest Information:
        - Name: {guest_info.get('guest_name', 'Guest')}
        - Group Size: {guest_info.get('group_size', '1')} guests
        - Stay Duration: {guest_info.get('stay_duration', 'N/A')} nights
        - Property: {guest_info.get('property_name', 'your accommodation')}
        - City: {guest_info.get('property_city', 'New Haven')}
        - Neighborhood: {guest_info.get('property_neighborhood', 'N/A')}
        
        Conversation History:
        {self._format_conversation_history(conversation_history)}
        
        Current User Message: {user_message}
        
        Respond naturally as a helpful concierge. Be conversational and helpful.
        If the user asks for specific recommendations, you can suggest general areas or types of places.
        Focus on being helpful and maintaining conversation context.
        """
        
        return context
