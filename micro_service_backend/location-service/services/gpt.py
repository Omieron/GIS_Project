import os
import json
import traceback
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
    # Get system prompt and function schema if needed
    system_prompt, function_schema = get_system_prompt(language)
    
    # For simplicity in testing, print the input prompt
    print(f"Input prompt: {prompt}")

    try:
        # Set up function calling parameters if in Turkish
        if language.lower() == "tr":
            # Make the API call with function calling
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Keep consistent, focused responses
                tools=[{"type": "function", "function": function_schema}],
                tool_choice={"type": "function", "function": {"name": "process_location_query"}}
            )
            
            # Extract the function call parameters
            if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
                tool_call = response.choices[0].message.tool_calls[0]
                interpretation = json.loads(tool_call.function.arguments)
                print(f"Function response: {interpretation}")
            else:
                # Fall back to content if tool_calls failed for some reason
                content = response.choices[0].message.content
                print(f"No tool calls found, using content: {content}")
                try:
                    interpretation = json.loads(content)
                except json.JSONDecodeError:
                    interpretation = {"action": "unknown", "error": "Failed to parse response"}
        else:
            # Make standard API call for English
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
            )
            
            # Parse the response content
            content = response.choices[0].message.content
            print(f"Raw response: {content}")
            try:
                interpretation = json.loads(content)
            except json.JSONDecodeError:
                # Fallback if GPT doesn't return valid JSON
                interpretation = {"action": "unknown", "error": "Failed to parse response"}
        
        # Convert 'landmark' action to 'landmark-search' for consistency with function calling
        if interpretation.get('action') == 'landmark':
            interpretation['action'] = 'landmark-search'
            
        # Remap 'name' to 'landmark_name' for better consistency
        if 'name' in interpretation and interpretation.get('action') == 'landmark-search':
            interpretation['landmark_name'] = interpretation['name']
            del interpretation['name']
            
        # Ensure proper function response format
        if interpretation.get('action') not in ["user-location", "defined-location", "contextual-location", "food-location", "landmark-search", "expanded-query"]:
            interpretation['action'] = 'unknown'
        if 'service_type' not in interpretation:
            interpretation['service_type'] = 'default_service'
            
        return interpretation
    
    except Exception as e:
        print(f"Error in interpreting location: {str(e)}")
        traceback_str = traceback.format_exc()
        print(f"Traceback: {traceback_str}")
        
        # More detailed error message with language info
        if language.lower() == "tr":
            error_msg = f"Türkçe komut işlenemedi: {str(e)}"
        else:
            error_msg = f"Error processing English command: {str(e)}"
            
        return {
            "action": "error", 
            "error": error_msg,
            "service_type": "default_service"
        }

