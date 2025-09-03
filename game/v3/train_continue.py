from stable_baselines3 import PPO
from rl_env import ProjectGameEnv
import os
import json
import numpy as np

# Load env and model
env = ProjectGameEnv()
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, "ppo_project_gamev5.zip")
model = PPO.load(model_path, env=env, device="cpu")


# Continue learning
model.learn(total_timesteps=200_000)

# Save updated model
model.save(os.path.join(script_dir, "ppo_project_gamev1"))

# Save log
def convert_numpy(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

log_path = os.path.join(script_dir, "final_run_v1.json")
with open(log_path, "w") as f:
    json.dump(env.all_episode_logs, f, indent=2, default=convert_numpy)

