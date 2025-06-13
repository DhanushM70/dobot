import DobotDllType as dType
import json

# Load detected objects
with open('inverse/detected_positions.json', 'r') as f:
    detected_objects = json.load(f)

if not detected_objects:
    print("❌ No detected objects found.")
    exit()

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
    dType.SetQueuedCmdStartExec(api)
    dType.dSleep(3000)

    # Movement functions
    def pick(X, Y):
        current_pose = dType.GetPose(api)
        dType.SetPTPCmdEx(api, 2, X, Y, -42.7519, current_pose[3], 1)  # Move down
        dType.SetEndEffectorSuctionCupEx(api, 1, 1)  # Suction on
        dType.SetPTPCmdEx(api, 2, X, Y, -5.0959, current_pose[3], 1)  # Lift object

    # Drop locations for each color
    DROP_LOCATIONS = {
        "r": (189.4034, -215.4372, -38.7),
        "b": (136.1378, -217.6174, -38.7),
        "g": (89.6897, -222.9117, -38.7),
        "y": (37.9336, -221.5780, -38.7),
    }

    # Track how many times each color has been dropped
    drop_counts = {}

    def drop(color):
        current_pose = dType.GetPose(api)

        if color not in DROP_LOCATIONS:
            print(f"❌ No drop location defined for {color}.")
            return

        count = drop_counts.get(color, 0)
        drop_counts[color] = count + 1

        base_X, base_Y, base_Z = DROP_LOCATIONS[color]
        stacked_Z = base_Z + (count * 26.0)

        print(f"📦 Dropping {color} object #{count + 1} at Z={stacked_Z}")

        dType.SetPTPCmdEx(api, 2, base_X, base_Y, -5.0959, current_pose[3], 1)  # Above
        dType.SetPTPCmdEx(api, 2, base_X, base_Y, stacked_Z, current_pose[3], 1)  # Drop height
        dType.SetEndEffectorSuctionCupEx(api, 0, 1)  # Suction off
        dType.SetPTPCmdEx(api, 2, base_X, base_Y, -5.0959, current_pose[3], 1)  # Lift again

    # Process each detected object
    for i, obj in enumerate(detected_objects, 1):
        X = obj["x"]
        Y = obj["y"]
        Z = obj["z"]
        R = obj["r"]
        color = obj["color"]

        print(f"\n▶️ Processing object {i}: Color={color}, X={X}, Y={Y}, Z={Z}")
        current_pose = dType.GetPose(api)

        dType.SetPTPCmdEx(api, 2, X, Y, Z, current_pose[3], 1)
        pick(X, Y)
        drop(color)

    # Return to home position
    print("\n🏠 Returning to home position...")
    current_pose = dType.GetPose(api)
    dType.SetPTPCmdEx(api, 2, 160.0321, -3.1056, -23.3732, current_pose[3], 1)

    dType.DisconnectDobot(api)
    print("✅ Task completed. Dobot disconnected.")
else:
    print("❌ Failed to connect to Dobot.")
