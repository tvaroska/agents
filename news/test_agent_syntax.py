"""Test script to check correct ADK built-in tool syntax."""

import google.adk

print(f"ADK Version: {getattr(google.adk, '__version__', 'unknown')}")

# Check what's available in google.adk
print("\nAvailable in google.adk:")
items = [item for item in dir(google.adk) if not item.startswith('_')]
for item in items:
    print(f"  - {item}")

# Try to find google_search or related
search_related = [item for item in items if 'search' in item.lower() or 'tool' in item.lower()]
print(f"\nSearch/Tool related items: {search_related}")

# Check Agent class
from google.adk import Agent
import inspect

print("\nAgent class info:")
print(f"  Module: {Agent.__module__}")
print(f"  MRO: {[c.__name__ for c in Agent.__mro__]}")

# Try creating an agent without tools
print("\nTrying to create agent without built-in tool...")
try:
    test_agent = Agent(
        name="test",
        model="gemini-2.0-flash",
        description="Test agent",
        instruction="Test instruction"
    )
    print(f"  ✅ Agent created: {test_agent.name}")
except Exception as e:
    print(f"  ❌ Error: {e}")
