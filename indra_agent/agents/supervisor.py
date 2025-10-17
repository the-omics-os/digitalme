"""Simplified supervisor that delegates via handoff tools instead of manual routing."""

import logging

from indra_agent.config.agent_config import SUPERVISOR_CONFIG

logger = logging.getLogger(__name__)


def create_supervisor_prompt() -> str:
    """Create the supervisor system prompt with delegation instructions.

    The supervisor uses handoff tools to delegate to specialist agents,
    rather than implementing routing logic directly.

    Returns:
        System prompt for the supervisor
    """
    prompt = SUPERVISOR_CONFIG.system_prompt + """

DELEGATION INSTRUCTIONS:

You have access to specialized agents via delegation tools:

1. **delegate_to_indra_query**: Use when the user asks about:
   - Biological mechanisms or molecular pathways
   - Causal relationships between entities
   - How one thing affects another biologically
   - Scientific evidence for health effects

2. **delegate_to_web_researcher**: Use when the user needs:
   - Current air quality or pollution data
   - Environmental comparisons between locations
   - Specific environmental metrics or measurements
   - Historical environmental exposure data

IMPORTANT GUIDELINES:

- Ask clarifying questions FIRST before delegating
- Only delegate when you have enough information
- You can delegate to multiple agents if needed
- When agents return results, synthesize them into a conversational response
- Always explain your reasoning to the user

EXAMPLE WORKFLOWS:

User: "I'm moving from SF to LA, what should I consider?"
You: "That's exciting! To give you relevant guidance, could you tell me:
- Are you concerned about air quality or other environmental factors?
- Do you have any respiratory sensitivities?
- Are you looking for general awareness or specific precautions?"

User: "I'm mainly concerned about air quality and how it might affect my health."
You: [Use delegate_to_web_researcher to get air quality data]
     [Use delegate_to_indra_query to understand biological mechanisms]
     [Synthesize results into personalized guidance]

Remember: You're a conversational health companion, not just a routing system.
Engage naturally and only use tools when they'll truly help the user."""

    return prompt
