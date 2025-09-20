from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os
from typing import Optional
from dotenv import load_dotenv
load_dotenv()

router = APIRouter()

# Initialize OpenAI client
try:
    client = OpenAI(
        base_url=os.getenv("base_url"),
        api_key="ollama",  # required but not used by Ollama
    )
except Exception as e:
    print(f"Warning: Could not initialize OpenAI client: {e}")
    client = None

# Request models
class ChatRequest(BaseModel):
    user_message: str
    age_group: Optional[str] = "general"
    knowledge_level: Optional[str] = "beginner"
    language: Optional[str] = "english"
    subject: Optional[str] = "climate_science"
    location: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    suggested_topics: list[str] = []

# Enhanced system prompt for climate tutor
SYSTEM_PROMPT = """
You are ClimateBuddy, an AI tutor specializing in climate science education. Your mission is to:

1. Explain climate science concepts in simple, clear terms
2. Adapt explanations to the user's age, knowledge level, and language preferences
3. Use local examples and relatable analogies when possible
4. Encourage actionable steps and connect lessons to real-life behavior
5. Be encouraging, patient, and supportive
6. Provide accurate, science-based information
7. Suggest related topics for further learning
8. Incorporate location-specific climate data when available
9. Focus on the specific subject area requested by the user

Guidelines:
- For children (under 12): Use simple words, analogies, and visual descriptions
- For teenagers (13-18): Include more scientific details but keep explanations accessible
- For adults: Provide comprehensive explanations with scientific context
- Always end with a practical action the user can take
- If asked about complex topics, break them into smaller, digestible parts
- Use positive, hopeful language while being honest about challenges
- When location is provided, use local climate examples and data
- Adapt content to the specific subject area (climate_science, renewable_energy, sustainability, etc.)
"""

# Climate science topics for suggestions
CLIMATE_TOPICS = [
    "Greenhouse Effect",
    "Carbon Footprint",
    "Renewable Energy",
    "Ocean Acidification",
    "Deforestation",
    "Climate Adaptation",
    "Weather vs Climate",
    "Biodiversity Loss",
    "Sustainable Living",
    "Climate Solutions"
]

# Available subjects for the AI tutor
AVAILABLE_SUBJECTS = {
    "climate_science": {
        "name": "Climate Science",
        "description": "Core climate science concepts and mechanisms",
        "topics": ["Greenhouse Effect", "Global Warming", "Climate Models", "Atmospheric Science"]
    },
    "renewable_energy": {
        "name": "Renewable Energy",
        "description": "Clean energy sources and technologies",
        "topics": ["Solar Power", "Wind Energy", "Hydroelectric", "Geothermal Energy"]
    },
    "sustainability": {
        "name": "Sustainability",
        "description": "Sustainable living and environmental practices",
        "topics": ["Carbon Footprint", "Sustainable Living", "Green Technology", "Environmental Conservation"]
    },
    "climate_impacts": {
        "name": "Climate Impacts",
        "description": "Effects of climate change on ecosystems and society",
        "topics": ["Sea Level Rise", "Extreme Weather", "Biodiversity Loss", "Food Security"]
    },
    "climate_solutions": {
        "name": "Climate Solutions",
        "description": "Actions and technologies to address climate change",
        "topics": ["Carbon Capture", "Climate Adaptation", "Policy Solutions", "Individual Actions"]
    }
}

