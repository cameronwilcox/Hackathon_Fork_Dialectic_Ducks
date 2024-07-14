# DO NOT EDIT -->
from pathlib    import Path
from typing     import Tuple

import math

THIS_FOLDER = Path(__file__).resolve().parent
TWR_POS = []
with open(THIS_FOLDER / 'twr.csv', 'r') as twr_h:
    for ln in twr_h:
        ln_parts = ln.strip().split(',') + [None]
        for idx in range(1, 3): ln_parts[idx] = int(ln_parts[idx])
        TWR_POS += [tuple(ln_parts + [None])]
    #End-for
#End-with
# <-- DO NOT EDIT


min_range = 999
max_range = -999
from pygame.math import Vector2
def twr_func(coord, tag : str, LoT : list, fire : bool, current_dir : float, target_dir : float) -> Tuple[float, bool, bool]:
    '''
    Add in your turret logic here

    Notes:
    - "2D-Vector" == pygame.math.Vector2d using pixels
    - angle == float in degrees

    PARAMETERS
    ----------
    coord : 2D-Vector
        Location of the subject tower relative to the home base

    tag : str
        An identifier defined by you

    LoT : list
        "List of Targets", each entry in this list has the following structure
        - Target Type : str
        - Target Position : 2D-Vector
        - Target Velocity : 2D-Vector

    fire : bool
        Indicates whether or not the next round will be fired when chambered

    current_dir : angle
        Current bearing of the gun

    target_dir : angle
        Target bearing of the gun

    RETURNS
    -------
    target_dir
        As defined in `PARAMETERS`

    fire
        As defined in `PARAMETERS`

    target_dir_is_radians : bool
        Indicates if the output target_dir is in radians

    '''
    # Wait to start shooting until an enemy spawns (if 1 turret)
    if len(LoT) > 2:
        priority_target = LoT[2]
        if tag == '3001':
            for entity in LoT:
                if entity[0] == 'Beast Rider':
                    priority_target = entity
                    break
                elif len(LoT) > 3:
                    priority_target = LoT[3]

    else:
        return (90, False, False)

    # Target variables
    # target_type = priority_target[0]
    target_pos = Vector2(priority_target[1][0], priority_target[1][1])
    # target_vel = Vector2(priority_target[2][0], priority_target[2][1])

    # Turret variables
    turret_pos = Vector2(coord[0], coord[1])
    # bullet_speed = 45 # Hard coded from Howard Walowitz Turret
    # rot_speed = 55
    target_range = (((target_pos[0] - turret_pos[0]) ** 2) + ((target_pos[1] - turret_pos[1]) **2)) ** .5
    # target_range = Vector2((target_pos.x - turret_pos.x), (target_pos.y - turret_pos.y))
    # 0 - 4
    k = 0
    if tag == "3001":
        k = 0.07 # Original
    elif tag == "3000":
        k = .22 + target_range/315
    # Add Bullet speed to calculation
    # k = .30 + target_range/275
    # print(f"k:{k}")
    # Needs: target_range, target_vel, bullet_speed, rot_speed

    # a = Vector2.dot(target_vel, target_vel) - bullet_speed**2
    # b = 2 * Vector2.dot(target_vel, target_range)
    # c = Vector2.dot(target_range, target_range)

    # disc = b*b - 4*a*c

    # deltaTime = 0

    # if(disc > 0):
    #     deltaTime = 2 * c / ((disc * 0.5) - b)
    # else:
    #     deltaTime = -1

    # aim_point = Vector2(target_pos - target_vel * deltaTime)
    # delta_x = turret_pos.x - aim_point.x #(target_pos.x + k*(target_vel.x))#aim_point.x # (target_pos.x + k*(target_vel.x))
    # delta_y = turret_pos.y - aim_point.y #(target_pos.y + k*(target_vel.y))#aim_point.y # (target_pos.y + k*(target_vel.y))
    delta_x = turret_pos.x - (target_pos.x + k*(priority_target[2][0]))
    delta_y = turret_pos.y - (target_pos.y + k*(priority_target[2][1]))

    if delta_x > 0:
        angle = math.degrees(math.atan(delta_y/delta_x)) + 180
    elif delta_x == 0 and delta_y > 0:
        return (90, True, False)
    elif delta_x == 0 and delta_y < 0:
        return (-90, True, False)
    else:
        angle = math.degrees(math.atan(delta_y/delta_x))

    return (angle, True, False)
#End-def