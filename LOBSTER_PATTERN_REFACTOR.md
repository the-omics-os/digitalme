# Lobster Pattern Refactor - Complete ✅

## Overview

The digitalme project has been successfully refactored to follow the **exact same pattern** as lobster's `data_expert.py`. All agents now use factory functions with tools defined inside, matching the proven lobster architecture.

---

## What Changed

### 1. **indra_query_agent.py** - Factory Function Pattern ✅

**Before:** Class-based agent with 277 lines, manual `__call__` method, async cleanup

**After:** Factory function with 191 lines following lobster pattern:
```python
def indra_query_agent(
    callback_handler=None,
    agent_name: str = "indra_query_agent",
    handoff_tools: List = None,
):
    """Create INDRA query specialist agent."""

    # Initialize services
    grounding_service = GroundingService()
    indra_service = INDRAService()
    graph_builder = GraphBuilderService()

    # Initialize LLM
    llm = ChatBedrock(...)

    # Define tools inside factory
    @tool
    async def analyze_biological_pathways(...) -> str:
        # Use services for logic
        paths = await indra_service.find_causal_paths(...)
        causal_graph = graph_builder.build_causal_graph(...)
        return json.dumps(result)

    @tool
    def ground_entities(...) -> str:
        grounded = grounding_service.ground_entities(entities)
        return json.dumps(result)

    # Combine tools
    tools = [analyze_biological_pathways, ground_entities] + (handoff_tools or [])

    # Return react agent
    return create_react_agent(
        model=llm,
        tools=tools,
        prompt=config.system_prompt,
        name=agent_name,
        state_schema=OverallState,
    )
```

**Key Tools:**
- `analyze_biological_pathways` - Query INDRA for causal paths
- `ground_entities` - Map entity names to database IDs

---

### 2. **web_researcher.py** - Factory Function Pattern ✅

**Before:** Class-based agent with 160 lines, manual `__call__` method, async cleanup

**After:** Factory function with 230 lines following lobster pattern:
```python
def web_research_agent(
    callback_handler=None,
    agent_name: str = "web_researcher",
    handoff_tools: List = None,
):
    """Create web research specialist agent."""

    # Initialize services
    web_service = WebDataService()

    # Initialize LLM
    llm = ChatBedrock(...)

    # Define tools inside factory
    @tool
    def analyze_environmental_data(location_history: list[dict]) -> str:
        environmental_data = web_service.analyze_location_history(location_history)
        return json.dumps(result)

    @tool
    async def get_current_pollution(city: str) -> str:
        data = await web_service.get_pollution_data(city)
        return json.dumps(data)

    @tool
    def calculate_exposure_delta(old_location: str, new_location: str) -> str:
        delta_data = web_service.calculate_exposure_delta(old_location, new_location)
        return json.dumps(result)

    # Combine tools
    tools = [analyze_environmental_data, get_current_pollution, calculate_exposure_delta] + (handoff_tools or [])

    # Return react agent
    return create_react_agent(
        model=llm,
        tools=tools,
        prompt=config.system_prompt,
        name=agent_name,
        state_schema=OverallState,
    )
```

**Key Tools:**
- `analyze_environmental_data` - Analyze location history for pollution exposure
- `get_current_pollution` - Fetch current air quality for a city
- `calculate_exposure_delta` - Calculate pollution change between locations

---

### 3. **graph.py** - Simplified Using Factory Functions ✅

**Before:** 266 lines with inline tool definitions

**After:** 106 lines calling factory functions:
```python
def create_causal_discovery_graph():
    """Create the LangGraph workflow using factory functions."""

    # Create Worker Agents using Factory Functions
    indra_agent = indra_query_agent(
        agent_name="indra_query_agent",
        handoff_tools=None,
    )

    web_agent = web_research_agent(
        agent_name="web_researcher",
        handoff_tools=None,
    )

    # Create Supervisor
    supervisor_llm = ChatBedrock(...)

    handoff_tools = [
        create_handoff_tool(
            agent_name="indra_query_agent",
            name="delegate_to_indra_query",
            description=INDRA_QUERY_AGENT_CONFIG.handoff_tool_description,
        ),
        create_handoff_tool(
            agent_name="web_researcher",
            name="delegate_to_web_researcher",
            description=WEB_RESEARCHER_CONFIG.handoff_tool_description,
        ),
    ]

    # Create supervisor workflow
    workflow = create_supervisor(
        agents=[indra_agent, web_agent],
        model=supervisor_llm,
        prompt=create_supervisor_prompt(),
        tools=handoff_tools,
        state_schema=OverallState,
        output_mode="last_message",
        add_handoff_messages=True,
        add_handoff_back_messages=True,
        include_agent_name="inline",
        supervisor_name="supervisor",
    )

    return workflow.compile()
```

---

## Architecture Comparison

### Lobster Pattern (data_expert.py)
```python
def data_expert(data_manager, callback_handler, agent_name, handoff_tools):
    # Initialize services
    geo_service = GEOService(data_manager)

    # Initialize LLM
    llm = create_llm(...)

    # Define tools
    @tool
    def download_geo_dataset(...):
        result = geo_service.download_dataset(...)
        return result

    # Combine tools
    tools = base_tools + (handoff_tools or [])

    # Return react agent
    return create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt,
        name=agent_name,
        state_schema=DataExpertState,
    )
```

