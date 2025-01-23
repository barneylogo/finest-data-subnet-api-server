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

    @staticmethod
    def get_neurons() -> list:
        try:
            metagraph = BittensorService.get_metagraph()
            return [
                {
                    "netuid": node.netuid,
                    "uid": node.uid,
                    "hotkey": node.hotkey,
                    "coldkey": node.coldkey,
                    "ip": node.prometheus_info.ip,
                    "port": node.prometheus_info.port,
                    "stake": node.stake.tao,
                    "rank": node.rank,
                    "emission": node.emission,
                    "incentive": node.incentive,
                    "consensus": node.consensus,
                    "trust": node.trust,
                    "validator_trust": node.validator_trust,
                    "dividends": node.dividends,
                    "validator_permit": node.validator_permit,
                    "active": node.active,
                    "last_update": node.last_update,
                }
                for node in metagraph.neurons
            ]
        except Exception as e:
            raise RuntimeError(f"Failed to get neurons: {e}") from e

    @staticmethod
    def get_validators() -> list:
        try:
            metagraph = BittensorService.get_metagraph()
            return [
                {
                    "uid": node.uid,
                    "hotkey": node.hotkey,
                    "stake": node.stake.tao,
                    "validator_trust": node.validator_trust,
                    "rank": node.rank,
                    "incentive": node.incentive,
                    "emission": node.emission,
                    "active": node.active,
                    "last_update": node.last_update,
                }
                for node in metagraph.neurons
                if node.validator_permit
                and node.validator_trust > 0
                and node.dividends > 0
                and node.stake.tao > settings.BITTENSOR_VALIDATOR_STAKE_THRESHOLD
            ]
        except Exception as e:
            raise RuntimeError(f"Failed to get validators: {e}") from e

    @staticmethod
    def get_miners() -> list:
        try:
            metagraph = BittensorService.get_metagraph()
            return [
                {
                    "uid": node.uid,
                    "hotkey": node.hotkey,
                    "incentive": node.incentive,
                }
                for node in metagraph.neurons
                if node.trust > 0 and node.incentive > 0
            ]
        except Exception as e:
            raise RuntimeError(f"Failed to get validators: {e}") from e

    @staticmethod
    def get_subnet_stats():
        try:
            metagraph = BittensorService.get_metagraph()
            nodes = metagraph.neurons

            total_nodes = len(nodes)
            active_nodes = len([node for node in nodes if node.active])
            inactive_nodes = total_nodes - active_nodes

            total_stake = sum([node.stake.tao for node in nodes])

            return {
                "total_nodes": total_nodes,
                "active_nodes": active_nodes,
                "inactive_nodes": inactive_nodes,
                "total_stake": total_stake,
            }
        except Exception as e:
            raise RuntimeError(f"Failed to get subnet stats: {e}") from e
