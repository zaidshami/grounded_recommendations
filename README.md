# 🏗️ Guest Recommendation Generation API

A **production-grade FastAPI application** that generates personalized recommendations for hotel guests using AI, integrating with multiple data sources for hyper-personalized experiences.

## ✨ Features

- **🤖 AI-Powered Recommendations**: Uses Google Gemini 1.5 Pro with grounded-in-maps and grounded-in-search tools for intelligent, location-aware suggestions
- **💬 Interactive Chat**: Maintains conversation history for contextual responses
- **📊 Direct JSON API**: One-time recommendation generation without chat interaction
- **🏨 Multi-Source Integration**: Combines reservations, properties, and conversations data
- **🔍 Google Places Enrichment**: Enhances recommendations with real-time location data
- **📈 Production Ready**: Proper error handling, logging, middleware, and configuration management
- **🔄 Dual Endpoints**: Both chat and direct recommendation endpoints using the same underlying tool

## 🏗️ Architecture

### **Production-Grade Structure**
```
app/
├── __init__.py                 # Main app package
├── main.py                     # FastAPI app initialization & middleware
├── core/                       # Core configuration & utilities
│   ├── config.py              # Settings & environment variables
│   ├── logging.py             # Structured logging configuration
│   └── exceptions.py          # Custom exception classes
├── api/                        # API layer
│   ├── v1/                    # API versioning
│   │   ├── api.py             # Main API router
│   │   └── endpoints/         # Individual endpoint implementations
│   │       ├── chat.py        # Chat endpoint
│   │       ├── recommendations.py  # Direct recommendations
│   │       └── reservations.py     # Reservation details
├── services/                   # Business logic layer
│   ├── recommendation_service.py  # Main orchestration service
│   ├── reservation_service.py     # Reservation data handling
│   ├── property_service.py        # Property data handling
│   └── conversation_service.py    # Conversation data handling
├── models/                     # Domain models
│   └── domain.py              # Core business entities
└── schemas/                    # Pydantic schemas
    ├── chat.py                # Chat request/response schemas
    └── recommendations.py     # Recommendation schemas
```

### **Data Flow Architecture**

#### **1. Interactive Chat Flow**
```
User Message → Chat Endpoint → Recommendation Service → 
Fetch All Data Sources → Generate AI Recommendations → 
Build Chat Context → Generate Response → Return Chat + Recommendations
```

#### **2. Direct Recommendations Flow**
```
Direct Request → Recommendations Endpoint → Recommendation Service → 
Fetch All Data Sources → Generate AI Recommendations → 
Enrich with Google Places → Return Structured JSON
```

#### **3. Shared Recommendation Engine**
Both endpoints use the same underlying `RecommendationService` for consistency and maintainability.

## 🚀 Quick Start

### **Prerequisites**
- Python 3.8+
- Google Cloud Project with Vertex AI enabled
- Service account with Vertex AI roles, or Application Default Credentials
- (Optional) Google Places API key
- (Optional) Properties API key
- (Optional) Conversations API key

### **Installation**

1. **Clone and setup**
```bash
git clone <your-repo>
cd GuestRecommendationAPI
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Google Cloud Authentication**
```bash
# Option 1: Service Account (Recommended for production)
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

# Option 2: Application Default Credentials (Development)
gcloud auth application-default login

# Option 3: Workload Identity (GKE/GCP)
# Automatically handled when running on Google Cloud
```

3. **Environment Configuration**
```bash
cp .env.example .env
# Edit .env with your Google Cloud project details
```

4. **Start the server**
```bash
python start_server.py
```

### **Environment Variables**
```bash
# Required: Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your_google_cloud_project_id
GOOGLE_CLOUD_LOCATION=us-east4

# Optional: Service Account Configuration
USE_SERVICE_ACCOUNT=true
SERVICE_ACCOUNT_FILE=/path/to/service-account-key.json

# Optional but recommended
GOOGLE_PLACES_API_KEY=your_google_places_api_key
PROPERTIES_API_KEY=your_properties_api_key
CONVERSATIONS_API_KEY=your_conversations_api_key

# Server settings
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

## 📚 API Endpoints

### **Base URL**: `/api/v1`

#### **1. Chat Endpoint** - `POST /api/v1/chat`
Interactive chat with conversation history and contextual responses.

**Request:**
```json
{
  "reservation_id": "142766272",
  "message": "I'm looking for good Italian restaurants near the hotel",
  "conversation_history": [],
  "include_conversation_context": true
}
```

**Response:**
```json
{
  "message_id": "msg_20250116_143022_1234",
  "response": "I'd be happy to help you find great Italian restaurants! Based on your location in New Haven...",
  "recommendations": [...],
  "conversation_summary": "Guest requested Italian restaurant recommendations",
  "timestamp": "2025-01-16T14:30:22.123Z"
}
```

#### **2. Direct Recommendations Endpoint** - `POST /api/v1/recommendations/generate`
One-time JSON recommendations without chat interaction.

**Request:**
```json
{
  "reservation_id": "142766272",
  "include_conversation_context": true,
  "max_recommendations": 5
}
```