### DigitalMe Pattern (NOW MATCHES!) ✅
```python
def indra_query_agent(callback_handler, agent_name, handoff_tools):
    # Initialize services
    indra_service = INDRAService()

    # Initialize LLM
    llm = ChatBedrock(...)

    # Define tools
    @tool
    async def analyze_biological_pathways(...):
        paths = await indra_service.find_causal_paths(...)
        return json.dumps(result)

    # Combine tools
    tools = base_tools + (handoff_tools or [])

    # Return react agent
    return create_react_agent(
        model=llm,
        tools=tools,
        prompt=config.system_prompt,
        name=agent_name,
        state_schema=OverallState,
    )
```

**Pattern is IDENTICAL!** ✅

---

## File Changes Summary

| File | Before | After | Change |
|------|--------|-------|--------|
| **indra_query_agent.py** | 277 lines (class) | 191 lines (factory) | **-86 lines** ✅ |
| **web_researcher.py** | 160 lines (class) | 230 lines (factory) | **+70 lines** (more tools) |
| **graph.py** | 266 lines (inline tools) | 106 lines (calls factories) | **-160 lines** ✅ |
| **Total** | 703 lines | 527 lines | **-176 lines** ✅ |

---

## Key Benefits

### ✅ **Consistent with Lobster**
- Exact same factory function pattern
- Tools defined inside factory with `@tool` decorator
- Services handle logic, tools are thin wrappers
- Returns `create_react_agent()`

### ✅ **Better Separation of Concerns**
- **Services**: Contain business logic (INDRAService, WebDataService)
- **Tools**: Thin wrappers that call services and format results
- **Agents**: Factory functions that wire everything together
- **Graph**: Simple orchestration, no business logic

### ✅ **Easier to Test**
- Can test services independently
- Can test agents by calling factory functions
- Can mock services in tests
- Tools are easy to unit test

### ✅ **More Maintainable**
- Tools live with their agents (not scattered in graph.py)
- Easy to add new tools to an agent
- Clear ownership and responsibility
- Services can be reused across agents

### ✅ **Better Code Reuse**
- Factory functions can be imported anywhere
- Services can be shared between agents
- Tools can be extended with handoff_tools
- Pattern is proven and scalable

---

## Pattern Checklist

Comparing with lobster's `data_expert.py`:

- ✅ Factory function signature matches
- ✅ Services initialized at top
- ✅ LLM created with config
- ✅ Tools defined with `@tool` decorator inside factory
- ✅ Tools use services for logic
- ✅ Tools return strings (JSON when needed)
- ✅ Base tools combined with handoff_tools
- ✅ System prompt from config
- ✅ Returns `create_react_agent()`
- ✅ State schema specified

**100% Pattern Compliance!** 🎯

---

## How to Use

### Basic Usage
```python
from indra_agent.agents.graph import create_causal_discovery_graph

# Create the graph
graph = create_causal_discovery_graph()

# Invoke with a query
result = graph.invoke({
    "messages": [
        {"role": "user", "content": "What's the relationship between PM2.5 and inflammation?"}
    ],
    "request_id": "test-123",
    "query": {"text": "What's the relationship between PM2.5 and inflammation?"},
    "user_context": {},
    "options": {}
}, {"recursion_limit": 50})
```

### Adding a New Agent
To add a new agent, follow the same pattern:

1. **Create factory function** in `agents/new_agent.py`:
```python
def new_agent(callback_handler=None, agent_name="new_agent", handoff_tools=None):
    # Initialize services
    new_service = NewService()

    # Initialize LLM
    llm = ChatBedrock(...)

    # Define tools
    @tool
    def new_tool(...):
        result = new_service.do_something(...)
        return json.dumps(result)

    # Combine tools
    tools = [new_tool] + (handoff_tools or [])

    # Return react agent
    return create_react_agent(...)
```

2. **Add to graph.py**:
```python
from indra_agent.agents.new_agent import new_agent

new_agent_instance = new_agent(agent_name="new_agent")
```

3. **Add handoff tool**:
```python
create_handoff_tool(
    agent_name="new_agent",
    name="delegate_to_new_agent",
    description="Delegate to new agent for X tasks"
)
```

---

## Testing Recommendations

### Unit Tests for Services
```python
def test_indra_service_find_paths():
    service = INDRAService()
    paths = await service.find_causal_paths("PM2.5", "CRP", max_depth=4)
    assert len(paths) > 0
```

### Integration Tests for Agents
```python
def test_indra_query_agent():
    agent = indra_query_agent()
    result = agent.invoke({
        "messages": [{"role": "user", "content": "Find PM2.5 -> CRP paths"}]
    })
    assert "causal_graph" in result
```

### End-to-End Tests for Graph
```python
def test_causal_discovery_graph():
    graph = create_causal_discovery_graph()
    result = graph.invoke({
        "messages": [{"role": "user", "content": "What's the link between pollution and health?"}]
    })
    assert result["messages"][-1]["content"]
```

---

## Migration Complete! 🎉

Your digitalme project now follows the **exact same architecture** as lobster:

- ✅ Factory functions for agents
- ✅ Tools defined inside factories
- ✅ Services contain business logic
- ✅ Supervisor handles orchestration
- ✅ Graph.py is clean and simple

The pattern is proven, scalable, and maintainable. You can now easily add new agents by following the same template!
