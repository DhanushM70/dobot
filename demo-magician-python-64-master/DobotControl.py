
# © 2025 Dilip Kumar S and Gokul S. All Rights Reserved.
# Authors: Dilip Kumar S, Gokul S
# Date: 2025-01-01
#
# This script is part of a proprietary project and may not be copied,
# modified, distributed, or used without explicit written permission 
# from the authors.

# This work was developed as part of a project at the Department of Robotics 
# and Automation, Rajalakshmi Engineering College, under the mentorship of 
# Mr. Ramkumar and guidance of our HoD, Dr. Giri.
#
# The computer vision logic in this script was fully developed by the authors
# and does not rely on any third-party SDKs or frameworks.
# 
# For robot motion control, this script uses only the official Dobot SDK 
# (DobotDllType) to ensure proper interfacing with the Dobot robotic arm,
# in accordance with the manufacturer's licensing and usage guidelines.
#
# WARNING: Any attempt to remove or alter this notice is strictly prohibited.
import DobotDllType as dType
from copy import deepcopy
import json

with open("color d&t/cube_matrix.json", "r") as f:
    cube_matrix = json.load(f)
with open("color d&t/final_cube_matrix.json", "r") as f:
    cube_matrix1 = json.load(f)

# Connect to Dobot
CON_STR = {
    dType.DobotConnect.DobotConnect_NoError: "DobotConnect_NoError",
    dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
    dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"
}

api = dType.load()
state = dType.ConnectDobot(api, "COM9", 115200)[0]
print("Connect status:", CON_STR[state])

