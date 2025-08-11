
from langgraph.graph import StateGraph, START, END

from app.graph.nodes import (
    node_fetch_reservation, node_fetch_conversation,
    node_extract_join_base, node_flatten_guests,
    node_reason_sentiment, node_hybrid_recos,
    node_enrich_candidates, node_assemble,route_by_reason
    ,node_hybrid_recos_business,node_hybrid_recos_pleasure
)

def build_graph():
    g = StateGraph(dict)
    g.add_node("fetch_reservation", node_fetch_reservation)
    g.add_node("fetch_conversation", node_fetch_conversation)
    g.add_node("extract_join_base", node_extract_join_base)
    g.add_node("flatten_guests", node_flatten_guests)
    g.add_node("reason_sentiment", node_reason_sentiment)
    g.add_node("travel-reason", lambda s: s)

    g.add_node("hybrid_recos_business", node_hybrid_recos_business)
    g.add_node("hybrid_recos_pleasure", node_hybrid_recos_pleasure)

    g.add_node("hybrid_recos", node_hybrid_recos)
    g.add_node("enrich", node_enrich_candidates)
    g.add_node("assemble", node_assemble)

    g.add_edge(START, "fetch_reservation")
    g.add_edge("fetch_reservation", "fetch_conversation")
    g.add_edge("fetch_conversation", "extract_join_base")
    g.add_edge("extract_join_base", "flatten_guests")
    g.add_edge("flatten_guests", "reason_sentiment")
    g.add_edge("reason_sentiment", "travel-reason")

    g.add_conditional_edges(
        "travel-reason",
        route_by_reason,
        {
            "business": "hybrid_recos_business",
            "pleasure": "hybrid_recos_pleasure",
            "unknown": END,
        },
    )
    g.add_edge("hybrid_recos_pleasure", "hybrid_recos")

    g.add_edge("hybrid_recos_business", "hybrid_recos")

    g.add_edge("hybrid_recos", "enrich")
    g.add_edge("enrich", "assemble")
    g.add_edge("assemble", END)


    return g.compile()
