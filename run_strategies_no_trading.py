import random
from collections import Counter
from catanatron import Color, RandomPlayer, ActionType, Player
from catanatron.models.enums import WOOD, BRICK, SHEEP, WHEAT, ORE
from catanatron.cli.play import play_batch, GameConfigOptions, OutputOptions
from catanatron.state_functions import get_player_freqdeck

class StrategyPlayer(Player):
    def __init__(self, color, strategy_name):
        super().__init__(color)
        self.strategy_name = strategy_name

    def decide(self, game, playable_actions):
        # 1. Gather all action types currently available to choose from
        action_types = [a.action_type for a in playable_actions]

        # 2. Mandatory Step: If we must roll the dice, do it immediately
        if ActionType.ROLL in action_types:
            return [a for a in playable_actions if a.action_type == ActionType.ROLL][0]

        # 3. Separate settlement actions and city actions
        settle_actions = [a for a in playable_actions if a.action_type == ActionType.BUILD_SETTLEMENT]
        city_actions = [a for a in playable_actions if a.action_type == ActionType.BUILD_CITY]
        all_building = settle_actions + city_actions

        # 4. If any building option is available, apply the core strategic choice
        if all_building:
            if self.strategy_name == "PROBABILITY":
                return self.pick_highest_yield(game, all_building)
            elif self.strategy_name == "DIVERSITY":
                return self.pick_diverse_resource(game, all_building)
            elif self.strategy_name == "NUMBER_DIVERSITY":
                return self.pick_diverse_numbers(game, all_building)
            elif self.strategy_name == "HYBRID_DIVERSITY":
                return self.pick_hybrid_diversity(game, all_building)
            elif self.strategy_name == "CITY_FOCUS":
                return self.pick_by_resource_priority(game, all_building, [ORE, WHEAT, SHEEP])
            elif self.strategy_name == "SETTLEMENT_FOCUS":
                return self.pick_by_resource_priority(game, all_building, [WOOD, BRICK])

        # 5. Mandatory Step: Handle mandatory roads (like during the initial placement phase)
        road_actions = [a for a in playable_actions if a.action_type == ActionType.BUILD_ROAD]
        if road_actions:
            return road_actions[0]

        # 6. Mandatory Step: If we are done moving/building, explicitly end our turn
        if ActionType.END_TURN in action_types:
            return [a for a in playable_actions if a.action_type == ActionType.END_TURN][0]

        # Final safety fallback for things like discarding cards or moving the robber
        return playable_actions[0]

    def get_node_pips(self, game, node_id):
        total_pips = 0
        # Look up adjacent LandTile objects mapped to this specific node index
        adjacent_tiles = game.state.board.map.adjacent_tiles.get(node_id, [])
        for tile in adjacent_tiles:
            if tile.number:
                # Map standard roll distributions (e.g., a 6 or 8 yields 5 pips)
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
        
        # Try to find a building option that targets a resource type we lack entirely
        for action in actions:
            adj_tiles = game.state.board.map.adjacent_tiles.get(action.value, [])
            for tile in adj_tiles:
                if tile.resource and tile.resource not in owned_resources:
                    return action
        return actions[0]

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
                        score += 3  
                    score += (6 - abs(7 - tile.number))
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
                
                pips = (6 - abs(7 - tile.number))
                score += pips
                
                if tile.resource and tile.resource not in owned_resources and tile.resource not in seen_in_action_res:
                    score += 5  
                    seen_in_action_res.add(tile.resource)
                    
                if tile.number not in owned_numbers and tile.number not in seen_in_action_nums:
                    score += 3  
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
    num_games = 100 
    
    for strat in strategies:
        print(f"\n--- Testing {strat} vs 3 RandomPlayers ({num_games} games) ---")
        
        players = [
            StrategyPlayer(Color.RED, strat),
            RandomPlayer(Color.BLUE),
            RandomPlayer(Color.WHITE),
            RandomPlayer(Color.ORANGE),
        ]
        
        # Run batch simulation using core library runner
        batch_results = play_batch(
            num_games, 
            players, 
            OutputOptions(None, None, False, False, False), 
            GameConfigOptions(7, 10, "BASE"), 
            True 
        )
        
        # Extract individual winners from the returned results tuple
        winners = batch_results[0]
        win_counts = Counter(winners)
        
        print(f"\nResults for {strat}:")
        for color in [Color.RED, Color.BLUE, Color.WHITE, Color.ORANGE]:
            count = win_counts.get(color, 0)
            percentage = (count / num_games) * 100
            player_type = "Strategy" if color == Color.RED else "Random"
            print(f"  {color.name} ({player_type}): {percentage:.2f}% ({count} wins)")


if __name__ == "__main__":
    run_comparison()