if state == dType.DobotConnect.DobotConnect_NoError:
    dType.SetQueuedCmdClear(api)

    dType.SetHOMEParams(api, 159.9386, -3.1038, -23.3520, -2.0209, isQueued=1)
    dType.SetPTPJointParams(api, 100, 100, 100, 100, 100, 100, 100, 100, isQueued=1)
    dType.SetPTPCommonParams(api, 100, 100, isQueued=1)
    dType.SetHOMECmd(api, temp=0, isQueued=1)
    dType.SetQueuedCmdStartExec(api)
    dType.dSleep(5000)

    # Variables
    gap = 60
    homex = 210.8128
    homey = -65.7639
    homez = 17.9405
    z_increment = 0
    y_increment = 0
    operation = 1
    homey1 = homey
    homez1 = homez
    location = 0
    approach = 1

    # Define State-based solver
    class State:
        def __init__(self, cur, moves=None, absolute=True):
            self.cur = cur
            self.blocks = sum(len(row) for row in cur)
            self.moves = moves if moves is not None else []
            self.absolute = absolute

        def diff(self, other):
            return self.absolute_diff(other) if self.absolute else self.relative_diff(other)

        def relative_diff(self, other):
            num = 0
            for i in range(len(self.cur)):
                for j in range(len(other.cur)):
                    k = 0
                    while k < len(self.cur[i]) and k < len(other.cur[j]):
                        if self.cur[i][k] == other.cur[j][k]:
                            num += 1
                            k += 1
                        else:
                            break
            return self.blocks - num

        def absolute_diff(self, other):
            num = 0
            for i in range(len(self.cur)):
                j = 0
                while j < len(self.cur[i]) and j < len(other.cur[i]):
                    if self.cur[i][j] == other.cur[i][j]:
                        num += 1
                        j += 1
                    else:
                        break
            return self.blocks - num

        def move(self, a, b):
            if len(self.cur[a]) == 0:
                return None
            current = deepcopy(self.cur)
            current[b].append(current[a].pop())
            return State(current, self.moves + [(1, a, len(self.cur[a]) - 1), (0, b, len(self.cur[b]))])

        def next_state(self):
            for i in range(len(self.cur)):
                for j in range(len(self.cur)):
                    if i == j:
                        continue
                    nxt_state = self.move(i, j)
                    if nxt_state is None:
                        continue
                    yield nxt_state

        def __repr__(self):
            return ' '.join(''.join(x) for x in self.cur)

    def solve(initial, goal):
        initial = State(initial)
        goal = State(goal)

        if initial.blocks != goal.blocks or len(initial.cur) != len(goal.cur) or ''.join(sorted(str(initial))) != ''.join(sorted(str(goal))):
            print('Impossible')
            return []

        cur_states = [initial]
        global_minima = [initial.diff(goal), initial]
        seen = set()
        threshold = 0

        while global_minima[0] != 0 and cur_states:
            local_minima = [float('inf'), None]
            new_states = []

            for _ in range(len(cur_states)):
                cur_state = cur_states.pop()
                state_hash = str(cur_state)
                if state_hash in seen:
                    continue

                for nxt_state in cur_state.next_state():
                    score = nxt_state.diff(goal)
                    if score < local_minima[0]:
                        local_minima = [score, nxt_state]
                    nxt_state.score = score
                    new_states.append(nxt_state)

                seen.add(state_hash)

            if local_minima[0] < global_minima[0]:
                global_minima = local_minima

            cur_states = [nxt_state for nxt_state in new_states if nxt_state.score - global_minima[0] <= threshold]

        if global_minima[0] != 0:
            print('Impossible')
            return []

        print('Solution:', global_minima[1].moves)
        ans = []
        for a, b, c in global_minima[1].moves:
            ans.append(3 - c)
            ans.append(b)
            ans.append(a)

        return ans

    # Robot movement commands
    def pick():
        global z_increment, approach, y_increment, location, gap, homey1, homey, homez1, homez, homex
        z_increment = 21 * approach
        y_increment = location * gap
        homey1 = homey + y_increment
        homez1 = homez - z_increment
        current_pose = dType.GetPose(api)
        dType.SetPTPCmdEx(api, 2, homex, homey1, homez, current_pose[3], 1)
        dType.SetEndEffectorSuctionCupEx(api, 1, 1)
        dType.SetPTPCmdEx(api, 2, homex, homey1, homez1, current_pose[3], 1)
        dType.SetEndEffectorSuctionCupEx(api, 1, 1)
        dType.SetPTPCmdEx(api, 2, homex, homey1, homez, current_pose[3], 1)

    def drop():
        global z_increment, approach, y_increment, location, gap, homey1, homey, homez1, homez, homex
        z_increment = 20 * approach
        y_increment = location * gap
        homey1 = homey + y_increment
        homez1 = homez - z_increment
        current_pose = dType.GetPose(api)
        dType.SetPTPCmdEx(api, 2, homex, homey1, homez, current_pose[3], 1)
        dType.SetEndEffectorSuctionCupEx(api, 1, 1)
        dType.SetPTPCmdEx(api, 2, homex, homey1, homez1, current_pose[3], 1)
        dType.SetEndEffectorSuctionCupEx(api, 0, 1)
        dType.SetPTPCmdEx(api, 2, homex, homey1, homez, current_pose[3], 1)

    def decision():
        global operation
        if operation == 1:
            pick()
        elif operation == 0:
            drop()

    # Solve and execute
    plan = solve(
        initial=[cube_matrix, [], []],
        goal=[cube_matrix1, [], []],
    )

    for i in range(0, len(plan), 3):
        approach = plan[i]
        location = plan[i + 1]
        operation = plan[i + 2]
        decision()
        dType.dSleep(1500)

    # ✅ User Input Section to Manually Go to HOME
    while True:
        user_input = input("Press 1 to go HOME or q to quit: ")
        if user_input == "1":
            print("Executing HOMECmd...")
            dType.SetHOMECmd(api, temp=0, isQueued=1)
            dType.dSleep(3000)
        elif user_input.lower() == "q":
            break
        else:
            print("Invalid input. Press 1 to go HOME or q to quit.")

    dType.DisconnectDobot(api)
