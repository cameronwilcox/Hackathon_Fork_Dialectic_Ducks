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
    if len(LoT) > 3:
        priority_target = LoT[1]
    else:
        print("start")
        return (0, False, False)
    
    # Target variables
    target_type = priority_target[0]
    target_pos = Vector2(priority_target[1][0], priority_target[1][1])
    target_vel = Vector2(priority_target[2][0], priority_target[2][1])

    # Turret variables
    turret_pos = Vector2(coord[0], coord[1])

    delta_x = turret_pos.x - (target_pos.x + (target_vel.x))
    delta_y = turret_pos.y - (target_pos.y + (target_vel.y))

    # Kind of dumb, but works? - Not really :(
    if target_pos == turret_pos.x and current_dir == 90:
        return (90, True, False)
    elif target_dir == turret_pos.x and current_dir == -90:
        return (-90, True, False)
    if priority_target[1][0] < coord[0]:
        angle = math.degrees(math.atan(delta_y/delta_x)) + 180
    elif priority_target[1][0] == coord[0]:
        if priority_target[1][1] > coord[1]:
            return (90, False, False)
        else:
            return (-90, False, False)
    else:
        angle = math.degrees(math.atan(delta_y/delta_x))

    return (angle, True, False)
#End-def