
from openai import OpenAI
import json
import os
from markdown import markdown

use_llama = False 
if use_llama :
    model_base="llama3.2"
    client = OpenAI(
        base_url = 'http://localhost:11434/v1',
        api_key='ollama',
    )
else :
    model_base="gpt-4o-mini"
    client = OpenAI(
        api_key= "YOUR_OPENAI_KEY"
    )

router_instructions = """
## Router Agent Instructions

### Overview
You are responsible for understanding user input, asking follow-up questions to gather necessary details, and routing the request to the appropriate tool once all conditions are met.

### Workflow

1. **Gather Context**: Ask targeted questions to collect necessary details (city, budget, timeframe, interests, starting point).
2. **Ask Follow-Up Questions**: Ask 3-4 questions to clarify missing information.
3. **Route to Tools**: Based on gathered info, call the appropriate tool if conditions are met.
4. **Iterative Process**: If data is incomplete, ask more questions before routing to a tool.

### Tools and Conditions

- **Questionnaire_Agent**: Collect missing details (city, budget, timeframe, interests, starting point).
- **Planner_Agent**: Call when all details are available.
- **Optimization_Agent**: Call after itinerary creation to refine based on constraints.
- **Weather_Agent**: Call when city and timeframe are known.

### Routing Logic

- **Partial Input**: If incomplete, use `Questionnaire_Agent` to gather missing details.
- **Complete Input**: Route to `Planner_Agent` for itinerary creation.
- **Post-Planning**: Use `Optimization_Agent` and `Weather_Agent` to refine and adjust the plan.

### Example Workflow

1. **User Input**: "I want to visit Berlin."
   - Ask follow-up questions: "Budget?", "Dates?", "Interests?"
2. Route to `Planner_Agent` once details are provided.
3. After itinerary creation, call `Optimization_Agent` and optionally `Weather_Agent`.

### Tool Usage Rules

- Never call a tool prematurely; ensure all conditions are met.
- Always gather missing data before routing to a tool.
- Prioritize the flow: Start with `Questionnaire_Agent`, then `Planner_Agent`, followed by `Optimization_Agent` and `Weather_Agent` as needed.

"""

def questionnaire_Agent(query) :
    Instructions = """
      You are a question asking agent who is Used to gather user preferences so ask questions to gather info relavant to
        - **User Preferences**:  
        - City to visit  
        - Available timings  
        - Budget  
        - Interests (e.g., culture, adventure, food, shopping)  
        - Ask for a starting location (e.g., hotel).  
      
      ## Fewshot examples : 
      example 1 : 
         User: Hi, I'd like to plan a one-day trip in Rome.
         ai response :Great! Let's get started. What day are you planning for, and what time do you want to start and end your day?
      example 2 : 
         User: I'll be visiting on the 10th of November. I want to start at 9 AM and finish by 6 PM.
         ai response : Noted Could you tell me your interests? For example, do you like historical sites, 
         nature, shopping, or food experiences?
      example 3 :
         User : Hi, I'd like to plan a one-day trip in Rome on dec 1st 
         ai response : whats your budget for the trip?
    """

    response = client.chat.completions.create(
        model=model_base,
        messages=[{"role": "system", "content": Instructions} , {"role": "user", "content": query}],
    )
    response_text = response.choices[0].message.content
    print("completed questionnaire_Agent")
    return markdown(response_text)


def Planner_Agent(query) :
    Instructions = """Generates an comprehensive travel plan itinerary based on user inputs covering relavant places or touristic spots. 
    output in a nice readable txt format with day , time , location , price etc.."""
    response = client.chat.completions.create(
        model=model_base,
        messages=[{"role": "system", "content": Instructions} , {"role": "user", "content": query}],
    )
    response_text = response.choices[0].message.content
    print("completed Planner_Agent")
    return markdown(response_text)


