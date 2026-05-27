import random
from collections import Counter

from catanatron import Color, RandomPlayer, ActionType, Player
from catanatron.models.enums import WOOD, BRICK, SHEEP, WHEAT, ORE, ActionPrompt
from catanatron.cli.play import play_batch, GameConfigOptions, OutputOptions
from catanatron.state_functions import get_player_freqdeck
from catanatron.players.weighted_random import WeightedRandomPlayer

class TopFourBattleRoyalePlayer(Player):
    def __init__(self, color, strategy_name):
        super().__init__(color)
        self.strategy_name = strategy_name
        
        # Optimized static-weights simulation bot for lightning-fast midgame execution
        self.base_simulator_bot = WeightedRandomPlayer(color)

    def decide(self, game, playable_actions):
        # 1. STRATEGIC SETUP INTERCEPTION
        if game.state.current_prompt == ActionPrompt.BUILD_INITIAL_SETTLEMENT:
            settle_actions = [a for a in playable_actions if a.action_type == ActionType.BUILD_SETTLEMENT]
            if settle_actions:
                if self.strategy_name == "HYBRID_DIVERSITY":
                    return self.pick_hybrid_diversity(game, settle_actions)
                elif self.strategy_name == "PROBABILITY":
                    return self.pick_highest_yield(game, settle_actions)
                elif self.strategy_name == "NUMBER_DIVERSITY":
                    return self.pick_diverse_numbers(game, settle_actions)
                elif self.strategy_name == "CITY_FOCUS":
                    return self.pick_by_resource_priority(game, settle_actions, [ORE, WHEAT, SHEEP])

        # 2. FAST CLI SIMULATION RESUMPTION
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

    def pick_diverse_numbers(self, game, actions):
        if not actions: return None
        
        owned_numbers = set()
        for node_id, (building_color, building_type) in game.state.board.buildings.items():
            if building_color == self.color:
                adj_tiles = game.state.board.map.adjacent_tiles.get(node_id, [])
                for tile in adj_tiles:
                    if tile.number:
                        owned_numbers.add(tile.number)

        def score_number_diversity(a):
            score = 0
            adj_tiles = game.state.board.map.adjacent_tiles.get(a.value, [])
            for tile in adj_tiles:
                if tile.number:
                    if tile.number not in owned_numbers:
                        score += 3  # Distinct number coverage bonus
                    score += (6 - abs(7 - tile.number))  # Base pips tie-breaker
            return score

        return max(actions, key=score_number_diversity)

    def pick_hybrid_diversity(self, game, actions):
        if not actions: return None
        
        current_deck = get_player_freqdeck(game.state, self.color)
        res_list = [WOOD, BRICK, SHEEP, WHEAT, ORE]
        owned_resources = {res_list[i] for i, count in enumerate(current_deck) if count > 0}
        
        owned_numbers = set()
        for node_id, (building_color, building_type) in game.state.board.buildings.items():
            if building_color == self.color:
                adj_tiles = game.state.board.map.adjacent_tiles.get(node_id, [])
                for tile in adj_tiles:
                    if tile.number:
                        owned_numbers.add(tile.number)

        def score_hybrid(a):
            score = 0
            adj_tiles = game.state.board.map.adjacent_tiles.get(a.value, [])
            seen_in_action_res = set()
            seen_in_action_nums = set()
            
            for tile in adj_tiles:
                if not tile.number:
                    continue
                
                score += (6 - abs(7 - tile.number))  # Base pip yield
                
                if tile.resource and tile.resource not in owned_resources and tile.resource not in seen_in_action_res:
                    score += 5  # Missing resource type premium
                    seen_in_action_res.add(tile.resource)
                    
                if tile.number not in owned_numbers and tile.number not in seen_in_action_nums:
                    score += 3  # Spreading roll frequency premium
                    seen_in_action_nums.add(tile.number)
            return score

        return max(actions, key=score_hybrid)
    
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

def run_top_four_battle_royale():
    num_games = 1000
    print(f"\n--- Running Top 4 Head-to-Head Battle Royale ({num_games} games, Seating Shuffled) ---")
    
    # Seating assignments for the four top-tier strategies
    players = [
        TopFourBattleRoyalePlayer(Color.RED, "HYBRID_DIVERSITY"),
        TopFourBattleRoyalePlayer(Color.BLUE, "PROBABILITY"),
        TopFourBattleRoyalePlayer(Color.WHITE, "NUMBER_DIVERSITY"),
        TopFourBattleRoyalePlayer(Color.ORANGE, "CITY_FOCUS"),
    ]
    
    # Final argument set to True automatically shuffles turn order every game
    batch_results = play_batch(
        num_games, 
        players, 
        OutputOptions(None, None, False, False, False), 
        GameConfigOptions(7, 10, "BASE"), 
        True 
    )
    
    winners = batch_results[0]
    win_counts = Counter(winners)
    
    print(f"\n===== ELITE TOP 4 STANDINGS =====")
    for p in players:
        count = win_counts.get(p.color, 0)
        percentage = (count / num_games) * 100
        print(f"  Strategy {p.strategy_name:<18} ({p.color.name}): {percentage:.2f}% ({count} wins)")

if __name__ == "__main__":
    run_top_four_battle_royale()