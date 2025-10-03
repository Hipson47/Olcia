#!/usr/bin/env python3
"""
AI-Powered MCP Orchestrator with LLM Reasoning
Intelligent agent routing using GPT-4o-mini with Chain-of-Thought reasoning.
"""

import asyncio
import importlib.util
import json
from dataclasses import dataclass
from enum import Enum
from typing import Any

OPENAI_AVAILABLE = importlib.util.find_spec("openai") is not None
if OPENAI_AVAILABLE:
    from openai import AsyncOpenAI
else:
    print("Warning: OpenAI not available. Falling back to rule-based routing.")


class AgentType(Enum):
    """Available agent types for routing."""
    GENERAL = "general"
    TESTS = "tests"
    DB = "db"


@dataclass
class AgentCapability:
    """Defines an agent's capabilities and routing criteria."""
    name: str
    description: str
    keywords: list[str]
    patterns: list[str]
    can_use_rag: bool = True


@dataclass
class RoutingResult:
    """Result of agent routing decision."""
    agent: AgentType
    confidence: float
    reasoning: str
    steps: list[str]


class RuleBasedRouter:
    """
    Fallback rule-based router for when AI is unavailable.
    """

    AGENT_CAPABILITIES = {
        AgentType.GENERAL: AgentCapability(
            name="General Purpose Agent",
            description="Handles general coding tasks, file operations, and project management",
            keywords=[
                "create", "implement", "write", "edit", "modify", "update", "add", "remove",
                "refactor", "optimize", "document", "comment", "format", "organize",
                "plan", "design", "structure", "architecture", "setup", "configure"
            ],
            patterns=[
                r"\b(create|implement|write|edit|modify|update)\b.*\b(file|function|class|module|component)\b",
                r"\b(add|remove|refactor|optimize)\b.*\b(code|logic|structure)\b",
                r"\b(plan|design|structure|architecture)\b.*\b(system|application|project)\b"
            ],
            can_use_rag=True
        ),

        AgentType.TESTS: AgentCapability(
            name="Testing Agent",
            description="Specializes in test creation, execution, and quality assurance",
            keywords=[
                "test", "testing", "unittest", "pytest", "assert", "mock", "fixture",
                "coverage", "tdd", "bdd", "integration", "unit", "functional",
                "verify", "validate", "check", "ensure", "assert", "spec", "specimen"
            ],
            patterns=[
                r"\b(test|testing|unittest|pytest)\b",
                r"\b(assert|mock|fixture|coverage)\b",
                r"\b(tdd|bdd|integration|unit|functional)\b.*\btest",
                r"\b(verify|validate|check|ensure)\b.*\b(code|function|behavior)"
            ],
            can_use_rag=True
        ),

        AgentType.DB: AgentCapability(
            name="Database Agent",
            description="Handles database operations, schema design, and data management",
            keywords=[
                "database", "db", "sql", "query", "table", "schema", "migration",
                "model", "orm", "data", "storage", "persist", "retrieve", "crud",
                "insert", "update", "delete", "select", "join", "index", "constraint"
            ],
            patterns=[
                r"\b(database|db|sql|query|table|schema)\b",
                r"\b(model|orm|migration|data|storage)\b",
                r"\b(insert|update|delete|select|join)\b",
                r"\b(persist|retrieve|crud)\b"
            ],
            can_use_rag=True
        )
    }

    def __init__(self) -> None:
        """Initialize rule-based router."""
        self.capabilities = self.AGENT_CAPABILITIES

    def route_goal(self, goal: str, meta: dict[str, Any] | None = None) -> RoutingResult:
        """Rule-based routing as fallback."""
        # Simplified rule-based routing
        goal_lower = goal.lower()

        if any(word in goal_lower for word in ["test", "testing", "pytest", "unittest", "assert", "mock"]):
            agent = AgentType.TESTS
            confidence = 0.8
        elif any(word in goal_lower for word in ["database", "db", "sql", "query", "table", "schema", "migration"]):
            agent = AgentType.DB
            confidence = 0.8
        else:
            agent = AgentType.GENERAL
            confidence = 0.6

        return RoutingResult(
            agent=agent,
            confidence=confidence,
            reasoning=f"Rule-based routing assigned to {agent.value} agent",
            steps=["Analyze task requirements", "Implement solution", "Test functionality"]
        )


