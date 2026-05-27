# # import random
# # from catanatron import Color, RandomPlayer, ActionType, Player
# # from catanatron.models.enums import WOOD, BRICK, SHEEP, WHEAT, ORE, ActionPrompt
# # from catanatron.cli.play import play_batch, GameConfigOptions, OutputOptions
# # from catanatron.state_functions import get_player_freqdeck
# # from catanatron.players.weighted_random import WeightedRandomPlayer # A highly optimized fast simulation bot
# # from collections import Counter

# # class FastSimulationStrategyPlayer(Player):
# #     def __init__(self, color, strategy_name):
# #         super().__init__(color)
# #         self.strategy_name = strategy_name
        
# #         # Instantiate a fast simulation-driven bot to play the rest of the game.
# #         # This player runs instantly via the CLI loop because it uses static matrix weights 
# #         # instead of building massive tree graphs like MCTS.
# #         self.base_simulator_bot = WeightedRandomPlayer(color)

# #     def decide(self, game, playable_actions):
# #         # 1. STRATEGIC SETUP INTERCEPTION
# #         # Only use your custom heuristics for placing the initial settlements
# #         if game.state.current_prompt == ActionPrompt.BUILD_INITIAL_SETTLEMENT:
# #             settle_actions = [a for a in playable_actions if a.action_type == ActionType.BUILD_SETTLEMENT]
# #             if settle_actions:
# #                 if self.strategy_name == "PROBABILITY":
# #                     return self.pick_highest_yield(game, settle_actions)
# #                 elif self.strategy_name == "DIVERSITY":
# #                     return self.pick_diverse_resource(game, settle_actions)
# #                 elif self.strategy_name == "CITY_FOCUS":
# #                     return self.pick_by_resource_priority(game, settle_actions, [ORE, WHEAT, SHEEP])
# #                 elif self.strategy_name == "SETTLEMENT_FOCUS":
# #                     return self.pick_by_resource_priority(game, settle_actions, [WOOD, BRICK])

# #         # 2. FAST CLI SIMULATION RESUMPTION
# #         # For roads, rolls, trading, and post-setup expansion, let the fast bot execute instantly
# #         return self.base_simulator_bot.decide(game, playable_actions)
    
# #     def get_node_pips(self, game, node_id):
# #         total_pips = 0
# #         adjacent_tiles = game.state.board.map.adjacent_tiles.get(node_id, [])
# #         for tile in adjacent_tiles:
# #             if tile.number:
# #                 total_pips += (6 - abs(7 - tile.number))
# #         return total_pips

# #     def pick_highest_yield(self, game, actions):
# #         if not actions: return None
# #         return max(actions, key=lambda a: self.get_node_pips(game, a.value))

# #     def pick_diverse_resource(self, game, actions):
# #         if not actions: return None
# #         current_deck = get_player_freqdeck(game.state, self.color)
# #         res_list = [WOOD, BRICK, SHEEP, WHEAT, ORE]
# #         owned_resources = [res_list[i] for i, count in enumerate(current_deck) if count > 0]
        
# #         for action in actions:
# #             adj_tiles = game.state.board.map.adjacent_tiles.get(action.value, [])
# #             for tile in adj_tiles:
# #                 if tile.resource and tile.resource not in owned_resources:
# #                     return action
# #         return actions[0]

# #     def pick_by_resource_priority(self, game, actions, priority_res):
# #         if not actions: return None
        
# #         def score_action(a):
# #             score = 0
# #             adj_tiles = game.state.board.map.adjacent_tiles.get(a.value, [])
# #             for tile in adj_tiles:
# #                 if tile.resource in priority_res and tile.number:
# #                     score += (6 - abs(7 - tile.number))
# #             return score

# #         return max(actions, key=score_action)

# # def run_comparison():
# #     strategies = ["PROBABILITY", "DIVERSITY", "CITY_FOCUS", "SETTLEMENT_FOCUS"]
# #     num_games = 1000 # Fully restored to 1,000 games!
    
# #     for strat in strategies:
# #         print(f"\n--- Running Fast Simulation: {strat} Setup vs 3 RandomPlayers ({num_games} games) ---")
        
# #         players = [
# #             FastSimulationStrategyPlayer(Color.RED, strat),
# #             RandomPlayer(Color.BLUE),
# #             RandomPlayer(Color.WHITE),
# #             RandomPlayer(Color.ORANGE),
# #         ]
        
# #         batch_results = play_batch(
# #             num_games, 
# #             players, 
# #             OutputOptions(None, None, False, False, False), 
# #             GameConfigOptions(7, 10, "BASE"), 
# #             True 
# #         )
        
# #         winners = batch_results[0]
# #         win_counts = Counter(winners)
        
