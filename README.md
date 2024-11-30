
# Travel Planning Assistant

This application is an intelligent travel planning assistant built using OpenAI's API. It leverages modular agents to handle specific tasks, including gathering user preferences, creating travel itineraries, optimizing plans, and fetching weather data. The application supports both GPT-based and LLaMA-based models.

## Features

- **Dynamic User Interaction**: Understands user input and asks follow-up questions to gather necessary details.
- **Modular Agents**:
  - **Questionnaire Agent**: Collects missing details like city, budget, dates, interests, etc.
  - **Planner Agent**: Creates a detailed travel itinerary.
  - **Optimization Agent**: Refines travel plans based on user constraints.
  - **Weather Agent**: Fetches weather data for the travel destination.
- **Routing Logic**: Ensures smooth transitions between agents based on available data.

---

## Installation

### Prerequisites

1. Python 3.8 or later
2. Install the `openai` library:
   ```bash
   pip install openai
   ```

3. Ensure you have an API key for OpenAI or a local instance of LLaMA.

### Configuration

- Update the API key in the code:
  - For GPT-based models, replace the `api_key` in the `OpenAI` client initialization.
  - For LLaMA-based models, configure the `base_url` and `api_key`.

---

## Usage

### Setting Up the Model

Modify the `use_llama` flag to switch between GPT-based and LLaMA-based models:

```python
use_llama = False  # Set to True for LLaMA-based models
```

### Running the Application
you can run the application with
   ```bash
   python main.py
   ```
the app can be accessed at 
  `http://127.0.0.1:8001/frontend/index.html`



The primary function for user interaction is `generate_llm_response`. Use it to input user queries and receive responses from the assistant.

Example:
```python
response = generate_llm_response("I want to plan a trip to Paris in December.")
print(response)
```

### Routing and Agents

The application dynamically selects the appropriate agent based on the user's input:

1. **Questionnaire Agent**: Gathers missing details.
2. **Planner Agent**: Generates the travel itinerary.
3. **Optimization Agent**: Optimizes the travel plan.
4. **Weather Agent**: Provides weather updates.

#### Example Workflow

Input:
```text
"I want to plan a trip to Rome."
```

The assistant will:
1. Use the **Questionnaire Agent** to ask follow-up questions (e.g., "What is your budget?" or "What are your interests?").
2. Once sufficient details are collected, call the **Planner Agent** to create an itinerary.
3. Optimize the itinerary with the **Optimization Agent** if required.
4. Fetch weather details with the **Weather Agent**.

---

## File Structure

- **Agents**:
  - `questionnaire_Agent`: Gathers user preferences.
  - `Planner_Agent`: Generates a detailed travel plan.
  - `Optimization_Agent`: Optimizes the travel itinerary.
  - `Weather_Agent`: Fetches weather information.
- **Routing Logic**:
  - `function_mapper`: Maps agent names to their implementations.
  - `function_call`: Handles dynamic routing to agents.
- **Main Functionality**:
  - `generate_llm_response`: Core interaction function for user queries.

---

## Development

### Adding New Features

To add a new agent:
1. Define the agent function similar to existing ones.
2. Update the `tools` list with the new agent's details.
3. Map the agent in the `function_mapper` function.

---

## Example Agents

### Questionnaire Agent
Used to ask follow-up questions and collect user preferences.

**Example Input**:
```text
"I want to plan a one-day trip in Paris."
```

**Response**:
```text
"Great! What is your budget and timeframe for the trip?"
```

### Planner Agent
Generates a detailed travel itinerary.

**Example Input**:
```text
"Plan a one-day trip to Paris with a budget of $200."
```

**Response**:
```text
"Day 1:
9:00 AM - Eiffel Tower: $25
11:00 AM - Louvre Museum: $17
..."
```

---

