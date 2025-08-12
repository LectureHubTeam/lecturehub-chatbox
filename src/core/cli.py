"""
Command Line Interface for testing the chatbot logic.

This module provides a simple CLI for testing the chatbot functionality
without requiring Streamlit.
"""

import argparse
import os
import sys

from src.core.chatbot_logic import create_chatbot

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


def setup_parser() -> argparse.ArgumentParser:
    """Setup command line argument parser."""
    parser = argparse.ArgumentParser(
        description="LectureHub Chatbot CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test system initialization
  python cli.py init --host localhost --port 5432 --database embedding --user root --password root_password

  # Test question processing
  python cli.py ask "What is this lecture about?" --host localhost --port 5432 --database embedding --user root --password root_password

  # Check system status
  python cli.py status --host localhost --port 5432 --database embedding --user root --password root_password
        """,
    )

    # Common database arguments
    parser.add_argument("--host", default="localhost", help="Database host")
    parser.add_argument("--port", default="5432", help="Database port")
    parser.add_argument("--database", default="embedding", help="Database name")
    parser.add_argument("--user", default="root", help="Database user")
    parser.add_argument("--password", default="root_password", help="Database password")
    parser.add_argument("--connection-string", help="Full database connection string")

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize the system")
    init_parser.add_argument("--force-rebuild", action="store_true", help="Force rebuild vector store")

    # Ask command
    ask_parser = subparsers.add_parser("ask", help="Ask a question")
    ask_parser.add_argument("question", help="Question to ask")

    # Status command
    subparsers.add_parser("status", help="Check system status")

    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("--interactive", action="store_true", help="Interactive mode")

    return parser


def run_init_command(args: argparse.Namespace) -> bool:
    """Run the init command."""
    print("Initializing system...")

    chatbot = create_chatbot()

    # Setup database
    if args.connection_string:
        success = chatbot.setup_database(connection_string=args.connection_string)
    else:
        success = chatbot.setup_database(
            host=args.host, port=args.port, database=args.database, user=args.user, password=args.password
        )

    if not success:
        print("❌ Database setup failed")
        return False

    print("✓ Database setup completed")

    # Load and process documents
    documents = chatbot.load_and_process_documents()
    if documents is None:
        print("❌ Document loading failed")
        return False

    print(f"✓ Loaded {len(documents)} document chunks")

    # Setup vector store
    conn_str = args.connection_string
    if not conn_str:
        conn_str = f"postgresql+psycopg://{args.user}:{args.password}@{args.host}:{args.port}/{args.database}"

    success = chatbot.setup_vectorstore(conn_str, documents, args.force_rebuild)
    if not success:
        print("❌ Vector store setup failed")
        return False

    print("✓ Vector store setup completed")

    # Setup QA chain
    success = chatbot.setup_qa_chain()
    if not success:
        print("❌ QA chain setup failed")
        return False

    print("✓ QA chain setup completed")
    print("🎉 System initialization completed successfully!")

    return True


def run_ask_command(args: argparse.Namespace) -> bool:
    """Run the ask command."""
    print(f"Processing question: {args.question}")

    chatbot = create_chatbot()

    # Initialize system
    if args.connection_string:
        success = chatbot.initialize_system(connection_string=args.connection_string)
    else:
        success = chatbot.initialize_system(
            host=args.host, port=args.port, database=args.database, user=args.user, password=args.password
        )

    if not success:
        print("❌ System initialization failed")
        return False

    # Process question
    answer, sources, is_relevant = chatbot.process_question(args.question)

    print(f"\nQuestion: {args.question}")
    print(f"Relevant: {is_relevant}")
    print(f"Answer: {answer}")

    if sources:
        print(f"\nSources ({len(sources)}):")
        for i, source in enumerate(sources, 1):
            print(f"  {i}. {source.metadata.get('file_type', 'unknown')} - {source.page_content[:100]}...")

    return True


def run_status_command(args: argparse.Namespace) -> bool:
    """Run the status command."""
    print("Checking system status...")

    chatbot = create_chatbot()

    # Try to initialize if database is available
    if args.connection_string:
        chatbot.initialize_system(connection_string=args.connection_string)
    else:
        chatbot.initialize_system(
            host=args.host, port=args.port, database=args.database, user=args.user, password=args.password
        )

    status = chatbot.get_system_status()

    print("\nSystem Status:")
    print(f"  Database Initialized: {status.get('database_initialized', False)}")
    print(f"  Database Connection: {status.get('database_connection', False)}")
    print(f"  Vector Store Initialized: {status.get('vectorstore_initialized', False)}")
    print(f"  QA Chain Initialized: {status.get('qa_chain_initialized', False)}")
    print(f"  Relevance Checker Initialized: {status.get('relevance_checker_initialized', False)}")

    return True


def run_test_command(args: argparse.Namespace) -> bool:
    """Run the test command."""
    if args.interactive:
        print("Interactive test mode")
        print("Type 'quit' to exit")

        chatbot = create_chatbot()

        while True:
            try:
                question = input("\nEnter a question: ").strip()
                if question.lower() in ["quit", "exit", "q"]:
                    break

                if not question:
                    continue

                # Try to process the question
                answer, sources, is_relevant = chatbot.process_question(question)

                print(f"Answer: {answer}")
                print(f"Relevant: {is_relevant}")

            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
    else:
        print("Running automated tests...")
        # Import and run the test module
        try:
            from tests.test_chatbot_logic import run_all_tests

            return run_all_tests()
        except ImportError:
            print("❌ Test module not found")
            return False

    return True


def main():
    """Main CLI entry point."""
    parser = setup_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == "init":
            success = run_init_command(args)
        elif args.command == "ask":
            success = run_ask_command(args)
        elif args.command == "status":
            success = run_status_command(args)
        elif args.command == "test":
            success = run_test_command(args)
        else:
            print(f"Unknown command: {args.command}")
            return 1

        return 0 if success else 1

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