def Optimization_Agent(query) :
    Instructions = """optimize travel paths based on budget, user preferences,original plan and time constraints"""
    response = client.chat.completions.create(
        model=model_base,
        messages=[{"role": "system", "content": Instructions} , {"role": "user", "content": query}],
    )
    response_text = response.choices[0].message.content
    print("completed Optimization_Agent")
    return markdown(response_text)


import logging
import os
import requests
# Add your OpenWeatherMap API key here
OPENWEATHER_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')


def Weather_Agent(query):
    """
    Weather_Agent fetches the weather information either through OpenWeatherMap API
    or uses the language model as a fallback.
    """
    # Extract city and timeframe from the query
    Instructions = """
    You are a weather information assistant. Your task is to extract relevant details about the weather query 
    and respond in a JSON format with the following keys:
    - "city": The name of the city mentioned in the user's query (required).
    - "timeframe": The timeframe for the weather (e.g., "current", "next week", "weekend"). Default to "current" if not mentioned.

    If the city is not mentioned in the query, respond with:
    {"error": "City not specified"}

    If the timeframe is not mentioned, use the default value "current".
    """
    
    response = client.chat.completions.create(
        model=model_base,
        messages=[{"role": "system", "content": Instructions}, {"role": "user", "content": query}],
    )
    response_text = response.choices[0].message.content

    # Assume response_text provides city and timeframe in a structured format
    try:
        # Parse city and optional timeframe
        details = json.loads(response_text)  # Expect structured response
        city = details.get("city")
        timeframe = details.get("timeframe", "current")

        if not city:
            return "Unable to determine the city from your query. Please specify the city."

        # Fetch weather data using OpenWeatherMap API
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        weather_response = requests.get(url)

        if weather_response.status_code == 200:
            weather_data = weather_response.json()
            weather_desc = weather_data['weather'][0]['description']
            temp = weather_data['main']['temp']
            return f"The weather in {city} is currently {weather_desc} with a temperature of {temp}°C."
        else:
            logging.error(f"Weather API Error: {weather_response.status_code} - {weather_response.text}")
            return "Error fetching weather data."

    except Exception as e:
        logging.exception("An error occurred while processing the weather information.")
        # Fallback to LLM
        return markdown(response_text)



tools = [
    {
        "type": "function",
        "function": {
            "name": "questionnaire_Agent",
            "description" : "Used to gather user preferences and ask questions to gather data relavant to trip",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "Planner_Agent",
            "description" : "Generates an comprehensive travel plan itinerary based on user inputs covering relavant places or touristic spots.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "Optimization_Agent",
            "description" : "optimize travel paths based on budget, user preferences,original plan and time constraints",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "Weather_Agent",
            "description" : "fetch the expected weather conditions of the region during the time of visit",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    }
]

def function_mapper(function_name , args) :
    if function_name == "questionnaire_Agent" :
        print("executing questionnaire_Agent")
        return questionnaire_Agent(**args)
    if function_name == "Planner_Agent" :
        print("executing Planner_Agent")
        return Planner_Agent(**args)
    if function_name == "Optimization_Agent" :
        print("executing Optimization_Agent")
        return Optimization_Agent(**args)
    if function_name == "Weather_Agent" :
        print("executing Weather_Agent")
        return Weather_Agent(**args)
    
def function_call(response) :
    tool_calls = response.choices[0].message.tool_calls
    if len(tool_calls) > 0 :
        print("toolcalls = " , tool_calls)
        tool_call = tool_calls[0]
    function_name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    print(args)
    return function_mapper(function_name,args) , function_name
    
context = [
    {"role": "system", "content": router_instructions},
]

def generate_llm_response(text) :
    context.append({"role": "user", "content": text})
    response = client.chat.completions.create(
        model=model_base,
        messages=context,
        tools=tools,
    )
    
    if (response.choices[0].message.tool_calls) :
        response_text , function_name = function_call(response)
        context.append({"role": "function", "name": function_name, "content": json.dumps(response_text)})
        return response_text 
    else :
        response_text = response.choices[0].message.content
        context.append({"role": "assistant", "content": markdown(response_text)})
        return markdown(response_text)

