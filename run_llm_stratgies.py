import os
import json
from collections import Counter
import time
# Core Catanatron imports
from catanatron import Color, RandomPlayer, ActionType, Player
from catanatron.models.enums import ActionPrompt
from catanatron.cli.play import play_batch, GameConfigOptions, OutputOptions
from catanatron.players.weighted_random import WeightedRandomPlayer

# Modern Google GenAI SDK import
try:
    from google import genai
    from google.genai import types
    
    # Initializes using os.environ.get("GEMINI_API_KEY") automatically
    client = genai.Client() 
except ImportError:
    client = None

class GeminiStrategyPlayer(Player):
    def __init__(self, color, model_name="gemini-2.5-pro"):
        super().__init__(color)
        self.model_name = model_name
        # Fallback to standard optimized bot for mid-game turns
        self.base_simulator_bot = WeightedRandomPlayer(color)

    def decide(self, game, playable_actions):
        # 1. STRATEGIC SETUP INTERCEPTION: Let Gemini choose the initial placement
        if game.state.current_prompt == ActionPrompt.BUILD_INITIAL_SETTLEMENT:
            settle_actions = [a for a in playable_actions if a.action_type == ActionType.BUILD_SETTLEMENT]
            if settle_actions:
                if client is None:
                    print("[Warning] google-genai library not installed. Falling back to random choice.")
                    return settle_actions[0]
                return self.decide_via_gemini(game, settle_actions)

        # 2. FAST CLI SIMULATION RESUMPTION: Pass back to memory-resident baseline loops
        return self.base_simulator_bot.decide(game, playable_actions)

    def decide_via_gemini(self, game, settle_actions):
        """Serializes board choices into structured JSON and passes it to Gemini."""
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

         # "Focus on high-yield probability (total_pips) and powerful resource synergies (like Ore/Wheat/Sheep for cities or Wood/Brick for roads). "
        system_instruction = (
            "You are a competitive Settlers of Catan AI assistant specializing in board-state evaluation. "
            "Your task is to analyze the available initial settlement nodes and select the absolute best one. "
            "Focus on maximizing powerful resource synergies like Brick and Wood for roads and settlements."
            "You MUST respond ONLY with a valid JSON object matching this schema: {\"chosen_index\": <integer>}"
        )

        user_prompt = f"Available Settlement Nodes:\n{json.dumps(options_data, indent=2)}\n\nWhich option index do you choose?"

        try:
            # Structuring the call using the modern SDK layout
            response = client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    # Forces Gemini to reply strictly with clean, parsable JSON
                    response_mime_type="application/json", 
                    temperature=0.1
                ),
            )
            
            # Safely extract and parse index text
            result = json.loads(response.text)
            chosen_idx = int(result.get("chosen_index", 0))
            
            # Boundary security evaluation
            if 0 <= chosen_idx < len(settle_actions):
                print(f"[Gemini Action] Selected node index {chosen_idx} matching {options_data[chosen_idx]['total_pips']} pips.")
                return settle_actions[chosen_idx]
                
        except Exception as e:
            print(f"[Gemini Error] API call or parsing failed ({e}). Falling back.")
        
        # Safe default index fallback in case of connection dropouts
        return settle_actions[0]

def run_gemini_simulation():
    total_games = 20
    print(f"\n--- Running Gemini-Guided Setup vs 3 Smart Bots ({total_games} games) ---")
    
    players = [
        GeminiStrategyPlayer(Color.RED, model_name="gemini-2.5-pro"),
        WeightedRandomPlayer(Color.BLUE),
        WeightedRandomPlayer(Color.WHITE),
        WeightedRandomPlayer(Color.ORANGE),
    ]
    
    winners_list = []
    
    # 2. Loop through the games individually to create the time gaps
    for game_idx in range(total_games):
        print(f"Starting Game {game_idx + 1}/{total_games}...")
        
        # We run play_batch with num_games=1 so it executes exactly ONE game
        batch_results = play_batch(
            1, 
            players, 
            OutputOptions(None, None, False, False, False), 
            GameConfigOptions(7, 10, "BASE"), 
            False # Changing this to False ensures wins are tracked cleanly by Color, preventing KeyErrors
        )
        
        # Save the winner of this individual game
        winners_list.extend(batch_results[0])
        
        # 3. WHERE IT MAKES SURE TO SLEEP:
        # This pauses execution for 1.5 seconds right after the game finishes.
        # This clears your Requests Per Minute (RPM) window perfectly!
        if game_idx < total_games - 1:
            print("Pausing to respect the Gemini Free Tier rate limits...")
            time.sleep(1.5)
            
    # Count the total accumulated winners across all sequential runs
    win_counts = Counter(winners_list)
    
    print(f"\n===== SIMULATION RESULTS =====")
    for color in [Color.RED, Color.BLUE, Color.WHITE, Color.ORANGE]:
        count = win_counts.get(color, 0)
        percentage = (count / total_games) * 100
        player_type = "Gemini Strategy" if color == Color.RED else "WeightedRandom Bot"
        print(f"  {color.name} ({player_type}): {percentage:.2f}% ({count} wins)")

if __name__ == "__main__":
    if not os.environ.get("GEMINI_API_KEY"):
        print("Please set your GEMINI_API_KEY environment variable before running.")
    else:
        run_gemini_simulation()