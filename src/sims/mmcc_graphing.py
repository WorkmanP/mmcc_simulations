import matplotlib.pyplot as plt
import numpy as np

from assignment1 import MMCCSimulation

from typing import List

def main():
    choice = menu()

    # CONFIG
    RUNS = 50
    CUSTOMERS = 1000
    SERVERS = 16
    SERVICE_TIME = 100

    while choice != "1" and choice != "x":
        choice = menu()

    if choice == "x":
        return
    
    sim_data_points : List[float] = []
    
    for x in range(10, 101, 3):
        ar = x / 1000
        avg_block_rate = 0
        for _ in range(RUNS):
            sim : MMCCSimulation = MMCCSimulation(
                    CUSTOMERS,
                    SERVERS,
                    SERVICE_TIME,
                    ar
                    )
            sim.run()
            avg_block_rate += sim.find_loss_rate()

        avg_block_rate /= RUNS

        sim_data_points.append(avg_block_rate)

    print(sim_data_points)


def menu():
    print("Select what to test and graph for MMCC queue:\n")
    print("[1] Blocking rates of the simulation, (ar: 0.01-0.1, 0.003 incr, 50 runs each data point)")
    print("[x] Exit")

    return input()

if __name__ == "__main__":
    main()