class AIAgentRouter:
    """
    AI-powered agent router using GPT-4o-mini with Chain-of-Thought reasoning.

    This system analyzes goals using LLM to provide intelligent routing decisions,
    dynamic specialization, and context-aware reasoning with RAG integration.
    """

    SYSTEM_PROMPT = """
    You are an expert software engineering agent orchestrator with access to a comprehensive knowledge base. Your task is to analyze development goals and route them to the most appropriate specialized agent, leveraging relevant knowledge when available.

    Available agents:
    1. GENERAL: General-purpose coding tasks, file operations, refactoring, architecture design, API development
    2. TESTS: Testing, quality assurance, TDD, test coverage, mocking, assertions, integration testing
    3. DB: Database operations, schema design, migrations, ORM, data modeling, CRUD operations, query optimization

    For each goal, provide:
    1. Most appropriate agent (GENERAL, TESTS, or DB)
    2. Confidence score (0.0-1.0) based on how well the goal matches agent capabilities and available knowledge
    3. Chain-of-Thought reasoning explaining your decision, incorporating relevant knowledge from the provided context
    4. Specific implementation steps tailored to the goal, informed by best practices from the knowledge base

    Use Chain-of-Thought reasoning:
    - Analyze the goal's technical domain and requirements
    - Consider required expertise, tools, and methodologies
    - Review relevant knowledge from the provided RAG context
    - Evaluate complexity, dependencies, and architectural implications
    - Determine best agent specialization based on expertise alignment
    - Generate actionable, context-aware implementation steps following industry best practices

    When RAG knowledge is provided:
    - Incorporate relevant patterns, frameworks, and approaches from the knowledge base
    - Reference specific technologies, architectures, or methodologies mentioned
    - Adapt implementation steps based on proven best practices
    - Use the knowledge to improve confidence scoring and step specificity

    Return response as JSON with keys: agent, confidence, reasoning, steps
    """

    def __init__(self) -> None:
        """Initialize AI agent router."""
        self.client: AsyncOpenAI | None = None
        if OPENAI_AVAILABLE:
            self.client = AsyncOpenAI()  # Will use OPENAI_API_KEY from env
        self.fallback_router = RuleBasedRouter()

    async def route_goal(self, goal: str, meta: dict[str, Any] | None = None) -> RoutingResult:
        """
        Route a goal using AI analysis with Chain-of-Thought reasoning.

        Args:
            goal: The goal description to route
            meta: Optional metadata about the context

        Returns:
            RoutingResult with AI-powered agent assignment and reasoning
        """
        if not goal or not goal.strip():
            return RoutingResult(
                agent=AgentType.GENERAL,
                confidence=0.0,
                reasoning="Empty or invalid goal provided",
                steps=["Clarify the goal and try again"]
            )

        # Try AI-powered routing first
        if self.client:
            try:
                return await self._ai_route_goal(goal, meta or {})
            except Exception as e:
                print(f"AI routing failed: {e}. Falling back to rule-based routing.")
                # Fall through to fallback routing

        # Fallback to rule-based routing
        return self.fallback_router.route_goal(goal, meta)

    async def _ai_route_goal(self, goal: str, meta: dict[str, Any]) -> RoutingResult:
        """Perform AI-powered goal routing using GPT-4o-mini with RAG context."""
        context = f"Goal: {goal}"
        if meta:
            context += f"\nContext: {json.dumps(meta, indent=2)}"

        # Get relevant context from RAG knowledge base
        rag_context = await self.get_rag_context(goal)
        if rag_context:
            context += f"\n\nRelevant Knowledge from RAG:\n{rag_context}"

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"Please analyze this development goal and route it to the most appropriate agent. Use the provided knowledge context when available:\n\n{context}"}
        ]

        assert self.client is not None, "OpenAI client not initialized"
        response = await self.client.chat.completions.create(  # type: ignore[call-overload]
            messages=messages,
            model="gpt-4o-mini",
            temperature=0.3,  # Balanced creativity and consistency
            max_tokens=1000,
            response_format={"type": "json_object"}
        )

        result_data = json.loads(response.choices[0].message.content)

        # Map string agent names to enum values
        agent_mapping = {
            "GENERAL": AgentType.GENERAL,
            "TESTS": AgentType.TESTS,
            "DB": AgentType.DB
        }

        agent_str = result_data.get("agent", "GENERAL").upper()
        agent = agent_mapping.get(agent_str, AgentType.GENERAL)

        return RoutingResult(
            agent=agent,
            confidence=min(float(result_data.get("confidence", 0.5)), 1.0),
            reasoning=result_data.get("reasoning", "AI-powered routing decision"),
            steps=result_data.get("steps", ["Analyze requirements", "Implement solution", "Test functionality"])
        )

    async def get_rag_context(self, goal: str) -> str:
        """
        Get relevant context from RAG knowledge base for better routing decisions.
        """
        try:
            # Import RAG server dynamically to avoid circular imports

            from mcp.server import RAGServer

            # Create a temporary RAG server instance for searching
            # Note: In production, this should be a singleton or injected dependency
            rag_server = RAGServer()

            # Search for relevant context in the knowledge base
            results = rag_server.search_knowledge(goal, n_results=3)

            if results:
                context_parts = []
                for result in results:
                    if result["relevance_score"] > 0.7:  # Only include highly relevant results
                        context_parts.append(f"• {result['content'][:500]}... (relevance: {result['relevance_score']:.2f})")

                if context_parts:
                    return "\n".join(context_parts)

        except Exception as e:
            # Silently fail and return empty context if RAG is unavailable
            print(f"RAG context retrieval failed: {e}")

        return ""

    def get_available_agents(self) -> dict[str, dict[str, Any]]:
        """
        Get information about all available agents with AI capabilities.
        """
        return {
            "general": {
                "name": "AI General Agent",
                "description": "Intelligent general-purpose coding with LLM reasoning",
                "capabilities": ["Architecture", "Refactoring", "Implementation", "Documentation"],
                "ai_powered": True
            },
            "tests": {
                "name": "AI Testing Agent",
                "description": "Advanced testing strategies with AI-driven test generation",
                "capabilities": ["TDD", "Coverage Analysis", "Mocking", "Integration Testing"],
                "ai_powered": True
            },
            "db": {
                "name": "AI Database Agent",
                "description": "Intelligent database design and optimization with LLM analysis",
                "capabilities": ["Schema Design", "Migrations", "Query Optimization", "Data Modeling"],
                "ai_powered": True
            }
        }


# Global AI router instance
router = AIAgentRouter()


async def route_goal_async(goal: str, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Route a goal to an appropriate agent using AI-powered analysis.

    This is the async entry point for the orchestrator.route tool.

    Args:
        goal: The goal description
        meta: Optional metadata

    Returns:
        Dictionary with agent, confidence, reasoning, and steps
    """
    result = await router.route_goal(goal, meta)

    return {
        "agent": result.agent.value,
        "confidence": result.confidence,
        "reasoning": result.reasoning,
        "steps": result.steps
    }


def route_goal(goal: str, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Synchronous wrapper for route_goal_async.

    This maintains backward compatibility with existing MCP server calls.
    """

    try:
        # Try to get current event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # We're in an async context, create a new thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, route_goal_async(goal, meta))
                return future.result()
        else:
            # We can run the coroutine directly
            return loop.run_until_complete(route_goal_async(goal, meta))
    except RuntimeError:
        # No event loop, create one
        return asyncio.run(route_goal_async(goal, meta))
