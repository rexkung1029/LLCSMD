import discord
import json
import os
import random
import math

from discord import app_commands
from discord.ext import commands

with open("setting.json","r",encoding="utf8") as s:
    j_setting = json.load(s)

active_games = {}


def json_write(path:str, file):
    try:
        with open(path,'w',encoding='utf8') as tmp:
            json.dump(file, tmp, indent=4, ensure_ascii=False)
    except Exception as e:
        print(e,", json_w")

    

class TwoAOneB(commands.Cog):
    def __init__(self, bot:commands.Bot):
        try:
            self.bot = bot
            self.active_games = active_games
        except Exception as e:
            print(e,"2a1b init")

    @app_commands.command(name="1a2b")
    async def start_game(self, interaction: discord.Interaction, length: int = 4):
        try:
            # Check for invalid length
            if length < 3:
                await interaction.response.send_message("遊戲長度必須至少為 3 位數。")
                return

            # Check if a game is already running for this user
            user_id = interaction.user.id
            if user_id in self.active_games:
                await interaction.response.send_message("您已經開始了一個遊戲。請先完成或取消現有遊戲。")
                return

            # Generate the target number
            target_number = str(self.generate_answer(length))
            print(target_number)
            # Initialize the game instance with relevant data
            game_instance = {
                "type": "1A2B",
                "attempts_left": 10,
                "answer": target_number,
                "guesses": [],  # List to store player guesses
                "guess_results": [],  # List to store feedback for each guess
                "length": length,
            }

            # Store the game instance in active_games
            self.active_games[user_id] = game_instance

            # Send a message acknowledging game selection and provide initial instructions
            await interaction.response.send_message(f"我生成了一個 {length} 位數 (沒有重複數字)。猜猜這個數字吧！")
        except Exception as e:
            print(e,",2a1b")


    @app_commands.command()
    async def guess(self, interaction: discord.Interaction, guess: str):
        try:
            # Check if a game is active for this user
            user_id = interaction.user.id

            if user_id not in self.active_games:
                await interaction.response.send_message("您尚未開始遊戲。請先用 `/1a2b` 開始遊戲。")
                return

            # Retrieve the game instance
            game_instance = self.active_games[user_id]
            length = game_instance["length"]

            # Validate guess format and number of digits
            if not guess.isdigit() or len(guess) != length:
                await interaction.response.send_message(f"無效的猜測。請輸入一個 {length} 位數。")
                return

            # Process the guess and get feedback
            a, b = self.check_guess(guess=guess, user_id=interaction.user.id)
            feedback = f"{a}A{b}B"

            # Update game data
            game_instance["guesses"].append(guess)
            game_instance["guess_results"].append(feedback)
            game_instance["attempts_left"] -= 1

            # Send feedback to the player
            await interaction.response.send_message(feedback)

            # Check for win or loss conditions
            if a == game_instance["length"] and b == 0:
                await interaction.channel.send("恭喜！你猜對了數字！")
                del self.active_games[user_id]  # Remove game from active games
    
            elif game_instance["attempts_left"] == 0:
                await interaction.channel.send("嘗試超過 10 次，遊戲結束。正確答案是: " + game_instance["answer"])
                del self.active_games[user_id]  # Remove game from active games

        except Exception as e:
            print(e, ", guess")

    @app_commands.command(name="1a2b_ans")
    async def _1a2b_ans(self, interaction: discord.Interaction):
        answer = self.active_games[interaction.user.id]["answer"]
        await interaction.response.send_message(f"答案是:{answer}")
        del self.active_games[interaction.user.id]

    @app_commands.command()
    async def end_game(self, interaction: discord.Interaction):
        del self.active_games[interaction.user.id]

    def check_guess(self, guess: str,user_id: int) -> tuple[int, int]:
        a, b = 0, 0
        game_instance = self.active_games[user_id]
        for i in range(game_instance["length"]):
            answer = game_instance["answer"] 
            if guess[i] == answer[i]:
                a += 1
            elif guess[i] in  answer:
                b += 1
        return a, b

    
    def generate_answer(self, length: int):
        nums = list(range(10))  # Create a list containing digits 0-9
        answer = []
        while len(answer) < length:
            n = random.choice(nums)  # Randomly select a digit from nums
            answer.append(n)
            nums.remove(n)  # Remove the selected digit from the list

        if len(set(answer)) == length:
            return "".join(str(x) for x in answer)  # Convert digits to string


async def setup(bot: commands.Bot):
    await bot.add_cog(TwoAOneB(bot))