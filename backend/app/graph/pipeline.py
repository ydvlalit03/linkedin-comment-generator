"""
LangGraph Pipeline — the comment generation workflow

Graph:
  analyze → search → rag → generate (parallel) → humanize+validate → retry?
                                                                      ↓
                                                              quality < 50 → re-generate
                                                              quality >= 50 → done
"""
import logging
from langgraph.graph import StateGraph, END
from app.graph.state import PipelineState
from app.graph.nodes import (
    analyze_node,
    search_node,
    rag_node,
    generate_node,
    humanize_validate_node,
    should_retry,
)

log = logging.getLogger("pipeline")


def build_pipeline() -> StateGraph:
    """Build and compile the LangGraph pipeline"""

    graph = StateGraph(PipelineState)

    # Add nodes
    graph.add_node("analyze", analyze_node)
    graph.add_node("search", search_node)
    graph.add_node("rag", rag_node)
    graph.add_node("generate", generate_node)
    graph.add_node("humanize_validate", humanize_validate_node)

    # Linear flow: analyze → search → rag → generate → humanize_validate
    graph.set_entry_point("analyze")
    graph.add_edge("analyze", "search")
    graph.add_edge("search", "rag")
    graph.add_edge("rag", "generate")
    graph.add_edge("generate", "humanize_validate")

    # Conditional: retry or done
    graph.add_conditional_edges(
        "humanize_validate",
        should_retry,
        {
            "retry": "generate",   # go back and regenerate
            "done": END,
        },
    )

    return graph.compile()


# Singleton compiled graph
_pipeline = None


def get_pipeline():
    global _pipeline
    if _pipeline is None:
        log.info("Building LangGraph pipeline...")
        _pipeline = build_pipeline()
        log.info("Pipeline ready")
    return _pipeline
