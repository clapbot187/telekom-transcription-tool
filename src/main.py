#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir.parent))

from src.config import Config
from src.gui import TranscriptionGUI


def main():
    parser = argparse.ArgumentParser(
        description="Telekom Transcription Tool - Record and transcribe audio"
    )
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        default=None,
        help="Path to configuration file (default: config.json)"
    )
    parser.add_argument(
        "--api-key",
        "-k",
        type=str,
        default=None,
        help="API key for LLM services (overrides config file)"
    )

    args = parser.parse_args()

    config = Config(config_path=args.config)

    if args.api_key:
        config.api_key = args.api_key

    if not config.is_valid:
        print("Error: API key not configured.")
        print("\nPlease either:")
        print("  1. Copy config.template.json to config.json and add your API key")
        print("  2. Set the TRANSCRIPTION_API_KEY environment variable")
        print("  3. Use the --api-key command line option")
        sys.exit(1)

    app = TranscriptionGUI(config)
    app.run()


if __name__ == "__main__":
    main()
