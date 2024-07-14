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
from pygame.math import Vector2

SEC_PER_UPDATE = (1000/120)/1000
GAME_FT_PX = 1/4
LUCKY_NUM = 777
MAX_LEAD_MULT = 1.65
ENEMY_LIST_HEAD_INDEX = 2 # Change based on turret count
SEEK_GENERIC_ENEMY_RANGE = 100
SEEK_BEAST_RIDER_RANGE = 300

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
    # Base case: Turret idle until enemies spawn
    if len(LoT) <= ENEMY_LIST_HEAD_INDEX:
        return (90, False, False)

    # Target variables
    priority_target = LoT[ENEMY_LIST_HEAD_INDEX]
    target_pos = Vector2(priority_target[1][0], priority_target[1][1])
    target_vel = Vector2(priority_target[2][0], priority_target[2][1])
    
    # Turret variables
    turret_pos = Vector2(coord[0], coord[1])
    dist_from_target = abs(turret_pos.distance_to(target_pos))
    bullet_speed = 0
    if tag == "3001":
        bullet_speed = SEC_PER_UPDATE * 45 / GAME_FT_PX
    if tag == "3000":
        bullet_speed = SEC_PER_UPDATE * 70 / GAME_FT_PX

    # Prioritization Algorithm
    for entity in LoT[2:]:
        if tag == "3000":
            if entity[0] == "Beast Rider" and dist_from_target < SEEK_BEAST_RIDER_RANGE:
                    priority_target = entity
                    break
        if(turret_pos.distance_to(Vector2(entity[1][0], entity[1][1])) < dist_from_target and dist_from_target < SEEK_GENERIC_ENEMY_RANGE):
            if tag == "3001":
                if entity[0] != "Beast Rider":
                    priority_target = entity
        else:
            priority_target = LoT[2]
        dist_from_target = abs(turret_pos.distance_to(entity[1]))

    target_pos = Vector2(priority_target[1][0], priority_target[1][1])
    target_vel = Vector2(priority_target[2][0], priority_target[2][1])

    # Aim Algorithm
    target_range = Vector2((target_pos.x - turret_pos.x), (target_pos.y - turret_pos.y))
    deltaTime = calc_aim_delta(target_range, target_vel, bullet_speed)
    deltaTime_mult = lerp(0, MAX_LEAD_MULT, abs(target_range.magnitude()/LUCKY_NUM)) # Feeling lucky? 
    aim_point = Vector2(target_pos - target_vel * deltaTime * deltaTime_mult)

    # Aim vector
    aim = Vector2(turret_pos.x - aim_point.x, turret_pos.y - aim_point.y)

    # Angle determination
    if aim.x > 0:
        angle = math.atan(aim.y/aim.x) + math.pi
    elif aim.x == 0 and aim.y > 0:
        return (90, True, False)
    elif aim.x == 0 and aim.y < 0:
        return (-90, True, False)
    else:
        angle = math.atan(aim.y/aim.x)

    return (angle, True, True)
#End-def

# Aim delta calculation function
def calc_aim_delta(rel_pos, rel_vel, bullet_speed):
    a = Vector2.dot(rel_vel, rel_vel) - bullet_speed**2
    b = 2 * Vector2.dot(rel_vel, rel_pos)
    c = Vector2.dot(rel_pos, rel_pos)
    disc = b*b - 4*a*c

    if(disc > 0):
        return 2 * c / ((disc * 0.5) - b)
    else:
        return -1
# Helper Linear Interpolation function
def lerp(start, end, t):
    return start * (1 - t) + end * t