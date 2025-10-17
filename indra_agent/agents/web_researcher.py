"""Web Researcher Agent for environmental data collection and analysis.

This agent is responsible for fetching current air quality data, analyzing
environmental exposures, and calculating pollution deltas between locations.
"""

import json
import logging
from typing import List

from langchain_aws import ChatBedrock
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

from indra_agent.agents.state import OverallState
from indra_agent.config.agent_config import WEB_RESEARCHER_CONFIG
from indra_agent.config.settings import get_settings
from indra_agent.services.web_data_service import WebDataService

logger = logging.getLogger(__name__)


def web_research_agent(
    callback_handler=None,
    agent_name: str = "web_researcher",
    handoff_tools: List = None,
):
    """
    Create web research specialist agent for environmental data analysis.

    This expert agent specializes in:
    - Fetching current air quality data (PM2.5, ozone, NO2)
    - Analyzing historical environmental exposures
    - Calculating environmental deltas (e.g., SF vs LA air quality)
    - Providing context for environmental health impacts

    Args:
        callback_handler: Optional callback handler for LLM interactions
        agent_name: Name identifier for the agent instance
        handoff_tools: Additional tools for inter-agent communication

    Returns:
        Configured ReAct agent with environmental analysis capabilities
    """

    settings = get_settings()
    config = WEB_RESEARCHER_CONFIG

    # Initialize LLM
    llm = ChatBedrock(
        model_id=settings.agent_model,
        region_name=settings.aws_region,
        model_kwargs={"temperature": config.temperature},
    )

    if callback_handler and hasattr(llm, "with_config"):
        llm = llm.with_config(callbacks=[callback_handler])

    # Initialize services
    web_service = WebDataService()

    # Define tools for environmental operations
    @tool
    def analyze_environmental_data(location_history: list[dict]) -> str:
        """Analyze environmental and pollution data for location history.

        Use this tool to analyze a user's environmental exposure timeline based
        on their location history. This will fetch PM2.5 levels and calculate
        exposure changes between locations.

        Args:
            location_history: List of location dicts with structure:
                [
                    {
                        "city": "San Francisco",
                        "start_date": "2020-01-01",
                        "end_date": "2023-06-01",
                        "avg_pm25": 7.8  # optional, will use typical if not provided
                    },
                    {
                        "city": "Los Angeles",
                        "start_date": "2023-06-01",
                        "end_date": "present"
                    }
                ]

        Returns:
            JSON string with environmental exposure data including timeline,
            current exposure, and delta analysis
        """
        try:
            if not location_history:
                return json.dumps(
                    {
                        "status": "error",
                        "error": "No location history provided",
                        "environmental_data": {},
                    }
                )

            logger.info(
                f"Analyzing environmental data for {len(location_history)} locations"
            )

            # Use service to analyze location history
            environmental_data = web_service.analyze_location_history(
                location_history
            )

            logger.info(
                f"Environmental data collected for {len(environmental_data.get('exposures', []))} locations"
            )

            return json.dumps(
                {
                    "status": "success",
                    "environmental_data": environmental_data,
                    "num_locations": len(location_history),
                }
            )

        except Exception as e:
            logger.error(f"Environmental analysis error: {e}", exc_info=True)
            return json.dumps(
                {
                    "status": "error",
                    "error": str(e),
                    "environmental_data": {},
                }
            )

    @tool
    async def get_current_pollution(city: str) -> str:
        """Get current pollution data for a city.

        Use this tool to fetch real-time or typical air quality data for a
        specific city. This will attempt to use live APIs (IQAir) if configured,
        or fall back to typical annual average values.

        Args:
            city: City name (e.g., "San Francisco", "Los Angeles", "New York")

        Returns:
            JSON string with pollution metrics including PM2.5, source, and timestamp
        """
        try:
            logger.info(f"Fetching pollution data for {city}")

            # Use service to get pollution data
            pollution_data = await web_service.get_pollution_data(city)

            return json.dumps(
                {
                    "status": "success",
                    "pollution_data": pollution_data,
                    "city": city,
                }
            )

        except Exception as e:
            logger.error(f"Pollution data fetch error: {e}", exc_info=True)
            return json.dumps(
                {
                    "status": "error",
                    "error": str(e),
                    "pollution_data": {},
                }
            )

    @tool
    def calculate_exposure_delta(old_location: str, new_location: str) -> str:
        """Calculate change in pollution exposure between two locations.

        Use this tool to compare air quality between two cities and quantify
        the exposure change (both absolute and fold-change).

        Args:
            old_location: Previous location (e.g., "San Francisco")
            new_location: Current location (e.g., "Los Angeles")

        Returns:
            JSON string with delta analysis including fold-change and description
        """
        try:
            logger.info(
                f"Calculating exposure delta: {old_location} -> {new_location}"
            )

            # Use service to calculate delta
            delta_data = web_service.calculate_exposure_delta(
                old_location, new_location
            )

            return json.dumps(
                {
                    "status": "success",
                    "delta_data": delta_data,
                }
            )

        except Exception as e:
            logger.error(f"Delta calculation error: {e}", exc_info=True)
            return json.dumps(
                {
                    "status": "error",
                    "error": str(e),
                    "delta_data": {},
                }
            )

    # Combine base tools with handoff tools if provided
    base_tools = [
        analyze_environmental_data,
        get_current_pollution,
        calculate_exposure_delta,
    ]
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
