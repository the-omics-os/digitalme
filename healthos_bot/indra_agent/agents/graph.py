"""LangGraph multi-agent graph using supervisor architecture.

This uses the langgraph_supervisor package for automatic handoff handling
and simplified agent coordination. Agents are created using factory functions
following the lobster pattern.
"""

import logging

from indra_agent.agents.indra_query_agent import indra_query_agent
from indra_agent.agents.state import OverallState
from indra_agent.agents.supervisor import create_supervisor_prompt
from indra_agent.agents.web_researcher import web_research_agent
from indra_agent.config.agent_config import (
    INDRA_QUERY_AGENT_CONFIG,
    WEB_RESEARCHER_CONFIG,
)
from indra_agent.config.settings import get_settings
from indra_agent.langgraph_supervisor import (
    create_handoff_tool,
    create_supervisor,
)
from indra_agent.llm_factory import LLMFactory

logger = logging.getLogger(__name__)


def create_causal_discovery_graph():
    """Create the LangGraph workflow for causal discovery using supervisor pattern.

    This function follows the lobster pattern by:
    1. Calling factory functions to create worker agents
    2. Creating supervisor with handoff tools
    3. Compiling the workflow

    Returns:
        Compiled LangGraph workflow
    """
    logger.info("Creating causal discovery graph with supervisor architecture")

    settings = get_settings()

    # ==========================================
    # Create Worker Agents using Factory Functions
    # ==========================================

    logger.debug("Creating INDRA query agent")
    indra_agent = indra_query_agent(
        callback_handler=None,
        agent_name="indra_query_agent",
        handoff_tools=None,  # Supervisor handles handoffs
    )

    logger.debug("Creating web research agent")
    web_agent = web_research_agent(
        callback_handler=None,
        agent_name="web_researcher",
        handoff_tools=None,  # Supervisor handles handoffs
    )

    # ==========================================
    # Create Supervisor
    # ==========================================

    logger.debug("Creating supervisor agent")
    supervisor_llm = LLMFactory.create_llm(
        model_config={
            "model_id": settings.agent_model,
            "region_name": settings.aws_region,
            "temperature": 0.0,
        },
        agent_name="supervisor",
    )

    # Create handoff tools for delegation
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

    # Create supervisor workflow using create_supervisor
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

    # Compile the graph
    graph = workflow.compile()

    logger.info("Causal discovery graph compiled successfully with supervisor pattern")
    return graph
