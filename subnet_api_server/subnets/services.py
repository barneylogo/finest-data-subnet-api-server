# myapp/management/commands/fetch_data.py
import argparse

import bittensor as bt


class BittensorService:
    def __init__(self, config: bt.config):
        self.config = config
        self.subtensor = bt.subtensor(config=config)

    def get_current_block(self):
        try:
            return self.subtensor.get_current_block()
        except Exception as e:
            raise RuntimeError("Failed to get current block") from e

    def get_config(self):
        # Add your Bittensor config logic here
        # The rest of the method remains unchanged
        parser = argparse.ArgumentParser(
            description="Commit dataset to Bittensor subtensor chain.",
        )
        parser.add_argument(
            "--netuid",
            type=int,
            default=250,
            help="The unique identifier for the network",
        )
        parser.add_argument(
            "--subtensor.network",
            type=str,
            default="test",
            help="The unique identifier for the network",
        )
        bt.wallet.add_args(parser)
        bt.subtensor.add_args(parser)
        return bt.config(parser)
