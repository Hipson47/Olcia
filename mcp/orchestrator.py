#!/usr/bin/env python3
"""
MCP Orchestrator with Agent Routing
Routes tasks to specialized agents based on goal analysis.
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any


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


class AgentRouter:
    """
    Routes goals to appropriate agents based on content analysis.

    Extension seams:
    - Add new AgentCapability instances to AGENT_CAPABILITIES
    - Modify routing logic in _analyze_goal()
    - Extend AgentType enum for new agents
    """

    # Agent capabilities and routing criteria
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
        """Initialize the agent router."""
        self.capabilities = self.AGENT_CAPABILITIES

    def route_goal(self, goal: str, meta: dict[str, Any] | None = None) -> RoutingResult:
        """
        Route a goal to the most appropriate agent.

        Args:
            goal: The goal description to route
            meta: Optional metadata about the context

        Returns:
            RoutingResult with agent assignment and reasoning
        """
        if not goal or not goal.strip():
            return RoutingResult(
                agent=AgentType.GENERAL,
                confidence=0.0,
                reasoning="Empty or invalid goal provided",
                steps=["Clarify the goal and try again"]
            )

        # Analyze the goal and determine best agent
        return self._analyze_goal(goal.lower(), meta or {})

    def _analyze_goal(self, goal: str, meta: dict[str, Any]) -> RoutingResult:
        """
        Analyze goal content and route to appropriate agent.

        Extension seam: Modify this method to add new routing logic.
        """
        # Score each agent based on keyword matches and patterns
        scores = {}

        for agent_type, capability in self.capabilities.items():
            score = self._calculate_agent_score(goal, capability)
            scores[agent_type] = score

        # Find the highest scoring agent
        # If there are ties, prefer specialized agents over general
        max_score = max(scores.values())
        candidates = [agent for agent, score in scores.items() if score == max_score]

        if len(candidates) == 1:
            best_agent = candidates[0]
        else:
            # Prefer specialized agents in tie situations
            # Priority: tests > db > general
            priority_order = [AgentType.TESTS, AgentType.DB, AgentType.GENERAL]
            for agent in priority_order:
                if agent in candidates:
                    best_agent = agent
                    break
            else:
                best_agent = candidates[0]  # Fallback

        confidence = scores[best_agent]

        # Generate reasoning and steps
        reasoning, steps = self._generate_reasoning_and_steps(best_agent, goal, confidence, meta)

        return RoutingResult(
            agent=best_agent,
            confidence=confidence,
            reasoning=reasoning,
            steps=steps
        )

    def _calculate_agent_score(self, goal: str, capability: AgentCapability) -> float:
        """
        Calculate how well a goal matches an agent's capabilities.

        Extension seam: Modify scoring algorithm here.
        """
        score = 0.0

        # Keyword matching (0-0.7 points)
        # More sensitive: each match adds points, but we normalize differently
        keyword_matches = sum(1 for keyword in capability.keywords if keyword in goal.lower())
        if keyword_matches > 0:
            # Base score from matches, with bonus for multiple matches
            base_score = min(keyword_matches * 0.2, 0.5)  # Up to 0.5 for keyword matches
            # Density bonus: more matches relative to goal length
            density_bonus = min(keyword_matches / max(len(goal.split()) / 10, 1), 0.2)
            score += base_score + density_bonus

        # Pattern matching (0-0.3 points)
        pattern_matches = sum(1 for pattern in capability.patterns
                            if re.search(pattern, goal, re.IGNORECASE))
        if pattern_matches > 0:
            score += min(pattern_matches * 0.15, 0.3)  # Up to 0.3 for pattern matches

        return min(score, 1.0)  # Cap at 1.0

    def _generate_reasoning_and_steps(self, agent: AgentType, goal: str,
                                    confidence: float, meta: dict[str, Any]) -> tuple[str, list[str]]:
        """
        Generate reasoning and recommended steps for the chosen agent.

        Extension seam: Customize reasoning and steps per agent here.
        """
        capability = self.capabilities[agent]

        # Base reasoning
        confidence_text = "high" if confidence > 0.7 else "medium" if confidence > 0.4 else "low"
        reasoning = f"Goal matches {capability.name} capabilities with {confidence_text} confidence"

        # Agent-specific steps
        if agent == AgentType.TESTS:
            steps = [
                "Analyze existing test coverage and structure",
                "Identify test cases needed for the goal",
                "Implement unit tests with proper mocking",
                "Run tests and verify coverage",
                "Document test scenarios and edge cases"
            ]
        elif agent == AgentType.DB:
            steps = [
                "Analyze data requirements and schema needs",
                "Design or modify database schema/models",
                "Implement data access layer and queries",
                "Test data operations and constraints",
                "Document data model and migration steps"
            ]
        else:  # GENERAL
            steps = [
                "Analyze requirements and break down the task",
                "Plan implementation approach and structure",
                "Implement the solution following best practices",
                "Test functionality and edge cases",
                "Document changes and update relevant files"
            ]

        # Add RAG usage if applicable
        if capability.can_use_rag and confidence > 0.3:
            steps.insert(0, "Search knowledge base for relevant examples and patterns")

        return reasoning, steps

    def get_available_agents(self) -> dict[str, dict[str, Any]]:
        """
        Get information about all available agents.

        Returns:
            Dictionary mapping agent names to their capabilities
        """
        return {
            agent_type.value: {
                "name": capability.name,
                "description": capability.description,
                "can_use_rag": capability.can_use_rag,
                "keywords": capability.keywords[:5],  # Show first 5 keywords
                "keyword_count": len(capability.keywords)
            }
            for agent_type, capability in self.capabilities.items()
        }


# Global router instance
router = AgentRouter()


def route_goal(goal: str, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Route a goal to an appropriate agent.

    This is the main entry point for the orchestrator.route tool.

    Args:
        goal: The goal description
        meta: Optional metadata

    Returns:
        Dictionary with agent, confidence, reasoning, and steps
    """
    result = router.route_goal(goal, meta)

    return {
        "agent": result.agent.value,
        "confidence": result.confidence,
        "reasoning": result.reasoning,
        "steps": result.steps
    }