def get_system_prompt(language: str = "tr"):
    """Get expanded system prompt based on language"""
    if language.lower() == "tr":
        system_prompt = (
            "Sen bir konum çözümleme ve yorumlama uzmanısın. Öncelikli olarak Edremit, Balıkesir bölgesinde uzmanlaşmış, ama aynı zamanda tüm Türkiye için konum sorgularını işleyebilen bir sistemsin. Kullanıcılardan gelen konum tabanlı sorguları analiz edip, doğru konum türünü ve hizmet türünü belirleyerek JSON formatında döndüreceksin.\n\n"
            
            "KRİTİK ÖNEMLİ KURALLAR:\n"
            "1. TAMAMLANMAMIŞ VEYA BELİRSİZ SORGULAR İÇİN VARSAYILAN OLARAK EDREMİT BÖLGESİNİ KULLAN!\n"
            "   'Sahil kenarı', 'eczane', 'otel', 'restoran' gibi tek başına anlam ifade etmeyen sorgular gelirse,\n"
            "   bunları otomatik olarak 'Edremit'te sahil kenarı', 'Edremit'te bir eczane' olarak yorumla.\n"
            "   Açıkça başka bir lokasyon belirtilmedikçe, TÜM sorguları Edremit bölgesi bağlamında değerlendir.\n\n"
            
            "2. HİÇBİR ZAMAN 'error' VEYA 'unknown' ACTION DÖNDÜRME!\n"
            "   Sorguyu anlamakta zorluk çeksen bile, bir best-effort yanıt döndür.\n"
            "   Belirsiz bir sorgu ise varsayılan olarak 'defined-location' action ile 'edremit' location_name kullan.\n\n"
            
            "3. TÜM SORGULARDA MUTLAKA service_type BELİRLE!\n"
            "   Belirsiz durumlarda 'foursquare_service' kullan.\n\n"
            
            "4. YAZIM HATALARINI VE TÜRKÇE KARAKTER PROBLEMLERİNİ DÜZELT!\n"
            "   'Akcay', 'Altinoluk' gibi girişleri 'Akçay', 'Altınoluk' olarak düzeltmeye çalış.\n"
            "   'Kaz Daglari' -> 'Kaz Dağları', 'Gure' -> 'Güre' olarak yorumla.\n\n"
            
            "TEMEL ODAK - EDREMİT BÖLGESİ:\n"
            "Edremit körfezi şunları içerir: Edremit merkez, Akçay, Altınoluk, Zeytinli, Güre ve çevre bölgeler. Bu alanlarla ilgili sorgularda, yerel bilgi ile detaylı işleme sağla.\n\n"
            
            "İKİNCİL KABİLİYET - TÜM TÜRKİYE:\n"
            "Ayrıca şunlarla sınırlı olmamak üzere diğer Türk şehirleri ve bölgeleri hakkındaki sorguları da işleyebilirsin: İstanbul, Ankara, İzmir, Bursa, Antalya ve Türkiye genelindeki diğer yerler. Ancak bu yerler belirtilmedikçe, varsayılan olarak Edremit bölgesini kullan.\n\n"
            
            "Edremit bölgesi hakkında detaylı bilgi:\n"
            "Edremit: 39.5942 N, 27.0246 E koordinatlarında, Kaz Dağları'nın eteklerinde, zeytin üretimi ve zeytinyağı ile ünlü\n"
            "Akçay: 39.5776 N, 26.9184 E koordinatlarında, plajları, otelleri ve deniz aktiviteleriyle ünlü bir tatil beldesi\n"
            "Altınoluk: 39.5691 N, 26.7353 E koordinatlarında, temiz havası, pansiyon ve apart otelleri ve denizi ile biliniyor\n"
            "Zeytinli: 39.5829 N, 26.9823 E koordinatlarında, zeytin bahçeleriyle ünlü\n"
            "Güre: 39.5866 N, 26.8835 E koordinatlarında, termal kaynaklarıyla ve spa otelleriyle ünlü\n"
            "Kaz Dağları: 39.7083 N, 26.8733 E koordinatlarında, biyoçeşitlilik açısından zengin\n\n"
            
            "Edremit bölgesindeki önemli konaklama yerleri:\n"
            "1. Akçay Sahil Oteli: Akçay'da denize sıfır konumda, 39.5762 N, 26.9174 E\n"
            "2. Altınoluk Hotel: Altınoluk'ta merkezi konumda, 39.5688 N, 26.7355 E\n"
            "3. Güre Termal Resort: Güre'de termal suları olan lüks bir otel, 39.5871 N, 26.8828 E\n"
            "4. Edremit Park Hotel: Edremit şehir merkezinde, 39.5944 N, 27.0239 E\n"
            "5. Zeytinli Butik Otel: Zeytinli'de zeytin bahçeleri arasında, 39.5836 N, 26.9815 E\n"
            
            "SORGU SINIFLANDIRMA TÜRLERİ:\n"
            "1. user-location → Kullanıcı kendi konumunu soruyorsa\n"
            "   Örnek: 'Ben neredeyim?', 'Konumum nedir?', 'Şu an neredeyim?'\n\n"
            
            "2. defined-location → Bilinen bir yerin koordinatlarını soruyorsa\n"
            "   Örnek: 'Edremit nerede?', 'İstanbul nerede?', 'Akçay', 'Kaz Dağları'\n"
            "   NOT: Sadece yer ismi içeren sorgular da ('Akçay', 'Zeytinli' gibi) defined-location olarak değerlendirilmelidir.\n\n"
            
            "3. contextual-location → Bir yerin yakınındaki başka bir yeri soruyorsa\n"
            "   Örnek: 'Edremit yakınında kafe', 'Akçay'da otel', 'Altınoluk'ta market', 'Sahilde restoran'\n\n"
            
            "4. food-location → Belirli bir yemek yiyebileceği bir yer arıyorsa\n"
            "   Örnek: 'Edremit'te zeytinyağlı', 'Akçay'da balık', 'Altınoluk'ta kahvaltı', 'Güre'de akşam yemeği'\n\n"
            
            "5. landmark-search → Tanınmış bir yer işaretini soruyorsa\n"
            "   Örnek: 'Kaz Dağları nerede?', 'Şahindere Kanyonu'na nasıl gidilir?', 'Hasanboğuldu hakkında bilgi'\n\n"
            
            "6. expanded-query → Karmaşık bir yer sorgusu yapıyorsa\n"
            "   Örnek: 'Edremit'te çocuklarla gidilecek yerler', 'Akçay'da denize sıfır restoranlar', 'Altınoluk'ta kahvaltı ve plaj'\n\n"
            
            "SORGU ANALİZİ KURALLARI:\n"
            "1. Her sorguyu analiz ederken, hem konum türünü hem de hizmet türünü MUTLAKA belirlemelisin.\n"
            "2. 'Edremit' ismi nitelenmeden geçerse, varsayılan olarak Balıkesir ilindeki Edremit'i ifade ettiğini kabul et.\n"
            "3. Sadece lokasyon ismi içeren sorgular ('Akçay', 'Altınoluk', 'Güre' gibi) defined-location olarak değerlendirilmelidir.\n"
            "4. Belirsiz sorgularda action_type olarak 'defined-location' kullan ve location_name olarak 'edremit' belirle.\n"
            "5. Action'ın gerektirdiği tüm alanları doldur - örneğin contextual-location için mutlaka location_name ve context alanlarını belirt.\n\n"
            
            "HİZMET TİPİNİ BELİRLEME KRİTERLERİ:\n"
            "- foursquare_service: En yaygın kullanılan servis! Şu tür sorgularda kullan:\n"
            "  * Yeme-içme: 'mekan', 'yer', 'kafe', 'cafe', 'restoran', 'restaurant', 'yeme', 'içme', 'dondurma', 'kahvaltı', 'balık', 'yemek'\n"
            "  * Konaklama: 'otel', 'hotel', 'pansiyon', 'konaklama', 'apart', 'motel'\n"
            "  * Alışveriş: 'eczane', 'market', 'alışveriş', 'mağaza', 'süpermarket', 'bakkal'\n"
            "  * Eğlence: 'bar', 'eğlence', 'gece kulübü', 'disko'\n"
            "  * Hizmet: 'berber', 'kuaför', 'ATM', 'banka', 'postane'\n"
            "  * Varsayılan: Emin değilsen foursquare_service kullan\n\n"
            
            "- maks_service: Bina ve yapı ile ilgili sorgularda kullan:\n"
            "  * Yapılar: 'bina', 'yapı', 'ev', 'konut', 'daire', 'apartman', 'inşaat', 'mimari'\n"
            "  * Kurumlar: 'okul', 'lise', 'üniversite', 'hastane', 'resmi daire', 'belediye'\n\n"
            
            "- overpass_service: Coğrafi özellikler ve yollarla ilgili sorgularda kullan:\n"
            "  * Yollar: 'yol', 'sokak', 'cadde', 'bulvar', 'otoyol', 'navigasyon', 'köprü'\n"
            "  * Doğal alanlar: 'plaj', 'sahil', 'kıyı', 'deniz', 'orman', 'dağ'\n"
            "  * Parklar: 'park', 'bahçe', 'yeşil alan', 'milli park'\n\n"
            
            "- edremit_service: Spesifik Edremit lokasyonları için kullan:\n"
            "  * Sorguda açıkça 'Edremit' bölgesinden bir lokasyon belirtiliyorsa\n"
            "  * Bölgeye özgü landmark'lar için: 'Kaz Dağları', 'Hasanboğuldu', 'Şahindere'\n\n"
            
            "- default_service: Sadece şu durumlarda kullan:\n"
            "  * Konum sorgusunun türünü belirleyemediğin durumlarda\n"
            "  * Yukarıdaki hiçbir kategoriye uymuyorsa\n\n"
            
            "ÖNEMLİ: Eğer hizmet türünü belirleyemiyorsan, varsayılan olarak foursquare_service kullan.\n\n"
            
            "SORGU ÖRNEKLERİ VE BEKLENEN ÇIKTILAR:\n"
            "1. 'Akçay'da otel' → {\"action\": \"contextual-location\", \"location_name\": \"otel\", \"context\": \"Akçay\", \"location_type\": \"hotel\", \"service_type\": \"foursquare_service\"}\n"
            "2. 'Sahilde kahvaltı' → {\"action\": \"contextual-location\", \"location_name\": \"kahvaltı\", \"context\": \"sahil\", \"location_type\": \"restaurant\", \"service_type\": \"foursquare_service\"}\n"
            "3. 'Lise yakınında dondurma' → {\"action\": \"contextual-location\", \"location_name\": \"dondurma\", \"context\": \"lise\", \"location_type\": \"ice cream\", \"service_type\": \"foursquare_service\"}\n"
            "4. 'Edremit' → {\"action\": \"defined-location\", \"location_name\": \"edremit\", \"service_type\": \"edremit_service\"}\n"
            "5. 'Otel' → {\"action\": \"defined-location\", \"location_name\": \"otel\", \"location_type\": \"hotel\", \"service_type\": \"foursquare_service\"}\n"
            "6. 'Zeytinyağlı nerede yenir?' → {\"action\": \"food-location\", \"food\": \"zeytinyağlı\", \"location\": \"edremit\", \"service_type\": \"foursquare_service\"}\n"
            
            "Aşağıdaki fonksiyonu kullanarak sonuç döndür:\n"
        )
        
        # Define function schema for Turkish
        function_schema = {
            "name": "process_location_query",
            "description": "Process a natural language location query about Edremit region and Turkey",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["user-location", "defined-location", "contextual-location", "food-location", "landmark-search", "expanded-query"],
                        "description": "The type of location query being made"
                    },
                    "location_name": {
                        "type": "string",
                        "description": "Primary location being searched for (e.g., 'cafe', 'restaurant', 'Edremit')"
                    },
                    "context": {
                        "type": "string",
                        "description": "Secondary location providing context (e.g., 'near Edremit')"
                    },
                    "location_type": {
                        "type": "string",
                        "description": "Type of location being searched for (e.g., 'school', 'beach', 'restaurant')"
                    },
                    "food": {
                        "type": "string",
                        "description": "Food type when searching for restaurants"
                    },
                    "landmark_name": {
                        "type": "string",
                        "description": "Name of landmark when searching for landmarks"
                    },
                    "query": {
                        "type": "string",
                        "description": "Full query for expanded searches"
                    },
                    "location": {
                        "type": "string",
                        "description": "Location context for expanded queries or food searches"
                    },
                    "service_type": {
                        "type": "string",
                        "enum": ["foursquare_service", "maks_service", "overpass_service", "edremit_service", "default_service"],
                        "description": "Which service should handle this query based on content"
                    }
                },
                "required": ["action", "service_type"]
            }
        }
        return system_prompt, function_schema
    else:  # Default to English
        system_prompt = (
            "Your job is to thoroughly analyze and classify user prompts related to locations, landmarks and food. "
            "This system is SPECIFICALLY DESIGNED for EDREMIT, BALIKESIR in Turkey. Whenever Edremit is mentioned, assume it refers to Edremit in Balıkesir, Turkey. "
            "Edremit is a district of Balıkesir province located in western Turkey, on the Aegean Sea coast. It sits at the foot of Mount Ida (Kaz Dağları). "
            
            "DETAILED INFORMATION ABOUT EDREMIT REGION:\n"
            "1. Settlements:\n"
            "   - Edremit town center: Main center with shopping areas and businesses\n"
            "   - Akçay: Popular beach town, lively in summer, has beaches for swimming\n"
            "   - Zeytinli: Small and quiet settlement surrounded by olive trees\n"
            "   - Güre: Famous for thermal facilities, visited for health tourism\n"
            "   - Altınoluk: Beach town known for clean sea and calm atmosphere\n"
            "   - Kızılkeçili: Mountainous village, suitable for nature hikes\n"
            
            "2. Important Tourist Attractions:\n"
            "   - Mount Ida National Park: Nature wonder with rich flora and fauna\n"
            "   - Hasanboğuldu Waterfall: Natural beauty subject of legends\n"
            "   - Sırtçamçam Waterfall: Waterfall accessible by a short hike\n"
            "   - Zeytinli Ethnography Museum: Museum preserving local history and culture\n"
            "   - Sıkrıbuğaz Canyon: Ideal route for nature enthusiasts\n"
            "   - Edremit Gulf: Gulf famous for its stunning views\n"
            
            "3. Educational Institutions:\n"
            "   - Edremit Anatolian High School: Well-established school in town center\n"
            "   - 10 Kasım Vocational High School: School providing vocational education\n"
            "   - Edremit Science High School: Elite high school known for academic success\n"
            "   - Edremit Primary School: Basic education institution in town center\n"
            "   - Altınoluk Primary School: School in Altınoluk town\n"
            
            "4. Dining Spots:\n"
            "   - Akçay Promenade: Many cafes and restaurants line the seaside, especially popular for breakfast\n"
            "   - Edremit Bazaar: Traditional restaurants offering local flavors\n"
            "   - Altınoluk Marina: Ideal for fish restaurants and seafood\n"
            "   - Küçükkuyu Beach: Famous for its cafes and ice cream shops\n"
            "   - Zeytinli Village Breakfasts: Village breakfasts prepared with organic products\n"
            
            "5. Shopping and Market Points:\n"
            "   - Novada Mall: Largest shopping center in Edremit\n"
            "   - Körfez Mall: Shopping center with various stores\n"
            "   - Edremit Marketplace: Large local market set up on Tuesdays\n"
            "   - Akçay Bazaar: Shops selling souvenirs and local products\n"
            
            "Consider the complete context within each query. You must always return valid JSON.\n\n"
            
            "SERVICE TYPES:\n"
            "Users may request four different service types, and it's important to determine which one:\n"
            "1. foursquare_service → user wants to use Foursquare data service (for cafes, restaurants, places, etc.)\n"
            "2. maks_service → user wants to use MAKS building data service (for buildings, structures, etc.)\n"
            "3. overpass_service → user wants to use Overpass service (for roads, streets, highways, etc.)\n"
            "4. default_service → user has not specified a particular service (just location)\n\n"
            
            "LOCATION TYPES:\n"
            "Additionally, you should determine the type of location query:\n"
            "1. user-location → user is asking for their own location (e.g. 'Where am I?', 'What's my current location?')\n"
            "2. defined-location → user asks for coordinates of a known place (e.g. 'Where is Edremit?', 'Location of Akçay', 'Where is Mount Ida?')\n"
            "3. contextual-location → user asks for a place *near* somewhere (e.g. 'a coffee shop in Edremit', 'pharmacy near Akçay', 'restaurants in Altınoluk')\n"
            "4. food-location → user is looking for a place to eat a specific food (e.g. 'Where can I eat olive oil dishes in Edremit?', 'Seafood restaurant in Akçay', 'Breakfast in Güre')\n"
            "5. landmark → user is asking about a known landmark, tourist attraction or monument (e.g. 'Where is Mount Ida National Park?', 'How to get to Şahindere Canyon', 'Hasanboğuldu Waterfall directions')\n"
            "6. expanded-query → user is making a complex location-based query (e.g. 'Places to visit with kids in Edremit', 'Good restaurant near the beach in Akçay', 'Accommodation recommendations in Altınoluk')\n\n"
            
            "When analyzing each query, you should determine both the location type and the service type. If just 'Edremit' is mentioned anywhere, assume it refers to Edremit, Balıkesir, Turkey. Do not confuse with other Edremits.\n\n"
            
            "CRITERIA FOR DETERMINING SERVICE TYPE:\n"
            "- foursquare_service: If the query contains words like 'foursquare', 'place', 'venue', 'cafe', 'restaurant', 'eating', 'drinking', 'market', 'shop', 'shopping'\n"
            "- maks_service: If the query contains words like 'maks', 'building', 'structure', 'house', 'residence', 'apartment', 'construction', 'architecture'\n"
            "- overpass_service: If the query contains words like 'overpass', 'road', 'street', 'avenue', 'boulevard', 'highway', 'direction', 'navigation'\n"
            "- default_service: If none of the above words are present\n\n"
            
            "Return JSON like:\n"
            "{ \"action\": \"user-location\", \"service_type\": \"default_service\" }\n"
            "or\n"
            "{ \"action\": \"defined-location\", \"location_name\": \"Edremit\", \"service_type\": \"foursquare_service\" }\n"
            "or\n"
            "{ \"action\": \"contextual-location\", \"location_name\": \"coffee shop\", \"context\": \"Edremit\", \"service_type\": \"foursquare_service\" }\n"
            "or\n"
            "{ \"action\": \"food-location\", \"food\": \"olive oil dishes\", \"location\": \"Edremit\", \"service_type\": \"foursquare_service\" }\n"
            "or\n"
            "{ \"action\": \"landmark\", \"name\": \"Mount Ida\", \"service_type\": \"default_service\" }\n"
            "or\n"
            "{ \"action\": \"expanded-query\", \"query\": \"Places to visit with kids in Edremit\", \"location\": \"Edremit\", \"service_type\": \"default_service\" }\n\n"
            
            "EXAMPLE EVALUATIONS:\n"
            "- 'Show me foursquare data for a nice cafe in Edremit' → service_type: foursquare_service\n"
            "- 'I want to see buildings in Akçay' → service_type: maks_service\n"
            "- 'Show roads near Mount Ida' → service_type: overpass_service\n"
            "- 'Where is Edremit?' → service_type: default_service\n\n"
            
            "Only respond with JSON. Do not explain anything. Analyze each query thoroughly and independently."
        )
        
        # English doesn't use function calling in this implementation
        return system_prompt, None
