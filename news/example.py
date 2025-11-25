"""Example script demonstrating how to use the stock research agent programmatically."""

import asyncio
from google.adk import InMemorySessionService
from research.agent import stock_research_agent


async def research_stock(ticker: str):
    """Research a stock and generate a report.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')
    """
    print(f"\n{'='*60}")
    print(f"Stock News Research Agent - {ticker.upper()}")
    print(f"{'='*60}\n")

    # Create a session service
    session_service = InMemorySessionService()

    # Create a new session
    session = session_service.create_session(
        app_name="stock_research",
        user_id="example_user"
    )

    # Create the user message
    user_message = f"Research recent news for {ticker} stock and create a comprehensive report"

    print(f"User: {user_message}\n")
    print("Agent is researching... (this may take 30-60 seconds)\n")

    try:
        # Run the agent
        response = await stock_research_agent.run_async(
            session=session,
            user_content=user_message
        )

        # Display the response
        print(f"{'='*60}")
        print("Research Report Generated:")
        print(f"{'='*60}\n")
        print(response)
        print(f"\n{'='*60}")

        # Check for artifacts
        if hasattr(session, 'artifacts') and session.artifacts:
            print(f"\nArtifacts saved: {len(session.artifacts)}")
            for artifact in session.artifacts:
                print(f"  - {artifact.get('name', 'unnamed')}")
        else:
            print("\nNote: Artifact storage may require additional configuration")

    except Exception as e:
        print(f"Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure your .env file is configured with GOOGLE_API_KEY")
        print("2. Verify you have internet connection")
        print("3. Check that google-adk is installed: pip install google-adk")


async def main():
    """Main function demonstrating different ticker examples."""

    # Example 1: Research Apple stock
    await research_stock("AAPL")

    # Uncomment to research other stocks:
    # await research_stock("GOOGL")
    # await research_stock("TSLA")
    # await research_stock("NVDA")
    # await research_stock("MSFT")


if __name__ == "__main__":
    print("Stock News Research Agent - Example Usage")
    print("=" * 60)

    # Run the async main function
    asyncio.run(main())
