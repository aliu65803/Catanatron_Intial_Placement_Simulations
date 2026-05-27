import os
import json
import time
import random
from collections import Counter

# Core Catanatron imports
from catanatron import Color, ActionType, Player
from catanatron.models.enums import WOOD, BRICK, SHEEP, WHEAT, ORE, ActionPrompt
from catanatron.cli.play import play_batch, GameConfigOptions, OutputOptions
from catanatron.state_functions import get_player_freqdeck
from catanatron.players.weighted_random import WeightedRandomPlayer

# Modern Google GenAI SDK import
try:
    from google import genai
    from google.genai import types
    client = genai.Client() 
except ImportError:
    client = None

class GeminiStrategyPlayer(Player):
    def __init__(self, color, model_name="gemini-2.5-pro"):
        super().__init__(color)
        self.model_name = model_name
        self.base_simulator_bot = WeightedRandomPlayer(color)

    # Overriding __str__ changes how catanatron names this row in terminal tables
    def __str__(self):
        return f"GEMINI_{self.model_name.upper()}"

    def decide(self, game, playable_actions):
        if game.state.current_prompt == ActionPrompt.BUILD_INITIAL_SETTLEMENT:
            settle_actions = [a for a in playable_actions if a.action_type == ActionType.BUILD_SETTLEMENT]
            if settle_actions:
                if client is None:
                    return settle_actions[0]
                return self.decide_via_gemini(game, settle_actions)
        return self.base_simulator_bot.decide(game, playable_actions)

    def decide_via_gemini(self, game, settle_actions):
        options_data = []
        for action in settle_actions:
            node_id = action.value
            adjacent_tiles = game.state.board.map.adjacent_tiles.get(node_id, [])
            tiles_descriptions = []
            total_pips = 0
            
            for tile in adjacent_tiles:
                if tile.resource:
                    num = tile.number if tile.number else 0
                    pips = (6 - abs(7 - num)) if num > 0 else 0
                    total_pips += pips
                    tiles_descriptions.append(f"{tile.resource} (Number: {num}, Pips: {pips})")
            
            options_data.append({
                "option_index": len(options_data),
                "node_id": node_id,
                "total_pips": total_pips,
                "adjacent_tiles": tiles_descriptions
            })

        system_instruction = (
            "You are a competitive Settlers of Catan AI assistant specializing in board-state evaluation. "
            "Your task is to analyze the available initial settlement nodes and select the absolute best one. "
            "You MUST respond ONLY with a valid JSON object matching this schema: {\"chosen_index\": <integer>}"
        )

        user_prompt = f"Available Settlement Nodes:\n{json.dumps(options_data, indent=2)}\n\nWhich option index do you choose?"

        max_retries = 3
        backoff_delay = 2.0

        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=self.model_name,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        response_mime_type="application/json", 
                        temperature=0.1
                    ),
                )
                result = json.loads(response.text)
                chosen_idx = int(result.get("chosen_index", 0))
                if 0 <= chosen_idx < len(settle_actions):
                    print(f"[Gemini Action] Selected node index {chosen_idx} matching {options_data[chosen_idx]['total_pips']} pips.")
                    return settle_actions[chosen_idx]
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"[Gemini Error] API attempt failed ({e}). Retrying in {backoff_delay}s...")
                    time.sleep(backoff_delay)
                    backoff_delay *= 2
        return settle_actions[0]

class HeadToHeadPlayer(Player):
    def __init__(self, color, strategy_name):
        super().__init__(color)
        self.strategy_name = strategy_name
        self.base_simulator_bot = WeightedRandomPlayer(color)

    # Overriding __str__ changes how catanatron names this row in terminal tables
    def __str__(self):
        return f"STRATEGY:{self.strategy_name}"

    def decide(self, game, playable_actions):
        if game.state.current_prompt == ActionPrompt.BUILD_INITIAL_SETTLEMENT:
            settle_actions = [a for a in playable_actions if a.action_type == ActionType.BUILD_SETTLEMENT]
            if settle_actions:
                if self.strategy_name == "PROBABILITY":
                    return self.pick_highest_yield(game, settle_actions)
                elif self.strategy_name == "CITY_FOCUS":
                    return self.pick_by_resource_priority(game, settle_actions, [ORE, WHEAT, SHEEP])
                elif self.strategy_name == "SETTLEMENT_FOCUS":
                    return self.pick_by_resource_priority(game, settle_actions, [WOOD, BRICK])
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

def run_llm_vs_heuristics():
    total_games = 20  
    print(f"\n--- Running Head-to-Head Strategy Performance Analysis ({total_games} games, Seating Shuffled) ---")
    
    players = [
        GeminiStrategyPlayer(Color.RED, model_name="gemini-2.5-pro"),
        HeadToHeadPlayer(Color.BLUE, "CITY_FOCUS"),
        HeadToHeadPlayer(Color.WHITE, "PROBABILITY"),
        HeadToHeadPlayer(Color.ORANGE, "SETTLEMENT_FOCUS"),
    ]
    
    probability_wins = 0
    city_wins = 0
    settlement_wins = 0
    gemini_wins = 0
    
    game_idx = 0
    while game_idx < total_games:
        # Shuffling elements directly alters player.color alignments dynamically 
        random.shuffle(players)
        
        # Changing the third parameter's flag tells catanatron to print game status tables to standard output
        batch_results = play_batch(
            1, 
            players, 
            OutputOptions(None, None, False, False, False), 
            GameConfigOptions(7, 10, "BASE"), 
            False 
        )
        
        if not batch_results or not batch_results[0]:
            print(f"[Warning] Game {game_idx + 1} was aborted by the engine. Re-running this game match...")
            time.sleep(2.0)
            continue
            
        # winning_color = batch_results[0][0]
        # winning_player = next(p for p in players if p.color == winning_color)
        
        # if isinstance(winning_player, GeminiStrategyPlayer):
        #     gemini_wins += 1
        # elif winning_player.strategy_name == "PROBABILITY":
        #     probability_wins += 1
        # elif winning_player.strategy_name == "CITY_FOCUS":
        #     city_wins += 1
        # elif winning_player.strategy_name == "SETTLEMENT_FOCUS":
        #     settlement_wins += 1
            
        game_idx += 1
        
    #     if game_idx < total_games:
    #         print("Pausing to respect the Gemini rate limits...")
    #         time.sleep(1.5)
            
    # probability_win_rate = (probability_wins / total_games) * 100
    # city_win_rate        = (city_wins / total_games) * 100
    # settlement_win_rate  = (settlement_wins / total_games) * 100
    # gemini_win_rate      = (gemini_wins / total_games) * 100
    
    # print(f"\n===== ISOLATED WIN RATES BY STRATEGY (SHUFFLED) =====")
    # print(f"Probability Player Win Rate : {probability_win_rate:.2f}% ({probability_wins}/{total_games} wins)")
    # print(f"City Focus Player Win Rate  : {city_win_rate:.2f}% ({city_wins}/{total_games} wins)")
    # print(f"Settlement Player Win Rate  : {settlement_win_rate:.2f}% ({settlement_wins}/{total_games} wins)")
    # print(f"Gemini LLM Player Win Rate  : {gemini_win_rate:.2f}% ({gemini_wins}/{total_games} wins)")

if __name__ == "__main__":
    if not os.environ.get("GEMINI_API_KEY"):
        print("Please set your GEMINI_API_KEY environment variable before running.")
    else:
        run_llm_vs_heuristics()