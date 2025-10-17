"""LLM Factory for provider-agnostic model instantiation.

This module provides a unified interface for creating LLM instances
using AWS Bedrock with proper ChatBedrockConverse support.
"""

import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class LLMFactory:
    """Factory for creating AWS Bedrock LLM instances."""

    @classmethod
    def create_llm(cls, model_config: Dict[str, Any], agent_name: str = None) -> Any:
        """
        Create an LLM instance using AWS Bedrock with ChatBedrockConverse.

        Args:
            model_config: Configuration dictionary with model parameters
            agent_name: Optional agent name for logging

        Returns:
            ChatBedrockConverse instance

        Raises:
            ValueError: If AWS credentials are not found
            ImportError: If langchain-aws is not installed
        """
        # Check for AWS credentials
        aws_access_key = os.environ.get('AWS_BEDROCK_ACCESS_KEY') or os.environ.get('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.environ.get('AWS_BEDROCK_SECRET_ACCESS_KEY') or os.environ.get('AWS_SECRET_ACCESS_KEY')

        if not aws_access_key or not aws_secret_key:
            error_msg = (
                "AWS Bedrock credentials not found in environment. Please set:\n"
                "  - AWS_ACCESS_KEY_ID (or AWS_BEDROCK_ACCESS_KEY)\n"
                "  - AWS_SECRET_ACCESS_KEY (or AWS_BEDROCK_SECRET_ACCESS_KEY)\n"
                "\nMake sure credentials are in healthos_bot/config/config.env"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Log provider selection if agent_name provided
        if agent_name:
            logger.debug(f"Creating LLM for agent '{agent_name}' using AWS Bedrock")

        try:
            from langchain_aws import ChatBedrockConverse
        except ImportError:
            raise ImportError(
                "langchain-aws package not installed. "
                "Please run: pip install langchain-aws"
            )

        # Get model parameters
        model_id = model_config.get('model_id')
        region_name = model_config.get('region_name', 'us-east-1')
        temperature = model_config.get('temperature', 1.0)

        # Create ChatBedrockConverse instance
        bedrock_params = {
            'model': model_id,
            'temperature': temperature,
            'region_name': region_name,
        }

        # Add AWS credentials if explicitly provided
        if aws_access_key and aws_secret_key:
            bedrock_params['aws_access_key_id'] = aws_access_key
            bedrock_params['aws_secret_access_key'] = aws_secret_key

        logger.debug(f"Creating ChatBedrockConverse with model: {model_id}, region: {region_name}")

        return ChatBedrockConverse(**bedrock_params)


# Convenience function for backward compatibility
def create_llm(agent_name: str, model_params: Dict[str, Any]) -> Any:
    """
    Create an LLM instance for a specific agent.

    This is a convenience function that maintains backward compatibility
    with the existing agent code.

    Args:
        agent_name: Name of the agent requesting the LLM
        model_params: Model configuration parameters

    Returns:
        LLM instance configured for the agent
    """
    return LLMFactory.create_llm(model_params, agent_name)
