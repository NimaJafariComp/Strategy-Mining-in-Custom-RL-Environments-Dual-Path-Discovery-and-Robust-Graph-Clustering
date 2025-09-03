from stable_baselines3 import PPO
from rl_env import ProjectGameEnv
import os
import json
import matplotlib.pyplot as plt
import pygame

env = ProjectGameEnv()

model = PPO(
    "MlpPolicy", 
    env, 
    verbose=1,
    learning_rate=3e-4,
    ent_coef=2.6,
    clip_range=0.2,
    n_steps=2048,
    device="cpu" # or "cpu" if needed
)
model.learn(total_timesteps=5_000_000)
pygame.init()

# Save model in the current script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, "ppo_project_game")
model.save(model_path)
# Save final log in the same location
import numpy as np

def convert_numpy(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj
log_path = os.path.join(script_dir, "final_run.json")
with open(log_path, "w") as f:
    json.dump(env.all_episode_logs, f, indent=2, default=convert_numpy)

    
obs = env.reset()
done = False
# while not done:
#     action, _ = model.predict(obs)
#     obs, reward, done, _ = env.step(action)
#     # env.render()
#     # pygame.time.delay(150)  # Adjust to slow down rendering
    
pygame.quit()
    

# Generate performance plots if game_won is recorded
episode_data = []
episode = 0
for entry in env.player_data:
    if entry.get("event") == "game_won":
        episode_data.append({
            "episode": episode,
            "steps_taken": entry.get("steps_taken", 0),
            "duration_seconds": entry.get("duration_seconds", 0.0)
        })
        episode += 1
if episode_data:
    episodes = [d["episode"] for d in episode_data]
    steps = [d["steps_taken"] for d in episode_data]
    times = [d["duration_seconds"] for d in episode_data]

    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.plot(episodes, steps, marker='o')
    plt.title("Steps Taken per Episode")
    plt.xlabel("Episode")
    plt.ylabel("Steps")

    plt.subplot(1, 2, 2)
    plt.plot(episodes, times, marker='o', color='green')
    plt.title("Duration per Episode")
    plt.xlabel("Episode")
    plt.ylabel("Time (seconds)")

    plt.tight_layout()
    plt_path = os.path.join(script_dir, "training_progress.png")
    plt.savefig(plt_path)
    print(f"Plot saved to: {plt_path}") 