**Response:**
```json
{
  "reservation_id": "142766272",
  "guest_name": "Benjamin Berlin",
  "destination": "New Haven, Aura",
  "stay_dates": "2025-01-16 to 2025-01-20",
  "group_type": "couple",
  "recommendations": [...],
  "generated_at": "2025-01-16T14:30:22.123Z",
  "personalization_summary": "Recommendations tailored for a couple staying 4 nights in downtown New Haven"
}
```

#### **3. Reservation Details** - `GET /api/v1/reservations/{id}`
Get comprehensive reservation information for debugging and verification.

#### **4. Health Check** - `GET /health`
Application health and status information.

#### **5. Root** - `GET /`
API information and endpoint listing.

## 🔧 Configuration

### **Core Settings**
- **AI Model**: Configurable Google Gemini model via Vertex AI (default: gemini-2.5-pro)
- **Temperature**: AI response creativity (default: 0.3)
- **Google Cloud**: Project ID and location configuration
- **Authentication**: Service account, ADC, or Workload Identity
- **Timeouts**: Configurable API timeouts
- **Logging**: Structured logging with configurable levels
- **CORS**: Configurable cross-origin settings

### **Data Source Configuration**
- **Reservations API**:  Required - Contains ALL data (guest, property, conversations)
- **Google Places API**: Optional for location enrichment

## 🛡️ Production Features

### **Security & Reliability**
- **Custom Exception Handling**: Structured error responses
- **Request Logging**: Comprehensive request/response logging
- **Rate Limiting**: Configurable rate limiting
- **Trusted Host Middleware**: Production security
- **CORS Configuration**: Flexible cross-origin settings

### **Monitoring & Debugging**
- **Health Checks**: Application status monitoring
- **Structured Logging**: JSON-formatted logs for production
- **Error Tracking**: Detailed error information and context
- **Performance Metrics**: Request duration and response tracking

### **Scalability**
- **Service Layer Architecture**: Clean separation of concerns
- **Async Support**: Non-blocking I/O operations
- **Configurable Timeouts**: Prevents hanging requests
- **Fallback Mechanisms**: Graceful degradation when services fail

## 🔍 Data Sources Integration

### **1. Reservations API** 
- **Endpoint**: `https://api.gptpricing.com/zendesk-comments/ai-summary`
- **Data**: Guest details, dates, location, group size, preferences
- **Status**: Fully integrated and required

### **2. Properties Data** 
- **Source**: Embedded in reservations API response
- **Data**: Building details, amenities, unit info, WiFi, parking, access codes
- **Status**: Fully available and integrated

### **3. Conversations Data** 
- **Source**: Embedded in reservations API response
- **Data**: Guest feedback, preferences, reservation notes, conversation summaries
- **Status**: Fully available and integrated

### **4. Gemini Grounded Tools via Vertex AI** 
- **Maps Integration**: Real-time location data, walking distances, transportation
- **Search Integration**: Current business hours, events, seasonal activities
- **Local Intelligence**: Hidden gems, authentic local spots, current information
- **Status**: Fully integrated for enhanced location-aware recommendations

## 🧪 Testing

### **Run Tests**
```bash
python test_api.py
```

### **Test Coverage**
- Health check endpoint
- Chat endpoint with conversation history
- Direct recommendations endpoint
- Reservation details endpoint
- Error handling and validation

## 🚀 Deployment

### **Development**
```bash
python start_server.py
# Server runs on http://localhost:8000
# Documentation at http://localhost:8000/docs
```

### **Production**
```bash
# Set DEBUG=false in environment
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### **Docker** (Coming Soon)
```bash
docker build -t guest-recommendations .
docker run -p 8000:8000 guest-recommendations
```

## 📊 Performance & Monitoring

### **Metrics Tracked**
- Request duration
- Response status codes
- API key usage status
- Data source availability
- Error rates and types

### **Logging Levels**
- **DEBUG**: Detailed development information
- **INFO**: General application flow
- **WARNING**: Non-critical issues
- **ERROR**: Application errors
- **CRITICAL**: System failures

## 🔧 Troubleshooting

### **Common Issues**

1. **Google Cloud Project Not Set**
    - Ensure `GOOGLE_CLOUD_PROJECT` is set in `.env`
    - Verify your Google Cloud project ID

2. **External APIs Unavailable**
   - System gracefully degrades to fallback recommendations
   - Check network connectivity and API endpoints

3. **Rate Limiting**
   - Configure `RATE_LIMIT_PER_MINUTE` in settings
   - Monitor API usage patterns

### **Debug Mode**
Set `DEBUG=true` in environment for:
- Detailed error messages
- API documentation access
- Development logging

## 🤝 Contributing

### **Development Setup**
1. Fork the repository
2. Create a feature branch
3. Follow the existing code structure
4. Add tests for new functionality
5. Submit a pull request

### **Code Standards**
- Follow PEP 8 style guidelines
- Add type hints for all functions
- Include comprehensive docstrings
- Write unit tests for new features

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For questions or issues:
1. Check the application logs
2. Verify API key configurations
3. Test individual data sources
4. Review the troubleshooting section

---

**Built with ❤️ using FastAPI, LangChain, and Google Cloud Vertex AI**