# #         print(f"\nResults for {strat}:")
# #         for color in [Color.RED, Color.BLUE, Color.WHITE, Color.ORANGE]:
# #             count = win_counts.get(color, 0)
# #             percentage = (count / num_games) * 100
# #             player_type = "Strategy+Sim" if color == Color.RED else "Random"
# #             print(f"  {color.name} ({player_type}): {percentage:.2f}% ({count} wins)")

# # if __name__ == "__main__":
# #     run_comparison()

# import random
# from catanatron import Color, RandomPlayer, ActionType, Player
# from catanatron.models.enums import WOOD, BRICK, SHEEP, WHEAT, ORE, ActionPrompt
# from catanatron.cli.play import play_batch, GameConfigOptions, OutputOptions
# from catanatron.state_functions import get_player_freqdeck
# from catanatron.players.weighted_random import WeightedRandomPlayer # A highly optimized fast simulation bot
# from collections import Counter

# class FastSimulationStrategyPlayer(Player):
#     def __init__(self, color, strategy_name):
#         super().__init__(color)
#         self.strategy_name = strategy_name
        
#         # Instantiate a fast simulation-driven bot to play the rest of the game.
#         # This player runs instantly via the CLI loop because it uses static matrix weights 
#         # instead of building massive tree graphs like MCTS.
#         self.base_simulator_bot = WeightedRandomPlayer(color)

#     def decide(self, game, playable_actions):
#         # 1. STRATEGIC SETUP INTERCEPTION
#         # Only use your custom heuristics for placing the initial settlements
#         if game.state.current_prompt == ActionPrompt.BUILD_INITIAL_SETTLEMENT:
#             settle_actions = [a for a in playable_actions if a.action_type == ActionType.BUILD_SETTLEMENT]
#             if settle_actions:
#                 if self.strategy_name == "PROBABILITY":
#                     return self.pick_highest_yield(game, settle_actions)
#                 elif self.strategy_name == "DIVERSITY":
#                     return self.pick_diverse_resource(game, settle_actions)
#                 elif self.strategy_name == "NUMBER_DIVERSITY":
#                     return self.pick_diverse_numbers(game, settle_actions)
#                 elif self.strategy_name == "HYBRID_DIVERSITY":
#                     return self.pick_hybrid_diversity(game, settle_actions)
#                 elif self.strategy_name == "CITY_FOCUS":
#                     return self.pick_by_resource_priority(game, settle_actions, [ORE, WHEAT, SHEEP])
#                 elif self.strategy_name == "SETTLEMENT_FOCUS":
#                     return self.pick_by_resource_priority(game, settle_actions, [WOOD, BRICK])

#         # 2. FAST CLI SIMULATION RESUMPTION
#         # For roads, rolls, trading, and post-setup expansion, let the fast bot execute instantly
#         return self.base_simulator_bot.decide(game, playable_actions)
    
#     def get_node_pips(self, game, node_id):
#         total_pips = 0
#         adjacent_tiles = game.state.board.map.adjacent_tiles.get(node_id, [])
#         for tile in adjacent_tiles:
#             if tile.number:
#                 total_pips += (6 - abs(7 - tile.number))
#         return total_pips

#     def pick_highest_yield(self, game, actions):
#         if not actions: return None
#         return max(actions, key=lambda a: self.get_node_pips(game, a.value))

#     def pick_diverse_resource(self, game, actions):
#         if not actions: return None
#         current_deck = get_player_freqdeck(game.state, self.color)
#         res_list = [WOOD, BRICK, SHEEP, WHEAT, ORE]
#         owned_resources = [res_list[i] for i, count in enumerate(current_deck) if count > 0]
        
#         for action in actions:
#             adj_tiles = game.state.board.map.adjacent_tiles.get(action.value, [])
#             for tile in adj_tiles:
#                 if tile.resource and tile.resource not in owned_resources:
#                     return action
#         return actions[0]

#     def pick_diverse_numbers(self, game, actions):
#         """Prioritizes expanding onto distinct token roll numbers not already owned."""
#         if not actions: return None
        
#         # Correctly determine numbers currently owned by inspecting state dictionaries directly
#         owned_numbers = set()
#         for node_id, player_color in game.state.settlements.items():
#             if player_color == self.color:
#                 adj_tiles = game.state.board.map.adjacent_tiles.get(node_id, [])
#                 for tile in adj_tiles:
#                     if tile.number:
#                         owned_numbers.add(tile.number)
                        
#         for node_id, player_color in game.state.cities.items():
#             if player_color == self.color:
#                 adj_tiles = game.state.board.map.adjacent_tiles.get(node_id, [])
#                 for tile in adj_tiles:
#                     if tile.number:
#                         owned_numbers.add(tile.number)

