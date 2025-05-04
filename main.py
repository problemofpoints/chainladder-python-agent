#!/usr/bin/env python
"""
Chainladder AI Agent - Main Entry Point

This script launches the Chainladder AI Agent system with a Gradio interface.
"""
import os
import argparse
from chainladder_agent.app import launch_app


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Chainladder AI Agent with Gradio UI")
    parser.add_argument(
        "--port", type=int, default=7860, 
        help="Port number to run the Gradio server on (default: 7860)"
    )
    parser.add_argument(
        "--share", action="store_true", 
        help="Enable Gradio sharing for public access"
    )
    parser.add_argument(
        "--debug", action="store_true", 
        help="Run in debug mode with additional logging"
    )
    return parser.parse_args()


def main():
    """Main entry point for the application."""
    args = parse_arguments()
    
    # Set up debugging if requested
    if args.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
        print("Running in debug mode")
    
    # Check for API key in environment
    if not os.environ.get("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY not found in environment variables.")
        print("You will need to input your API key in the web interface.")
    
    # Launch the Gradio app
    app = launch_app()
    app.launch(server_port=args.port, share=args.share)


if __name__ == "__main__":
    main()
