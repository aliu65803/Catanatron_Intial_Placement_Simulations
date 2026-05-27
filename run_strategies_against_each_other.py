import random
from catanatron import Color, RandomPlayer, ActionType, Player
from catanatron.models.enums import WOOD, BRICK, SHEEP, WHEAT, ORE, ActionPrompt
from catanatron.cli.play import play_batch, GameConfigOptions, OutputOptions
from catanatron.state_functions import get_player_freqdeck
from catanatron.players.weighted_random import WeightedRandomPlayer
from collections import Counter

class HeadToHeadPlayer(Player):
    def __init__(self, color, strategy_name):
        super().__init__(color)
        self.strategy_name = strategy_name
        self.base_simulator_bot = WeightedRandomPlayer(color)

    def decide(self, game, playable_actions):
        # 1. Handle Setup Choices Based on Assigned Archetype
        if game.state.current_prompt == ActionPrompt.BUILD_INITIAL_SETTLEMENT:
            settle_actions = [a for a in playable_actions if a.action_type == ActionType.BUILD_SETTLEMENT]
            if settle_actions:
                if self.strategy_name == "PROBABILITY":
                    return self.pick_highest_yield(game, settle_actions)
                elif self.strategy_name == "DIVERSITY":
                    return self.pick_diverse_resource(game, settle_actions)
                elif self.strategy_name == "CITY_FOCUS":
                    return self.pick_by_resource_priority(game, settle_actions, [ORE, WHEAT, SHEEP])
                elif self.strategy_name == "SETTLEMENT_FOCUS":
                    return self.pick_by_resource_priority(game, settle_actions, [WOOD, BRICK])

        # 2. Standardized execution playground for midgame parity
        return self.base_simulator_bot.decide(game, playable_actions)
    
    def get_node_pips(self, game, node_id):
        total_pips = 0
        adjacent_tiles = game.state.board.map.adjacent_tiles.get(node_id, [])
        for tile in adjacent_tiles:
            if tile.number:
                total_pips += (6 - abs(7 - tile.number))
        return total_pips

    def pick_highest_yield(self, game, actions):
        if not actions: return None
        return max(actions, key=lambda a: self.get_node_pips(game, a.value))

    def pick_diverse_resource(self, game, actions):
        if not actions: return None
        current_deck = get_player_freqdeck(game.state, self.color)
        res_list = [WOOD, BRICK, SHEEP, WHEAT, ORE]
        owned_resources = [res_list[i] for i, count in enumerate(current_deck) if count > 0]
        
        for action in actions:
            adj_tiles = game.state.board.map.adjacent_tiles.get(action.value, [])
            for tile in adj_tiles:
                if tile.resource and tile.resource not in owned_resources:
                    return action
        return actions[0]

    def pick_by_resource_priority(self, game, actions, priority_res):
        if not actions: return None
        
        def score_action(a):
            score = 0
            adj_tiles = game.state.board.map.adjacent_tiles.get(a.value, [])
            for tile in adj_tiles:
                if tile.resource in priority_res and tile.number:
                    score += (6 - abs(7 - tile.number))
            return score

        return max(actions, key=score_action)

def run_battle_royale():
    num_games = 1000 # 1,000 runs will execute in 2-3 seconds via CLI optimization
    print(f"\n--- Running Head-to-Head Battle Royale ({num_games} games, Seating Shuffled) ---")
    
    # Give every strategy a seat at the table
    players = [
        HeadToHeadPlayer(Color.RED, "PROBABILITY"),
        HeadToHeadPlayer(Color.BLUE, "DIVERSITY"),
        HeadToHeadPlayer(Color.WHITE, "CITY_FOCUS"),
        HeadToHeadPlayer(Color.ORANGE, "SETTLEMENT_FOCUS"),
    ]
    
    # Setting the final argument to True enables automatic player array shuffling 
    # before each game, completely neutralizing turn-order advantages.
    batch_results = play_batch(
        num_games, 
        players, 
        OutputOptions(None, None, False, False, False), 
        GameConfigOptions(7, 10, "BASE"), 
        True 
    )
    
    winners = batch_results[0]
    win_counts = Counter(winners)
    
    # Map strategies back to their respective colors to report the final standings accurately
    print(f"\n===== FINAL STANDINGS =====")
    for p in players:
        count = win_counts.get(p.color, 0)
        percentage = (count / num_games) * 100
        print(f"  Strategy {p.strategy_name:<18} ({p.color.name}): {percentage:.2f}% ({count} wins)")

if __name__ == "__main__":
    run_battle_royale()