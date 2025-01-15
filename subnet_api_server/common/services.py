# myapp/management/commands/fetch_data.py
import argparse

import bittensor as bt
from django.conf import settings


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
            default=settings.BITTENSOR_NETWORK_UID,
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
            subtensor = BittensorService.get_subtensor()
            return subtensor.get_current_block()
        except Exception as e:
            raise RuntimeError(f"Failed to get current block: {e}") from e

    @staticmethod
    def get_subtensor() -> bt.subtensor:
        try:
            config = BittensorService.get_config()
            return bt.subtensor(network=settings.BITTENSOR_NETWORK, config=config)
        except Exception as e:
            raise RuntimeError(f"Failed to get subtensor: {e}") from e

    @staticmethod
    def get_metagraph() -> bt.metagraph:
        try:
            config = BittensorService.get_config()
            subtensor = BittensorService.get_subtensor()
            return subtensor.metagraph(netuid=config.netuid)
        except Exception as e:
            raise RuntimeError(f"Failed to get metagraph: {e}") from e