#         def score_number_diversity(a):
#             score = 0
#             adj_tiles = game.state.board.map.adjacent_tiles.get(a.value, [])
#             for tile in adj_tiles:
#                 if tile.number:
#                     # Grant a premium for a production number you don't already have
#                     if tile.number not in owned_numbers:
#                         score += 3  # Distinct number coverage bonus
#                     # Base pip value added as a tie-breaker so we prefer higher probability spots
#                     score += (6 - abs(7 - tile.number))
#             return score

#         return max(actions, key=score_number_diversity)

#     def pick_hybrid_diversity(self, game, actions):
#         """Combines resource variety and number token variety into a multi-factor score."""
#         if not actions: return None
        
#         # 1. Identify currently owned resources using your freqdeck helper
#         current_deck = get_player_freqdeck(game.state, self.color)
#         res_list = [WOOD, BRICK, SHEEP, WHEAT, ORE]
#         owned_resources = {res_list[i] for i, count in enumerate(current_deck) if count > 0}
        
#         # 2. Identify currently owned numbers directly from state dictionaries
#         owned_numbers = set()
#         for state_dict in [game.state.settlements, game.state.cities]:
#             for node_id, player_color in state_dict.items():
#                 if player_color == self.color:
#                     adj_tiles = game.state.board.map.adjacent_tiles.get(node_id, [])
#                     for tile in adj_tiles:
#                         if tile.number:
#                             owned_numbers.add(tile.number)

#         def score_hybrid(a):
#             score = 0
#             adj_tiles = game.state.board.map.adjacent_tiles.get(a.value, [])
#             seen_in_action_res = set()
#             seen_in_action_nums = set()
            
#             for tile in adj_tiles:
#                 if not tile.number:
#                     continue
                
#                 # Base pip yield
#                 pips = (6 - abs(7 - tile.number))
#                 score += pips
                
#                 # Resource Diversity Bonus
#                 if tile.resource and tile.resource not in owned_resources and tile.resource not in seen_in_action_res:
#                     score += 5  # Strong incentive to get a missing resource type
#                     seen_in_action_res.add(tile.resource)
                    
#                 # Number Diversity Bonus
#                 if tile.number not in owned_numbers and tile.number not in seen_in_action_nums:
#                     score += 3  # Incentive to spread across different roll frequencies
#                     seen_in_action_nums.add(tile.number)
#             return score

#         return max(actions, key=score_hybrid)
#     def pick_by_resource_priority(self, game, actions, priority_res):
#         if not actions: return None
        
#         def score_action(a):
#             score = 0
#             adj_tiles = game.state.board.map.adjacent_tiles.get(a.value, [])
#             for tile in adj_tiles:
#                 if tile.resource in priority_res and tile.number:
#                     score += (6 - abs(7 - tile.number))
#             return score

#         return max(actions, key=score_action)

# def run_comparison():
#     strategies = [
#         "PROBABILITY", 
#         "DIVERSITY", 
#         "NUMBER_DIVERSITY", 
#         "HYBRID_DIVERSITY", 
#         "CITY_FOCUS", 
#         "SETTLEMENT_FOCUS"
#     ]
#     num_games = 1000 # Fully restored to 1,000 games!
    
#     for strat in strategies:
#         print(f"\n--- Running Fast Simulation: {strat} Setup vs 3 RandomPlayers ({num_games} games) ---")
        
#         players = [
#             FastSimulationStrategyPlayer(Color.RED, strat),
#             RandomPlayer(Color.BLUE),
#             RandomPlayer(Color.WHITE),
#             RandomPlayer(Color.ORANGE),
#         ]
        
#         batch_results = play_batch(
#             num_games, 
#             players, 
#             OutputOptions(None, None, False, False, False), 
#             GameConfigOptions(7, 10, "BASE"), 
#             True 
#         )
        
#         winners = batch_results[0]
#         win_counts = Counter(winners)
        
#         print(f"\nResults for {strat}:")
#         for color in [Color.RED, Color.BLUE, Color.WHITE or Color.ORANGE]:
#             color_keys = [Color.RED, Color.BLUE, Color.WHITE, Color.ORANGE]
#         for color in color_keys:
#             count = win_counts.get(color, 0)
#             percentage = (count / num_games) * 100
#             player_type = "Strategy+Sim" if color == Color.RED else "Random"
#             print(f"  {color.name} ({player_type}): {percentage:.2f}% ({count} wins)")

# if __name__ == "__main__":
#     run_comparison()

import random
from collections import Counter

from catanatron import Color, RandomPlayer, ActionType, Player
from catanatron.models.enums import WOOD, BRICK, SHEEP, WHEAT, ORE, ActionPrompt
from catanatron.cli.play import play_batch, GameConfigOptions, OutputOptions
from catanatron.state_functions import get_player_freqdeck
from catanatron.players.weighted_random import WeightedRandomPlayer # A highly optimized fast simulation bot