@router.post("/", response_model=ChatResponse)
async def chat_with_tutor(request: ChatRequest):
    """
    Chat with the AI climate tutor
    """
    try:
        if client is None:
            # Fallback response when AI client is not available
            fallback_response = f"""
            Hello! I'm ClimateBuddy, your AI climate science tutor. I'm here to help you understand climate science concepts in simple terms.
            
            You asked: "{request.user_message}"
            
            While I'm currently experiencing some technical difficulties with my AI system, I can still help you learn about climate science! Here are some key concepts related to your question:
            
            🌍 Climate vs Weather: Climate is the long-term pattern of weather in a specific area, while weather is what you see day-to-day.
            
            🌡️ Greenhouse Effect: This is how Earth stays warm enough for life. Certain gases in our atmosphere trap heat from the sun.
            
            💡 What you can do: Start by learning about your carbon footprint and how small changes in daily habits can make a big difference!
            
            Please try again in a few moments, or explore our interactive dashboard to learn more about climate data!
            """
            
            return ChatResponse(
                reply=fallback_response,
                suggested_topics=["Greenhouse Effect", "Carbon Footprint", "Climate vs Weather"]
            )
        
        # Customize system prompt based on user preferences
        location_context = f"\n- User Location: {request.location}" if request.location else ""
        personalized_prompt = f"{SYSTEM_PROMPT}\n\nUser Profile:\n- Age Group: {request.age_group}\n- Knowledge Level: {request.knowledge_level}\n- Language: {request.language}\n- Subject Focus: {request.subject}{location_context}\n\nPlease adapt your response accordingly and focus on the {request.subject} subject area."
        
        messages = [
            {"role": "system", "content": personalized_prompt},
            {"role": "user", "content": request.user_message}
        ]
        
        response = client.chat.completions.create(
            model="llama3.1:latest",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        assistant_reply = response.choices[0].message.content
        
        # Generate suggested topics based on the conversation
        suggested_topics = generate_suggested_topics(request.user_message)
        
        return ChatResponse(
            reply=assistant_reply,
            suggested_topics=suggested_topics
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")

@router.get("/topics")
async def get_climate_topics():
    """
    Get list of available climate science topics
    """
    return {"topics": CLIMATE_TOPICS}

@router.get("/subjects")
async def get_available_subjects():
    """
    Get list of available subjects for the AI tutor
    """
    return {"subjects": AVAILABLE_SUBJECTS}

@router.get("/subjects/{subject_id}/topics")
async def get_subject_topics(subject_id: str):
    """
    Get topics for a specific subject
    """
    if subject_id not in AVAILABLE_SUBJECTS:
        raise HTTPException(status_code=404, detail=f"Subject '{subject_id}' not found")
    
    return {
        "subject": AVAILABLE_SUBJECTS[subject_id],
        "topics": AVAILABLE_SUBJECTS[subject_id]["topics"]
    }

@router.get("/explain/{topic}")
async def explain_topic(topic: str, age_group: str = "general", knowledge_level: str = "beginner"):
    """
    Get a detailed explanation of a specific climate topic
    """
    try:
        if client is None:
            # Fallback explanation when AI client is not available
            fallback_explanations = {
                "greenhouse effect": "The greenhouse effect is like a blanket around Earth. Just like a blanket keeps you warm at night, certain gases in our atmosphere trap heat from the sun, keeping our planet warm enough for life to exist.",
                "carbon footprint": "Your carbon footprint is like a trail you leave behind. It's the total amount of greenhouse gases (especially carbon dioxide) that your activities produce. Everything from driving a car to using electricity adds to your footprint.",
                "renewable energy": "Renewable energy comes from sources that never run out, like sunlight, wind, and water. Unlike fossil fuels (coal, oil, gas) that take millions of years to form, renewable energy sources are constantly being replenished by nature.",
                "climate change": "Climate change refers to long-term changes in global temperatures and weather patterns. While climate naturally varies, human activities since the 1800s have been the main driver of climate change, primarily due to burning fossil fuels."
            }
            
            explanation = fallback_explanations.get(topic.lower(), f"Climate science is fascinating! {topic} is an important concept in understanding how our planet works. While I'm experiencing technical difficulties, I encourage you to explore our interactive dashboard to learn more about climate data and trends.")
            
            return {
                "topic": topic,
                "explanation": explanation,
                "related_topics": get_related_topics(topic)
            }
        
        prompt = f"Explain '{topic}' in climate science. Age group: {age_group}, Knowledge level: {knowledge_level}. Make it engaging and include practical examples."
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        response = client.chat.completions.create(
            model="llama3.1:latest",
            messages=messages,
            temperature=0.7,
            max_tokens=600
        )
        
        explanation = response.choices[0].message.content
        
        return {
            "topic": topic,
            "explanation": explanation,
            "related_topics": get_related_topics(topic)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error explaining topic: {str(e)}")

def generate_suggested_topics(user_message: str) -> list[str]:
    """
    Generate relevant topic suggestions based on user message
    """
    message_lower = user_message.lower()
    suggestions = []
    
    # Simple keyword matching for topic suggestions
    topic_keywords = {
        "greenhouse": ["Carbon Footprint", "Renewable Energy"],
        "carbon": ["Greenhouse Effect", "Carbon Footprint"],
        "energy": ["Renewable Energy", "Sustainable Living"],
        "ocean": ["Ocean Acidification", "Biodiversity Loss"],
        "weather": ["Weather vs Climate", "Climate Adaptation"],
        "tree": ["Deforestation", "Biodiversity Loss"],
        "sustainable": ["Sustainable Living", "Climate Solutions"],
        "biodiversity": ["Biodiversity Loss", "Deforestation"],
        "adaptation": ["Climate Adaptation", "Climate Solutions"]
    }
    
    for keyword, topics in topic_keywords.items():
        if keyword in message_lower:
            suggestions.extend(topics)
    
    # Remove duplicates and limit to 3 suggestions
    suggestions = list(set(suggestions))[:3]
    
    # If no specific matches, return general topics
    if not suggestions:
        suggestions = ["Greenhouse Effect", "Renewable Energy", "Sustainable Living"]
    
    return suggestions

def get_related_topics(topic: str) -> list[str]:
    """
    Get related topics for a given climate topic
    """
    related_map = {
        "greenhouse effect": ["Carbon Footprint", "Climate Solutions"],
        "carbon footprint": ["Greenhouse Effect", "Sustainable Living"],
        "renewable energy": ["Climate Solutions", "Sustainable Living"],
        "ocean acidification": ["Biodiversity Loss", "Climate Adaptation"],
        "deforestation": ["Biodiversity Loss", "Carbon Footprint"],
        "climate adaptation": ["Climate Solutions", "Weather vs Climate"],
        "weather vs climate": ["Climate Adaptation", "Greenhouse Effect"],
        "biodiversity loss": ["Deforestation", "Ocean Acidification"],
        "sustainable living": ["Carbon Footprint", "Renewable Energy"],
        "climate solutions": ["Renewable Energy", "Sustainable Living"]
    }
    
    return related_map.get(topic.lower(), ["Greenhouse Effect", "Renewable Energy", "Sustainable Living"])
