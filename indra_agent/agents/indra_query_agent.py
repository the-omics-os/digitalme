"""INDRA Query Agent for biological pathway analysis and causal graph construction.

This agent is responsible for querying the INDRA bio-ontology database,
grounding biological entities, and constructing causal graphs from pathways.
"""

import json
import logging
from typing import List

from langchain_aws import ChatBedrock
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

from indra_agent.agents.state import OverallState
from indra_agent.config.agent_config import INDRA_QUERY_AGENT_CONFIG
from indra_agent.config.settings import get_settings
from indra_agent.services.graph_builder import GraphBuilderService
from indra_agent.services.grounding_service import GroundingService
from indra_agent.services.indra_service import INDRAService

logger = logging.getLogger(__name__)


def indra_query_agent(
    callback_handler=None,
    agent_name: str = "indra_query_agent",
    handoff_tools: List = None,
):
    """
    Create INDRA query specialist agent for biological pathway analysis.

    This expert agent specializes in:
    - Grounding biological entities to database identifiers (MESH, HGNC, GO, CHEBI)
    - Querying INDRA database for causal paths between entities
    - Ranking paths by evidence count and confidence
    - Building structured causal graphs with nodes and edges
    - Calculating effect sizes and temporal lags from INDRA belief scores

    Args:
        callback_handler: Optional callback handler for LLM interactions
        agent_name: Name identifier for the agent instance
        handoff_tools: Additional tools for inter-agent communication

    Returns:
        Configured ReAct agent with INDRA analysis capabilities
    """

    settings = get_settings()
    config = INDRA_QUERY_AGENT_CONFIG

    # Initialize LLM
    llm = ChatBedrock(
        model_id=settings.agent_model,
        region_name=settings.aws_region,
        model_kwargs={"temperature": config.temperature},
    )

    if callback_handler and hasattr(llm, "with_config"):
        llm = llm.with_config(callbacks=[callback_handler])

    # Initialize services
    grounding_service = GroundingService()
    indra_service = INDRAService()
    graph_builder = GraphBuilderService()

    # Define tools for INDRA operations
    @tool
    async def analyze_biological_pathways(
        query: str,
        source_entities: list[str],
        target_entities: list[str],
        max_depth: int = 4,
    ) -> str:
        """Analyze biological pathways and construct causal graphs.

        Use this tool to find causal relationships between biological entities
        using the INDRA knowledge base. This will query for paths from source
        entities (e.g., environmental exposures) to target entities (e.g., biomarkers).

        Args:
            query: The user's query text for context
            source_entities: Source entities (e.g., ["PM2.5", "Ozone"])
            target_entities: Target entities (e.g., ["CRP", "IL-6"])
            max_depth: Maximum path depth to explore (default: 4)

        Returns:
            JSON string with causal graph data including nodes, edges, and paths
        """
        try:
            logger.info(
                f"Analyzing pathways: {source_entities} -> {target_entities}"
            )

            # Query INDRA for paths
            all_paths = []
            for source in source_entities:
                for target in target_entities:
                    paths = await indra_service.find_causal_paths(
                        source=source,
                        target=target,
                        max_depth=max_depth,
                    )
                    all_paths.extend(paths)

            # Rank paths by evidence and confidence
            ranked_paths = indra_service.rank_paths(all_paths)
            logger.info(f"Found {len(ranked_paths)} causal paths")

            # Build causal graph from top paths
            causal_graph = graph_builder.build_causal_graph(
                paths=ranked_paths[:3],  # Use top 3 paths
                genetics={},  # TODO: Add genetics support
            )

            return json.dumps(
                {
                    "status": "success",
                    "causal_graph": causal_graph.model_dump(),
                    "num_paths": len(ranked_paths),
                    "paths": ranked_paths[:5],  # Top 5 for context
                    "query": query,
                }
            )

        except Exception as e:
            logger.error(f"Pathway analysis error: {e}", exc_info=True)
            return json.dumps(
                {
                    "status": "error",
                    "error": str(e),
                    "causal_graph": {
                        "nodes": [],
                        "edges": [],
                        "genetic_modifiers": [],
                    },
                }
            )

    @tool
    def ground_entities(entities: list[str]) -> str:
        """Ground biological entities to database identifiers.

        Use this tool to map entity names (like "CRP", "PM2.5", "IL-6") to
        standardized database identifiers (MESH, HGNC, GO, CHEBI). This is
        necessary before querying for causal paths.

        Args:
            entities: List of entity names to ground (e.g., ["CRP", "IL-6"])

        Returns:
            JSON string with grounded entities and their database identifiers
        """
        try:
            logger.info(f"Grounding {len(entities)} entities")
            grounded = grounding_service.ground_entities(entities)

            return json.dumps(
                {
                    "status": "success",
                    "grounded": grounded,
                    "num_entities": len(entities),
                }
            )

        except Exception as e:
            logger.error(f"Grounding error: {e}", exc_info=True)
            return json.dumps(
                {
                    "status": "error",
                    "error": str(e),
                    "grounded": {},
                }
            )

    # Combine base tools with handoff tools if provided
    base_tools = [analyze_biological_pathways, ground_entities]
    tools = base_tools + (handoff_tools or [])

    # System prompt from config
    system_prompt = config.system_prompt

    # Return ReAct agent
    return create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt,
        name=agent_name,
        state_schema=OverallState,
    )
