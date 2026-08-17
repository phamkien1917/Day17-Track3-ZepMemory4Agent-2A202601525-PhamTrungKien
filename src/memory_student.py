from __future__ import annotations

from typing import Any

from .config import settings
from .context_budget import ContextBudgetManager
from .utils import cap_query
from .zep_common import prime_eval_thread, render_graph_search


class StudentMemory:
    """Only this file needs to be edited by students."""

    def __init__(self, client: Any):
        self.client = client
        self.budget = ContextBudgetManager(settings.context_tokens)

    # NOTE: Zep rejects graph.search queries longer than 400 characters. Some
    # eval queries are longer than that, so wrap every query with
    # `cap_query(query)` (see src/utils.py) before passing it to graph.search.

    def retrieve_long_term(self, user_id: str, thread_id: str, query: str) -> str:
        prime_eval_thread(self.client, user_id, thread_id, query)
        context = self.client.thread.get_user_context(thread_id=thread_id)
        
        edges = self.client.graph.search(
            user_id=user_id,
            query=cap_query(query),
            scope="edges",
            limit=30,
        )
        return str(context.context) + "\n" + render_graph_search(edges)

    def retrieve_episodic(self, user_id: str, query: str) -> str:
        results = self.client.graph.search(
            user_id=user_id,
            query=cap_query(query[-400:]),
            scope="episodes",
            limit=50,
        )
        
        class _WrappedResults:
            def __init__(self, orig):
                self.context = getattr(orig, "context", None)
                self.edges = getattr(orig, "edges", None)
                self.episodes = [ep for ep in (getattr(orig, "episodes", None) or []) if len(getattr(ep, "content", "")) < 300]
                self.nodes = getattr(orig, "nodes", None)
                self.observations = getattr(orig, "observations", None)
                self.thread_summaries = getattr(orig, "thread_summaries", None)

        return render_graph_search(_WrappedResults(results), episode_char_cap=170)

    def retrieve_semantic(self, graph_id: str, query: str) -> str:
        # LAB TODO 3/4
        # Search the standalone graph (graph_id, NOT user_id).
        # Recommended: scope="episodes" — it returns raw document text that keeps
        # literal markers (e.g. PAYMENT-RULE-3). The "auto" scope returns
        # extracted facts that DROP those literal codes, so avoid it here.
        # Fallback: scope="nodes".
        results = self.client.graph.search(
            graph_id=graph_id,
            query=cap_query(query),
            scope="episodes",
            limit=8,
        )
        return render_graph_search(results)

    def assemble_context(self, layers: dict[str, str]) -> tuple[str, dict[str, dict[str, int]]]:
        # LAB TODO 4/4
        # Use ContextBudgetManager to enforce 10/4/3/3 budget and priority order.
        return self.budget.assemble(layers)
