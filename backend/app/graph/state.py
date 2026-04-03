"""LangGraph State — shared across all nodes"""
from typing import TypedDict, Annotated
import operator


class PipelineState(TypedDict):
    # Input
    post_id: int
    post_text: str
    post_author: dict         # {name, headline}
    media: list[dict]

    # Analysis
    analysis: dict            # PostAnalysis
    web_context: str          # formatted search results
    rag_context: str          # formatted RAG examples
    rag_angles: list[str]     # extracted angle names from RAG

    # Commenter
    profile: dict             # CommenterProfile

    # Generation — uses Annotated + operator.add to APPEND (not replace)
    comments: Annotated[list[dict], operator.add]

    # Control
    retry_count: int
    errors: Annotated[list[str], operator.add]
