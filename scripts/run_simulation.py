#!/usr/bin/env python3
"""White Room 시뮬레이션 실행 스크립트"""

import argparse
import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# .env 파일 로드
from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from games.white_room.simulation import WhiteRoomSimulation


def main():
    parser = argparse.ArgumentParser(description="White Room Simulation Runner")
    parser.add_argument(
        "--config",
        type=str,
        default="games/white_room/config/phase1_default.yaml",
        help="Path to config YAML file",
    )
    parser.add_argument(
        "--language", "-l",
        type=str,
        choices=["ko", "en"],
        help="Override language setting",
    )
    parser.add_argument(
        "--adapter", "-a",
        type=str,
        help="Override default adapter (mock, anthropic, google, ollama)",
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        help="Override default model",
    )
    parser.add_argument(
        "--seed", "-s",
        type=int,
        help="Override random seed",
    )
    parser.add_argument(
        "--epochs", "-e",
        type=int,
        help="Override total epochs",
    )

    args = parser.parse_args()

    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = project_root / config_path

    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)

    sim = WhiteRoomSimulation(str(config_path))

    # Apply overrides
    if args.language:
        sim.language = args.language
    if args.adapter:
        # Re-create adapters with new type
        from engine.adapters import create_adapter
        for agent in sim.agents:
            sim.adapters[agent.id] = create_adapter(
                args.adapter,
                model=args.model or sim.config.get("default_model", "mock"),
                persona=agent.persona,
                agent_id=agent.id,
            )
    if args.seed is not None:
        import random
        random.seed(args.seed)
    if args.epochs:
        sim.total_epochs = args.epochs

    sim.run()


if __name__ == "__main__":
    main()
