import gym
from gym import spaces
import numpy as np
import pygame
from collections import deque
import time
import projectGame2
from item import Key, Explosive

INTERACTION_DISTANCE = 40
SCALING_FACTOR = 1.2

def path_distance(start_pos, goal_pos, tmx_data, max_steps=300):
    tile_width = int(tmx_data.tilewidth)
    tile_height = int(tmx_data.tileheight)

    start_tile = (int(start_pos[0] // tile_width), int(start_pos[1] // tile_height))
    goal_tile = (int(goal_pos[0] // tile_width), int(goal_pos[1] // tile_height))

    visited = set()
    queue = deque([(start_tile, 0)])

    def is_walkable(tx, ty):
        if tx < 0 or ty < 0 or tx >= tmx_data.width or ty >= tmx_data.height:
            return False
        gid = tmx_data.get_tile_gid(tx, ty, 0)
        return gid != 0

    while queue:
        (x, y), steps = queue.popleft()
        if (x, y) == goal_tile:
            return steps  # shortest walkable path length
        if steps > max_steps:
            return float("inf")  # unreachable within limit

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if is_walkable(nx, ny) and (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append(((nx, ny), steps + 1))

    return float("inf")



class ProjectGameEnv(gym.Env):
    def __init__(self):
        super(ProjectGameEnv, self).__init__()
        self.action_space = spaces.Discrete(10)  # 0-3 move, 4=pickup, 5=interact, 6-9=select item 0-3
        self.observation_space = spaces.Box(low=0, high=1, shape=(7,), dtype=np.float32)
        self.selected_item = None
        self.steps = 0
        self.visited_tiles = set()  # Track unique tiles visited
        self.proximity_seen = set()
        self.episode_start_time = None
        self.episode_distance = 0
        self.prev_tile = None
        self.all_episode_logs = []  # stores every episode's data
        self.memorized_win = False
        self.success_path = []
        self.last_success_goal_dist = None


        
        # Initial game object setup
        projectGame2.init_game_objects()
        self._load_game_objects()
        self.tmx_data   = projectGame2.tmx_data
        self.tilewidth  = int(self.tmx_data.tilewidth  * SCALING_FACTOR)
        self.tileheight = int(self.tmx_data.tileheight * SCALING_FACTOR)
        self.reset()
        
        self.known_key_locs = {}
        self.known_explosive_locs = {}
        self.known_door_locs = {}
        self.known_rock_locs = {}
        self.learned_object_memory = False
        
        self.visited_explosive = False
        self.visited_key = False
        self.visited_rock = False
        self.visited_door = False
        self.last_rock_dist = None





    def _load_game_objects(self):
        self.player, self.player_data, self.items, self.doors, self.rocks, self.coins, self.all_sprites = projectGame2.get_game_objects()
    

    def reset(self):
        projectGame2.init_game_objects()
        self._load_game_objects()

        # clear all per-episode logs & timers
        self.player_data = []          
        self.visited_tiles = set()
        self.proximity_seen = set()
        self.selected_item = None
        self.steps = 0
        self.episode_distance = 0
        self.episode_start_time = time.time()
        self.last_key_dist = None
        self.last_door_dist = None
        self.last_explosive_dist = None
        self.player_data = []  # clear episode log
        self.last_success_goal_dist = None

        self.rewarded_rock = False
        self.rewarded_key = False
        self.rewarded_door = False
        self.last_potential = None
        self.last_door_path = None
        self.last_rock_path = None
        self.last_rock_dist = None


        
        if self.memorized_win:
            self.hard_targets = deque(filter(None, [
                self.known_explosive_locs.get("red"),
                self.known_rock_locs.get("red"),
                self.known_key_locs.get("blue"),
                self.known_door_locs.get("blue"),
            ]))
        else:
            self.hard_targets = deque()


        explosives = [i for i in self.items if isinstance(i, Explosive)]
        print(f"[Reset #{self.steps}] Explosives on map: {len(explosives)}")
        return self._get_obs()

    
    def step(self, action):
        reward = 0.0
        done = False
        info = {}
        
        if self.steps == 0:
            self.did_meaningful_action = False


        # 1) Movement or selection or interaction
        if action in [0, 1, 2, 3]:
            self.player.update_rl(
                action,
                self.tileheight,
                self.tilewidth,
                self.tmx_data,
                self.player_data,
                self.rocks
            )
        elif action == 4:
            # PICKUP
            collected = pygame.sprite.spritecollide(self.player, self.items, True)
            for item in collected:
                self.player.pick_up(item)
                self.player_data.append({
                    "event": "collect_item",
                    "item": (item.name, item.color),
                    "position": self.player.rect.topleft,
                    "step": self.steps
                })
                
                if isinstance(item, Key) or isinstance(item, Explosive):
                    self.did_meaningful_action = True

                # base rewards
                if isinstance(item, Explosive):
                    self.known_explosive_locs = {e.color: e.rect.center for e in self.items if isinstance(e, Explosive)}
                    reward += 2.0
                    for rock in self.rocks:
                        if rock.color == item.color:
                            dist = path_distance(self.player.rect.center, rock.rect.center, self.tmx_data, 300)
                            if dist < float("inf") and dist <= 10:
                                reward += 1.0
                                self.player_data.append({
                                    "event": "smart_explosive_pickup",
                                    "item_color": item.color,
                                    "matched_rock": True,
                                    "step": self.steps
                                })
                                break
                elif isinstance(item, Key):
                    self.known_key_locs = {k.color: k.rect.center for k in self.items if isinstance(k, Key)}
                    reward += 2.0
                    if self.rewarded_rock:
                        for door in self.doors:
                            if door.color == item.color:
                                dist = path_distance(self.player.rect.center, door.rect.center, self.tmx_data, 300)
                                if dist < float("inf") and dist <= 5:
                                    reward += 0.5
                                    self.player_data.append({
                                        "event": "smart_key_pickup",
                                        "item_color": item.color,
                                        "matched_door": True,
                                        "step": self.steps
                                    })
                                    break

        elif action == 5:
            # INTERACT
            near_block = False
            # auto-select if none chosen
            if not self.selected_item:
                for rock in self.rocks:
                    if self.player.rect.colliderect(rock.rect.inflate(INTERACTION_DISTANCE, INTERACTION_DISTANCE)):
                        for i in self.player.inventory:
                            if isinstance(i, Explosive) and i.color == rock.color:
                                self.selected_item = i
                                break
                for door in self.doors:
                    if self.player.rect.colliderect(door.rect.inflate(INTERACTION_DISTANCE, INTERACTION_DISTANCE)):
                        for i in self.player.inventory:
                            if isinstance(i, Key) and i.color == door.color:
                                self.selected_item = i
                                break

            # 🚨 Only one call to _interact()
            interacted = self._interact()
            if interacted:
                self.did_meaningful_action = True
                print(f"[STEP {self.steps}] ✅ Successful interaction using: {self.last_used}")
                reward += 2.0
                self.player_data.append({
                    "event": "successful_interaction",
                    "type": self.last_used,
                    "step": self.steps
                })

                # 🎯 Subtask rewards
                if self.last_used == "explosive" and not hasattr(self, "rewarded_rock"):
                    reward += 10.0
                    self.rewarded_rock = True
                    self.player_data.append({
                        "event": "subtask_complete",
                        "subtask": "rock_destroyed",
                        "step": self.steps
                    })

                elif self.last_used == "key" and not hasattr(self, "rewarded_door"):
                    reward += 15.0
                    self.rewarded_door = True
                    self.player_data.append({
                        "event": "subtask_complete",
                        "subtask": "door_unlocked",
                        "step": self.steps
                    })

            else:
                # Failed interaction penalties
                near_block = any(
                    self.player.rect.colliderect(obj.rect.inflate(INTERACTION_DISTANCE, INTERACTION_DISTANCE))
                    for obj in list(self.rocks) + list(self.doors)
                )
                if near_block and self.selected_item:
                    reward -= 1.0
                else:
                    reward -= 0.3
            
        elif action in [6, 7, 8, 9]:
            # SELECT ITEM
            idx = action - 6
            if idx < len(self.player.inventory):
                self.selected_item = self.player.inventory[idx]
                self.player_data.append({
                    "event": "select_item",
                    "index": idx,
                    "item": (self.selected_item.name, self.selected_item.color),
                    "step": self.steps
                })
                reward += 0.3
                # hint shaping: is selected‐item usable soon?
                matched = False
                if isinstance(self.selected_item, Explosive):
                    for rock in self.rocks:
                        if rock.color == self.selected_item.color:
                            dist = path_distance(self.player.rect.center, rock.rect.center, self.tmx_data, 300)
                            if dist < float("inf") and dist <= 10:
                                matched = True
                                break
                else:  # Key
                    for door in self.doors:
                        if door.color == self.selected_item.color:
                            dist = path_distance(self.player.rect.center, door.rect.center, self.tmx_data, 300)
                            if dist < float("inf") and dist <= 10:
                                matched = True
                                break

                if matched:
                    reward += 1.0
                    self.player_data.append({
                        "event": "hint_shaping_reward",
                        "item": (self.selected_item.name, self.selected_item.color),
                        "step": self.steps
                    })


        # 2) Step‐counters & exploration bonus
        self.steps += 1
        tx = self.player.rect.x // self.tilewidth
        ty = self.player.rect.y // self.tileheight
        tile = (tx, ty)
        if self.prev_tile and tile != self.prev_tile:
            self.episode_distance += 1
        self.prev_tile = tile

        if tile not in self.visited_tiles:
            self.visited_tiles.add(tile)
            reward += 0.2
        else:
            reward -= 0.05


        # 3) Adaptive reward shaping: pick correct target and re-prioritize after each pickup

        d_exp = min(
            (path_distance(self.player.rect.center, e.rect.center, self.tmx_data, 300)
            for e in self.items if isinstance(e, Explosive)),
            default=float('inf')
        )
        d_key = min(
            (path_distance(self.player.rect.center, k.rect.center, self.tmx_data, 300)
            for k in self.items if isinstance(k, Key)),
            default=float('inf')
        )
        d_door = min(
            (path_distance(self.player.rect.center, d.rect.center, self.tmx_data, 300)
            for d in self.doors if d.color == "blue"),
            default=float('inf')
        )
        

        has_key = any(isinstance(i, Key) for i in self.player.inventory)
        has_explosive = any(isinstance(i, Explosive) for i in self.player.inventory)

        # -------------------
        # Phase 1: No items held
        # -------------------
        if not has_key and not has_explosive:
            if d_exp + 2 < d_key:
                if self.last_explosive_dist is not None and d_exp < self.last_explosive_dist:
                    reward += 2.0
                    # print(f"[Shaping] Seeking Explosive (d_exp={d_exp:.1f})")
                if d_key < float("inf"):
                    reward -= 0.05
                if d_door < float("inf"):
                    reward -= 0.05
            elif d_key + 2 < d_exp:
                if self.last_key_dist is not None and d_key < self.last_key_dist:
                    reward += 2.0
                    # print(f"[Shaping] Seeking Key (d_key={d_key:.1f})")
                if d_exp < float("inf"):
                    reward -= 0.05
                if d_door < float("inf"):
                    reward -= 0.05

        # -------------------
        # Phase 2: Picked up one item
        # -------------------
        elif has_explosive and not has_key:
            rock = next((r for r in self.rocks if r.color == "red"), None)
            key_obj = next((k for k in self.items if isinstance(k, Key)), None)
            if key_obj:
                d_key = path_distance(self.player.rect.center, key_obj.rect.center, self.tmx_data, 300)
            else:
                d_key = float('inf')

            if rock:
                d_rock = path_distance(self.player.rect.center, rock.rect.center, self.tmx_data, 300) if rock else float('inf')
                if d_rock + 2 < d_key:  # rock is closer than key
                    if self.last_rock_dist is not None and d_rock < self.last_rock_dist:
                        reward += 2.0
                        # print(f"[Shaping] Go to rock first (has explosive)")
                    self.last_rock_dist = d_rock
                else:
                    if self.last_key_dist is not None and d_key < self.last_key_dist:
                        reward += 2.0
                        # print(f"[Shaping] Skip rock, go to key")

        elif has_key and not has_explosive:
            # Is the door reachable without explosive?
            door = next((d for d in self.doors if d.color == "blue"), None)
            rock_exists = any(r.color == "red" for r in self.rocks)

            if door:
                door_path = path_distance(self.player.rect.center, door.rect.center, self.tmx_data, 300)
                door_reachable = door_path < float("inf")

                if rock_exists and not door_reachable:
                    # Rock blocking door, must go get explosive
                    if self.last_explosive_dist is not None and d_exp < self.last_explosive_dist:
                        reward += 3.0
                        # print(f"[Shaping] Rock blocking door — go to explosive (has key)")
                else:
                    # Rock gone or door is reachable
                    if self.last_door_dist is not None and d_door < self.last_door_dist:
                        reward += 2.0
                        # print(f"[Shaping] Rock gone or bypassed — go to door (has key)")


        # -------------------
        # Phase 3: Has both → go to door
        # -------------------
        # -------------------
# Phase 3: Has both → go to rock (if needed) then door
# -------------------
        elif has_key and has_explosive:
            rock = next((r for r in self.rocks if r.color == "red"), None)

            if rock:
                d_rock = path_distance(self.player.rect.center, rock.rect.center, self.tmx_data, 300)
                if self.last_rock_dist is not None and d_rock < self.last_rock_dist:
                    reward += 9.0
                    # print(f"[Shaping] Go to rock before door (has key + explosive)")
                self.last_rock_dist = d_rock
            else:
                # rock is gone, go to door
                if self.last_door_dist is not None and d_door < self.last_door_dist:
                    reward += 10.0
                    # print(f"[Shaping] Final Target: Door (d_door={d_door:.1f})")


        # -------------------
        # Save distances for next comparison
        # -------------------
        self.last_explosive_dist = d_exp
        self.last_key_dist = d_key
        self.last_door_dist = d_door




        # 4) Proximity bonuses
        for exp in (i for i in self.items if isinstance(i, Explosive)):
            if self.player.rect.colliderect(exp.rect.inflate(INTERACTION_DISTANCE* 2, INTERACTION_DISTANCE* 2)):
                reward += 0.5
                break
        else:
            for key in (i for i in self.items if isinstance(i, Key)):
                if self.player.rect.colliderect(key.rect.inflate(INTERACTION_DISTANCE* 2, INTERACTION_DISTANCE* 2)):
                    reward += 0.5
                    break
            else:
                for door in self.doors:
                    if self.player.rect.colliderect(door.rect.inflate(INTERACTION_DISTANCE, INTERACTION_DISTANCE)):
                        reward += 0.50
                        break

        # 5) Goal discovery bonus
        for door in self.doors:
            if door.color == "blue" and \
               self.player.rect.colliderect(door.rect.inflate(INTERACTION_DISTANCE * 5, INTERACTION_DISTANCE * 5)) and \
               id(door) not in self.proximity_seen:
                reward += 0.5
                self.proximity_seen.add(id(door))
                self.known_door_locs = {d.color: d.rect.center for d in self.doors}
                break
            
    
        # 8) tiny penalty if deviating > 3 tiles from the current hard target
        if self.hard_targets and self.memorized_win:
            dx = path_distance(self.player.rect.center, self.hard_targets[0], self.tmx_data, 300)
            if dx < float('inf'):
                reward -= 0.01 * dx
                if dx < 2:  # if 3 tiles away
                    reward += 6.0
                    self.player_data.append({
                        "event": "reached_hard_target",
                        "target_index": len(self.hard_targets),
                        "step": self.steps,
                        "position": self.player.rect.topleft
                    })
                    self.hard_targets.popleft()

           
        # 9) Check win/lose
        game_reward, done = self._check_game_status()
        reward += game_reward

        # force‐end
        if self.steps >= 20000:
            done = True

        # small time penalty
        reward -= 0.03

        # 7) If episode finished, compute and stash metrics in info
        if done:
            # build full episode record
            episode_time = time.time() - self.episode_start_time
            won = any(e.get("event") == "game_won" for e in self.player_data)
            
            if won and not self.memorized_win:
                max_steps = 20000  # e.g. 30000
                efficiency_bonus = 10 * (max_steps - self.steps) / max_steps
                reward += efficiency_bonus
                if not self.learned_object_memory and not self.memorized_win:
                    self.known_key_locs = {key.color: key.rect.center for key in self.items if isinstance(key, Key)}
                    self.known_explosive_locs = {e.color: e.rect.center for e in self.items if isinstance(e, Explosive)}
                    self.known_door_locs = {d.color: d.rect.center for d in self.doors}
                    self.known_rock_locs = {r.color: r.rect.center for r in self.rocks}
                    self.learned_object_memory = True
                    self.player_data.append({
                        "event": "learned_map_memory",
                        "step": self.steps,
                        "key_locs": self.known_key_locs,
                        "explosive_locs": self.known_explosive_locs,
                        "door_locs": self.known_door_locs,
                        "rock_locs": self.known_rock_locs
                    })
                    
                self.memorized_win = True
                    




            episode_log = {
                "episode_summary": {
                    "steps": self.steps,
                    "distance_moved": self.episode_distance,
                    "duration_seconds": round(episode_time, 3),
                    "game_won": won
                },
                "events": list(self.player_data)  # every movement, pickup, select, etc.
            }

            self.all_episode_logs.append(episode_log)
            print("🏁 Episode complete:", episode_log["episode_summary"])
            
            # ⛔ Cancel reward if agent never did anything useful
            if done and not self.did_meaningful_action:
                self.player_data.append({
                    "event": "invalidated_episode",
                    "reason": "no_pickup_or_interact",
                    "final_reward": reward
                })
                reward -= 5.0 
            # if won:    
            #     self.success_path = [
            #             self.known_explosive_locs,
            #             self.known_rock_locs,
            #             self.known_key_locs,
            #             self.known_door_locs
            #         ]    
            # if self.success_path:
            #     next_goal = self.success_path[0]
            #     d = path_distance(self.player.rect.center, next_goal, self.tmx_data, 300)
            #     if self.last_success_goal_dist is not None and d < self.last_success_goal_dist:
            #         reward += 1.0
            #     if d < 2:
            #         reward += 10.0
            #         self.success_path.pop(0)
            #     self.last_success_goal_dist = d



        # final observation
        reward = np.clip(reward, -1000, 2000)
        obs = self._get_obs()
        return obs, reward, done, info





    def _get_obs(self):
        x, y = self.player.rect.center
        tile_x = int(x // 50)
        tile_y = int(y // 50)
        key_count = len([i for i in self.player.inventory if isinstance(i, Key)])
        exp_count = len([i for i in self.player.inventory if isinstance(i, Explosive)])
        selected_idx = -1
        if self.selected_item and self.selected_item in self.player.inventory:
            selected_idx = self.player.inventory.index(self.selected_item)
        
        is_near = 0
        for sprite in list(self.items) + list(self.doors) + list(self.rocks):
            if self.player.rect.colliderect(sprite.rect.inflate(INTERACTION_DISTANCE, INTERACTION_DISTANCE)):
                is_near = 1
                break

        return np.array([
            tile_x / 30,
            tile_y / 30,
            key_count / 5,
            exp_count / 5,
            selected_idx / 4,
            self.steps / 300,
            is_near 
        ], dtype=np.float32)


    def _interact(self):
        if not self.selected_item:
            return False
        # else:
        #     print(f"Selected item: {self.selected_item}")

        for door in self.doors:
            if self.player.rect.colliderect(door.rect.inflate(INTERACTION_DISTANCE, INTERACTION_DISTANCE)):
                if isinstance(self.selected_item, Key) and self.selected_item.color == door.color:
                    door.interact(self.player, self.selected_item)
                    if self.selected_item in self.player.inventory:
                        self.player.inventory.remove(self.selected_item)

                    self.player_data.append({
                        "event": "interact",
                        "type": "door",
                        "color": door.color,
                        "item": (self.selected_item.name, self.selected_item.color),
                        "position": self.player.rect.topleft
                    })

                    if door.color == "blue":
                        self.player_data.append({
                            "event": "game_won",
                            "steps_taken": self.steps,
                            "duration_seconds": round(time.time() - self.episode_start_time, 3),
                        })
                        

                    self.selected_item = None
                    self.last_used = "key"  # 🔑 Mark usage
                    return True
                
                else:
                    # Wrong item on door
                    self.player_data.append({
                        "event": "failed_interaction",
                        "reason": "wrong_item_on_door",
                        "door_color": door.color,
                        "item": (self.selected_item.name, self.selected_item.color),
                        "position": self.player.rect.topleft,
                        "step": self.steps
                    })
                    return False  # immediately exit after wrong use on valid object
                        

        for rock in self.rocks:
            if self.player.rect.colliderect(rock.rect.inflate(INTERACTION_DISTANCE, INTERACTION_DISTANCE)):
                if isinstance(self.selected_item, Explosive) and self.selected_item.color == rock.color:
                    rock.interact(self.player, self.selected_item)
                    if self.selected_item in self.player.inventory:
                        self.player.inventory.remove(self.selected_item)

                    self.player_data.append({
                        "event": "interact",
                        "type": "rock",
                        "color": rock.color,
                        "item": (self.selected_item.name, self.selected_item.color),
                        "position": self.player.rect.topleft
                    })

                    self.selected_item = None
                    self.last_used = "explosive"  # 💥 Mark for reward boost
                    return True
                else:
                    # Wrong item on rock
                    self.player_data.append({
                        "event": "failed_interaction",
                        "reason": "wrong_item_on_rock",
                        "rock_color": rock.color,
                        "item": (self.selected_item.name, self.selected_item.color),
                        "position": self.player.rect.topleft,
                        "step": self.steps
                    })
                    return False
        
        # None matched → log failed attempt
        # if self.selected_item:
        #     self.player_data.append({
        #         "event": "failed_interaction",
        #         "item": (self.selected_item.name, self.selected_item.color),
        #         "position": self.player.rect.topleft,
        #         "step": self.steps
        #     })

        return False


    def _check_game_status(self):
        for event in self.player_data:
            if event.get("event") == "game_won":
                return 500.0, True
        return 0.0, False

    def render(self, mode="human"):
        # if mode != "human":
        #     return

        # # Clear screen
        # projectGame2.screen.fill(projectGame2.WHITE)

        # # Redraw the map
        # for layer in projectGame2.tmx_data.visible_layers:
        #     for x, y, gid in layer:
        #         tile = projectGame2.tmx_data.get_tile_image_by_gid(gid)
        #         if tile:
        #             scaled_tile = pygame.transform.scale(tile, (
        #                 int(projectGame2.tmx_data.tilewidth * projectGame2.SCALING_FACTOR),
        #                 int(projectGame2.tmx_data.tileheight * projectGame2.SCALING_FACTOR)
        #             ))
        #             projectGame2.screen.blit(scaled_tile, (
        #                 x * projectGame2.tmx_data.tilewidth * projectGame2.SCALING_FACTOR,
        #                 y * projectGame2.tmx_data.tileheight * projectGame2.SCALING_FACTOR
        #             ))

        # # Draw sprites
        # for sprite in self.all_sprites:
        #     projectGame2.screen.blit(sprite.image, sprite.rect)

        # # Update display
        # pygame.display.flip()
        # projectGame2.clock.tick(30)
        pass

