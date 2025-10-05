#!/usr/bin/env python3
"""
Unit tests for MCP Orchestrator agent routing functionality.
"""

import unittest
from unittest.mock import patch, MagicMock
from typing import Any

# Add current directory to path for imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.orchestrator import AgentRouter, AgentType, route_goal


class TestAgentRouter(unittest.TestCase):
    """Test the AgentRouter class functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.router = AgentRouter()

    def test_route_goal_general_agent(self):
        """Test routing to general agent for typical coding tasks."""
        test_cases = [
            "Create a new Python function to handle file operations",
            "Write documentation for the API endpoints",
            "Refactor the code to improve performance",
            "Add error handling to the existing functions",
            "Design a new module structure for the project",
            "Implement a user interface component"
        ]

        for goal in test_cases:
            with self.subTest(goal=goal):
                result = self.router.route_goal(goal)
                self.assertEqual(result.agent, AgentType.GENERAL)
                self.assertGreater(result.confidence, 0.0)
                self.assertIsInstance(result.steps, list)
                self.assertGreater(len(result.steps), 0)

    def test_route_goal_tests_agent(self):
        """Test routing to tests agent for testing-related tasks."""
        test_cases = [
            "Write unit tests for the new calculator function",
            "Create integration tests for the API endpoints",
            "Add test coverage for the database operations",
            "Implement TDD approach for the new feature",
            "Write pytest fixtures for testing the models",
            "Verify the functionality with comprehensive tests"
        ]

        for goal in test_cases:
            with self.subTest(goal=goal):
                result = self.router.route_goal(goal)
                self.assertEqual(result.agent, AgentType.TESTS)
                self.assertGreater(result.confidence, 0.0)
                self.assertIn("test", result.reasoning.lower())

    def test_route_goal_db_agent(self):
        """Test routing to database agent for data-related tasks."""
        test_cases = [
            "Design a database schema for user management",
            "Create SQL queries for retrieving user data",
            "Implement database migrations for the new tables",
            "Add database constraints and indexes",
            "Design ORM models for the application",
            "Optimize database queries for better performance"
        ]

        for goal in test_cases:
            with self.subTest(goal=goal):
                result = self.router.route_goal(goal)
                self.assertEqual(result.agent, AgentType.DB)
                self.assertGreater(result.confidence, 0.0)
                self.assertIn("database", result.reasoning.lower())

    def test_route_goal_empty_input(self):
        """Test routing with empty or invalid input."""
        test_cases = ["", "   ", None]

        for goal in test_cases:
            with self.subTest(goal=goal):
                result = self.router.route_goal(goal)
                self.assertEqual(result.agent, AgentType.GENERAL)
                self.assertEqual(result.confidence, 0.0)
                self.assertIn("invalid", result.reasoning.lower())

    def test_route_goal_with_meta(self):
        """Test routing with metadata."""
        goal = "Create a test for the database function"
        meta = {"context": "testing", "priority": "high"}

        result = self.router.route_goal(goal, meta)

        # Should route to db agent due to "database" being the primary domain
        self.assertEqual(result.agent, AgentType.DB)
        self.assertGreater(result.confidence, 0.0)

    def test_calculate_agent_score(self):
        """Test the agent scoring mechanism."""
        capability = self.router.capabilities[AgentType.TESTS]

        # High match score
        score = self.router._calculate_agent_score("write unit tests for the function", capability)
        self.assertGreater(score, 0.5)

        # Low match score
        score = self.router._calculate_agent_score("design a new user interface", capability)
        self.assertLess(score, 0.3)

    def test_get_available_agents(self):
        """Test getting information about available agents."""
        agents = self.router.get_available_agents()

        self.assertIsInstance(agents, dict)
        self.assertIn("general", agents)
        self.assertIn("tests", agents)
        self.assertIn("db", agents)

        for agent_name, agent_info in agents.items():
            self.assertIn("name", agent_info)
            self.assertIn("description", agent_info)
            self.assertIn("can_use_rag", agent_info)
            self.assertIn("keywords", agent_info)

    def test_agent_capabilities_structure(self):
        """Test that agent capabilities are properly structured."""
        for agent_type, capability in self.router.capabilities.items():
            self.assertIsInstance(capability.name, str)
            self.assertIsInstance(capability.description, str)
            self.assertIsInstance(capability.keywords, list)
            self.assertIsInstance(capability.patterns, list)
            self.assertIsInstance(capability.can_use_rag, bool)

            # Should have some keywords and patterns
            self.assertGreater(len(capability.keywords), 0)
            self.assertGreater(len(capability.patterns), 0)


class TestOrchestratorIntegration(unittest.TestCase):
    """Test the orchestrator integration functions."""

    def test_route_goal_function(self):
        """Test the route_goal function interface."""
        result = route_goal("Create a new Python class for handling API requests")

        self.assertIsInstance(result, dict)
        self.assertIn("agent", result)
        self.assertIn("confidence", result)
        self.assertIn("reasoning", result)
        self.assertIn("steps", result)

        self.assertEqual(result["agent"], "general")
        self.assertIsInstance(result["steps"], list)

    def test_route_goal_function_with_meta(self):
        """Test route_goal function with metadata."""
        meta = {"project_type": "web", "framework": "flask"}
        result = route_goal("Implement user authentication", meta)

        self.assertIsInstance(result, dict)
        self.assertIn("agent", result)

    def test_consistent_routing(self):
        """Test that similar goals route to the same agent consistently."""
        goals = [
            "Write unit tests for the authentication module",
            "Add test coverage for the login endpoint",
            "Implement pytest fixtures for API testing"
        ]

        agents = []
        for goal in goals:
            result = route_goal(goal)
            agents.append(result["agent"])

        # All should route to tests agent
        self.assertTrue(all(agent == "tests" for agent in agents))

    def test_routing_boundary_cases(self):
        """Test routing for goals that could match multiple agents."""
        # Goal with both testing and database keywords
        result = route_goal("Write tests for database operations")
        # Should prioritize database due to "database" being the primary domain
        self.assertEqual(result["agent"], "db")

        # Goal with database and general keywords
        result = route_goal("Create database models for the application")
        # Should route to database due to "database" keyword
        self.assertEqual(result["agent"], "db")


class TestMCPServerOrchestratorIntegration(unittest.TestCase):
    """Test MCP server integration with orchestrator."""

    def setUp(self):
        """Set up test fixtures."""
        from mcp.server import MCPServer
        self.server = MCPServer()

    def test_orchestrator_route_tool_call(self):
        """Test calling orchestrator.route through MCP server."""
        import asyncio

        async def test():
            message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "orchestrator.route",
                    "arguments": {
                        "goal": "Implement a function to validate user input"
                    }
                }
            }

            response = await self.server.handle_message(message)

            self.assertEqual(response["jsonrpc"], "2.0")
            self.assertEqual(response["id"], 1)
            self.assertIn("result", response)

            result = response["result"]
            self.assertIn("agent", result)
            self.assertIn("confidence", result)
            self.assertIn("reasoning", result)
            self.assertIn("steps", result)

        asyncio.run(test())

    def test_orchestrator_route_tool_with_meta(self):
        """Test orchestrator.route tool with metadata."""
        import asyncio

        async def test():
            message = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "orchestrator.route",
                    "arguments": {
                        "goal": "Create database schema for user management",
                        "meta": {"context": "backend", "priority": "high"}
                    }
                }
            }

            response = await self.server.handle_message(message)

            self.assertEqual(response["jsonrpc"], "2.0")
            self.assertEqual(response["id"], 2)
            self.assertIn("result", response)

            result = response["result"]
            self.assertEqual(result["agent"], "db")  # Should route to DB agent

        asyncio.run(test())

    def test_orchestrator_tools_list_includes_route(self):
        """Test that orchestrator.route is included in tools/list."""
        import asyncio

        async def test():
            message = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/list"
            }

            response = await self.server.handle_message(message)

            self.assertEqual(response["jsonrpc"], "2.0")
            self.assertEqual(response["id"], 3)
            self.assertIn("result", response)

            tool_names = [tool["name"] for tool in response["result"]["tools"]]
            self.assertIn("orchestrator.route", tool_names)

        asyncio.run(test())


if __name__ == '__main__':
    unittest.main()
