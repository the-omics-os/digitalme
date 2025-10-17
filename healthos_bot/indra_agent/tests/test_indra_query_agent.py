"""Simple test for INDRA query agent functionality."""

import asyncio
import pytest
from indra_agent.services.indra_service import INDRAService


@pytest.mark.asyncio
async def test_indra_query_agent_basic():
    """Test basic INDRA query functionality with path finding."""

    # Initialize service
    indra_service = INDRAService()

    try:
        # Test query: PM2.5 -> CRP (common health query)
        source = "PM2.5"
        target = "CRP"

        print(f"\nQuerying INDRA: {source} -> {target}")

        # Find causal paths
        paths = await indra_service.find_causal_paths(
            source=source,
            target=target,
            max_depth=4
        )

        # Verify we got results
        assert paths is not None, "Should return paths list"
        assert isinstance(paths, list), "Paths should be a list"

        if len(paths) > 0:
            # Verify path structure matches expected format
            first_path = paths[0]
            assert "nodes" in first_path, "Path should have nodes"
            assert "edges" in first_path, "Path should have edges"
            assert isinstance(first_path["nodes"], list), "Nodes should be a list"
            assert isinstance(first_path["edges"], list), "Edges should be a list"

            # Verify edge structure
            if len(first_path["edges"]) > 0:
                edge = first_path["edges"][0]
                assert "source" in edge, "Edge should have source"
                assert "target" in edge, "Edge should have target"
                assert "relationship" in edge, "Edge should have relationship"
                assert "evidence_count" in edge, "Edge should have evidence_count"
                assert "belief" in edge, "Edge should have belief score"

                # Verify relationship type is valid
                valid_relationships = ["activates", "inhibits", "increases", "decreases"]
                assert edge["relationship"] in valid_relationships, \
                    f"Relationship should be one of {valid_relationships}"

            print(f"✓ Found {len(paths)} paths")
            print(f"✓ First path has {len(first_path['nodes'])} nodes and {len(first_path['edges'])} edges")
            print(f"✓ Path structure is valid")
        else:
            print("⚠ No paths found (may use cached responses in production)")

    finally:
        # Cleanup
        await indra_service.close()


if __name__ == "__main__":
    # Run test directly
    asyncio.run(test_indra_query_agent_basic())
