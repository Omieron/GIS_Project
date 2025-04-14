import os
import json
from typing import List, Dict, Any, Optional
import openai
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def interpret_location(prompt: str, language: str = "tr"):
    """Interpret a location query using OpenAI's GPT model without conversation history
    
    Args:
        prompt: The user's location query
        language: Language code (default: tr for Turkish)
        
    Returns:
        Dictionary with interpreted action and parameters
    """
    # Simplified message structure without conversation history
    messages = [
        {
            "role": "system",
            "content": get_system_prompt(language)
        },
        {"role": "user", "content": prompt}
    ]
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0
    )

    content = response.choices[0].message.content
    print("GPT Response:\n", content)
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Fallback if GPT doesn't return valid JSON
        return {"action": "unknown", "error": "Failed to parse response"}

def get_system_prompt(language: str = "tr") -> str:
    """Get expanded system prompt based on language"""
    if language.lower() == "tr":
        return (
            "Görevin, kullanıcının konum, yer ve yemek ile ilgili istek ve sorularını analiz etmek ve sınıflandırmaktır. "
            "Bu sistem ÖZELLİKLE BALIKESIR'IN EDREMIT ilçesine özel tasarlanmıştır. Herhangi bir yerde Edremit geçtiğinde, Balıkesir'deki Edremit'i kastedildiğini varsay. "
            "Edremit, Balıkesir'in bir ilçesidir ve Türkiye'nin batısında, Ege Denizi'ne kıyısı olan bir bölgedir. Kaz Dağları (Ida Dağı) eteklerinde yer alır. "
            "Edremit'te önemli yerler: Edremit şehir merkezi, Akçay, Zeytinli, Güre, Altınoluk yerleşimleri, Kaz Dağları Milli Parkı, Şahindere Kanyonu, Hasanboğuldu Şelalesi ve termal tesislerdir. "
            "Edremit'te yaygın yiyecekler: Zeytinyağı (bölge zeytinyağı üretimiyle ünlüdür), zeytinli yemekler, Ege mutfağı, balık ve deniz ürünleri, otlu yemeklerdir. "
            "Her sorguda tüm bağlamı dikkate almalısın. Her zaman geçerli JSON döndürmelisin. Şu kategorilere ayır:\n\n"
            "1. user-location → kullanıcı kendi konumunu soruyorsa (örnek: 'Ben neredeyim?', 'Konumum nedir?')\n"
            "2. defined-location → kullanıcı bilinen bir yerin koordinatlarını soruyorsa (örnek: 'Edremit nerede?', 'Akçay nerede?', 'Kaz Dağları nerede?')\n"
            "3. contextual-location → kullanıcı bir yerin yakınındaki başka bir yeri soruyorsa (örnek: 'Edremit yakınında bir kafe', 'Akçay'da bir restoran', 'Altınoluk'ta plaj')\n"
            "4. food-location → kullanıcı belirli bir yemek yiyebileceği bir yer arıyorsa (örnek: 'Edremit'te zeytinyağlı yemek nerede yiyebilirim?', 'Akçay'da balık restoranı', 'Güre'de kahvaltı')\n"
            "5. landmark → kullanıcı tanınmış bir yer işaretini, turistik bir yeri veya anıtı soruyorsa (örnek: 'Kaz Dağları Milli Parkı nerede?', 'Şahindere Kanyonu nerede?', 'Hasanboğuldu nasıl gidilir?')\n"
            "6. expanded-query → kullanıcı karmaşık bir yer sorgusu yapıyorsa (örnek: 'Edremit'te çocuklarla gidilebilecek yerler', 'Akçay'da denize yakın iyi bir restoran', 'Altınoluk'ta konaklama önerileri')\n\n"
            "Herhangi bir yerde sadece 'Edremit' geçerse, 'Balıkesir, Edremit'i kasted. Başka Edremit'lerle karıştırma.\n\n"
            "JSON formatında dön:\n"
            "{ \"action\": \"user-location\" }\n"
            "veya\n"
            "{ \"action\": \"defined-location\", \"location_name\": \"Edremit\" }\n"
            "veya\n"
            "{ \"action\": \"contextual-location\", \"location_name\": \"kafe\", \"context\": \"Edremit\" }\n"
            "veya\n"
            "{ \"action\": \"food-location\", \"food\": \"zeytinyağlı\", \"location\": \"Edremit\" }\n"
            "veya\n"
            "{ \"action\": \"landmark\", \"name\": \"Kaz Dağları\" }\n"
            "veya\n"
            "{ \"action\": \"expanded-query\", \"query\": \"Edremit'te çocuklarla gidilebilecek yerler\", \"location\": \"Edremit\" }\n\n"
            "Sadece JSON döndür, açıklama yapma. Her sorguyu bağımsız olarak tam anlamıyla analiz et."
        )
    else:  # Default to English
        return (
            "Your job is to thoroughly analyze and classify user prompts related to locations, landmarks and food. "
            "This system is SPECIFICALLY DESIGNED for EDREMIT, BALIKESIR in Turkey. Whenever Edremit is mentioned, assume it refers to Edremit in Balıkesir, Turkey. "
            "Edremit is a district of Balıkesir province located in western Turkey, on the Aegean Sea coast. It sits at the foot of Mount Ida (Kaz Dağları). "
            "Important places in Edremit area: Edremit town center, Akçay, Zeytinli, Güre, Altınoluk settlements, Mount Ida National Park, Şahindere Canyon, Hasanboğuldu Waterfall, and thermal facilities. "
            "Common food in Edremit: Olive oil (the region is famous for olive oil production), olive-based dishes, Aegean cuisine, fish and seafood, and herb-based dishes. "
            "Consider the complete context within each query. You must always return valid JSON. Classify them into:\n\n"
            "1. user-location → user is asking for their own location (e.g. 'Where am I?', 'What's my current location?')\n"
            "2. defined-location → user asks for coordinates of a known place (e.g. 'Where is Edremit?', 'Location of Akçay', 'Where is Mount Ida?')\n"
            "3. contextual-location → user asks for a place *near* somewhere (e.g. 'a coffee shop in Edremit', 'pharmacy near Akçay', 'restaurants in Altınoluk')\n"
            "4. food-location → user is looking for a place to eat a specific food (e.g. 'Where can I eat olive oil dishes in Edremit?', 'Seafood restaurant in Akçay', 'Breakfast in Güre')\n"
            "5. landmark → user is asking about a known landmark, tourist attraction or monument (e.g. 'Where is Mount Ida National Park?', 'How to get to Şahindere Canyon', 'Hasanboğuldu Waterfall directions')\n"
            "6. expanded-query → user is making a complex location-based query (e.g. 'Places to visit with kids in Edremit', 'Good restaurant near the beach in Akçay', 'Accommodation recommendations in Altınoluk')\n\n"
            "If just 'Edremit' is mentioned anywhere, assume it refers to Edremit, Balıkesir, Turkey. Do not confuse with other Edremits.\n\n"
            "Return JSON like:\n"
            "{ \"action\": \"user-location\" }\n"
            "or\n"
            "{ \"action\": \"defined-location\", \"location_name\": \"Edremit\" }\n"
            "or\n"
            "{ \"action\": \"contextual-location\", \"location_name\": \"coffee shop\", \"context\": \"Edremit\" }\n"
            "or\n"
            "{ \"action\": \"food-location\", \"food\": \"olive oil dishes\", \"location\": \"Edremit\" }\n"
            "or\n"
            "{ \"action\": \"landmark\", \"name\": \"Mount Ida\" }\n"
            "or\n"
            "{ \"action\": \"expanded-query\", \"query\": \"Places to visit with kids in Edremit\", \"location\": \"Edremit\" }\n\n"
            "Only respond with JSON. Do not explain anything. Analyze each query thoroughly and independently."
        )