class FastSimulationStrategyPlayer(Player):
    def __init__(self, color, strategy_name):
        super().__init__(color)
        self.strategy_name = strategy_name
        
        # Instantiate a fast simulation-driven bot to play the rest of the game.
        # This player runs instantly via the CLI loop because it uses static matrix weights 
        # instead of building massive tree graphs like MCTS.
        self.base_simulator_bot = WeightedRandomPlayer(color)

    def decide(self, game, playable_actions):
        # 1. STRATEGIC SETUP INTERCEPTION
        # Only use your custom heuristics for placing the initial settlements
        if game.state.current_prompt == ActionPrompt.BUILD_INITIAL_SETTLEMENT:
            settle_actions = [a for a in playable_actions if a.action_type == ActionType.BUILD_SETTLEMENT]
            if settle_actions:
                if self.strategy_name == "PROBABILITY":
                    return self.pick_highest_yield(game, settle_actions)
                elif self.strategy_name == "DIVERSITY":
                    return self.pick_diverse_resource(game, settle_actions)
                elif self.strategy_name == "NUMBER_DIVERSITY":
                    return self.pick_diverse_numbers(game, settle_actions)
                elif self.strategy_name == "HYBRID_DIVERSITY":
                    return self.pick_hybrid_diversity(game, settle_actions)
                elif self.strategy_name == "CITY_FOCUS":
                    return self.pick_by_resource_priority(game, settle_actions, [ORE, WHEAT, SHEEP])
                elif self.strategy_name == "SETTLEMENT_FOCUS":
                    return self.pick_by_resource_priority(game, settle_actions, [WOOD, BRICK])

        # 2. FAST CLI SIMULATION RESUMPTION
        # For roads, rolls, trading, and post-setup expansion, let the fast bot execute instantly
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

    def pick_diverse_numbers(self, game, actions):
        """Prioritizes expanding onto distinct token roll numbers not already owned."""
        if not actions: return None
        
        # Determine numbers currently owned by inspecting the board's buildings
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
                    # Grant a premium for a production number you don't already have
                    if tile.number not in owned_numbers:
                        score += 3  # Distinct number coverage bonus
                    # Base pip value added as a tie-breaker (prefer higher probability spots)
                    score += (6 - abs(7 - tile.number))
            return score

        return max(actions, key=score_number_diversity)

    def pick_hybrid_diversity(self, game, actions):
        """Combines resource variety and number token variety into a multi-factor score."""
        if not actions: return None
        
        # 1. Identify currently owned resources
        current_deck = get_player_freqdeck(game.state, self.color)
        res_list = [WOOD, BRICK, SHEEP, WHEAT, ORE]
        owned_resources = {res_list[i] for i, count in enumerate(current_deck) if count > 0}
        
        # 2. Identify currently owned numbers directly from board buildings
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
                
                # Base pip yield (Probability)
                pips = (6 - abs(7 - tile.number))
                score += pips
                
                # Resource Diversity Bonus
                if tile.resource and tile.resource not in owned_resources and tile.resource not in seen_in_action_res:
                    score += 5  # Strong incentive to get a missing resource type
                    seen_in_action_res.add(tile.resource)
                    
                # Number Diversity Bonus
                if tile.number not in owned_numbers and tile.number not in seen_in_action_nums:
                    score += 3  # Incentive to spread across different roll frequencies
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

def run_comparison():
    strategies = [
        "PROBABILITY", 
        "DIVERSITY", 
        "NUMBER_DIVERSITY", 
        "HYBRID_DIVERSITY", 
        "CITY_FOCUS", 
        "SETTLEMENT_FOCUS"
    ]
    num_games = 1000 # Fully restored to 1,000 games!
    
    for strat in strategies:
        print(f"\n--- Running Fast Simulation: {strat} Setup vs 3 RandomPlayers ({num_games} games) ---")
        
        players = [
            FastSimulationStrategyPlayer(Color.RED, strat),
            RandomPlayer(Color.BLUE),
            RandomPlayer(Color.WHITE),
            RandomPlayer(Color.ORANGE),
        ]
        
        batch_results = play_batch(
            num_games, 
            players, 
            OutputOptions(None, None, False, False, False), 
            GameConfigOptions(7, 10, "BASE"), 
            True 
        )
        
        winners = batch_results[0]
        win_counts = Counter(winners)
        
        print(f"\nResults for {strat}:")
        color_keys = [Color.RED, Color.BLUE, Color.WHITE, Color.ORANGE]
        for color in color_keys:
            count = win_counts.get(color, 0)
            percentage = (count / num_games) * 100
            player_type = "Strategy+Sim" if color == Color.RED else "Random"
            print(f"  {color.name} ({player_type}): {percentage:.2f}% ({count} wins)")

if __name__ == "__main__":
    run_comparison()