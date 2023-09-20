import os
import time

def pick_own_move(opponent_move):
    return ("dot1", "dot2")

def read_opponent_move():
    with open("move_file", 'rb') as file:
        try: 
            file.seek(-2, os.SEEK_END)
            while file.read(1) != b'\n':
                file.seek(-2, os.SEEK_CUR)
        except OSError:
            file.seek(0)
        return file.readline().decode()

def write_move(dot1, dot2):
    move = groupname + " " + dot1 + " " + dot2

    with open("move_file", "w") as file:
        file.write(move)

groupname = "omnifarious"
if __name__ == "__main__":

    start_time = 0
    pass_time_limit = 2
    while True:
        if os.path.exists(groupname + ".go"):
            start_time = time.perf_counter()
            opponent_move = read_opponent_move()
            print(opponent_move)
            our_move = pick_own_move(opponent_move)
            write_move("0,0", "0,0")
            print("move completed")
            # gotta wait until the file is gone probably just a time.sleep(0.1)
            time.sleep(100)
        elif os.path.exists(groupname + ".pass"):
            start_time = time.perf_counter()
            opponent_move = read_opponent_move()
            # our_move = pick_own_move(opponent_move)
            write_move("0,0", "0,0")
            print("pass completed")
            time.sleep(100)
        # Game ended break out of loop
        if os.path.exists("end_game"):
            break
        time.sleep(0.01)
    # Game is ended
    print("game ended")


