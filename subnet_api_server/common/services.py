# myapp/management/commands/fetch_data.py
import argparse

import bittensor as bt

from config import settings


class BittensorService:

    @staticmethod
    def get_config() -> bt.config:
        # Add your Bittensor config logic here
        # The rest of the method remains unchanged

        network = settings.BITTENSOR_NETWORK

        parser = argparse.ArgumentParser(
            description="Commit dataset to Bittensor subtensor chain.",
        )
        parser.add_argument(
            "--netuid",
            type=int,
            default=(250 if network == "test" else 0),
            help="The unique identifier for the network",
        )
        parser.add_argument(
            "--subtensor.network",
            type=str,
            default=network,
            help="The unique identifier for the network",
        )
        bt.wallet.add_args(parser)
        bt.subtensor.add_args(parser)

        return bt.config(parser)

    @staticmethod
    def get_current_block() -> int:
        try:
            config = BittensorService.get_config()
            subtensor = bt.subtensor(config)
            return subtensor.get_current_block()
        except Exception as e:
            raise RuntimeError("Failed to get current block") from e

    @staticmethod
    def get_subtensor() -> bt.subtensor:
        try:
            config = BittensorService.get_config()
            return bt.subtensor(config)
        except Exception as e:
            raise RuntimeError("Failed to get subtensor") from e

    @staticmethod
    def get_metagraph() -> bt.metagraph:
        try:
            config = BittensorService.get_config()
            subtensor = bt.subtensor(config)
            return subtensor.metagraph(netuid=config.netuid)
        except Exception as e:
            raise RuntimeError("Failed to get metagraph") from e
