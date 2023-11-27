import matplotlib.pyplot as plt
import numpy as np

from assignment1 import MMCCSimulation
from mmcc_val import loss_rate
from typing import List

def main():
    choice = menu()

    # CONFIG
    RUNS = 25
    CUSTOMERS = 1000
    SERVERS = 16
    SERVICE_TIME = 100

    while choice != "1" and choice != "x":
        choice = menu()

    if choice == "x":
        return
    
    sim_data_points : List[float] = []
    ana_data_points : List[float] = []
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
        ana_data_points.append(loss_rate(ar, 1/SERVICE_TIME, SERVERS))

    print(sim_data_points)
    print(ana_data_points)


def menu():
    print("Select what to test and graph for MMCC queue:\n")
    print("[1] Blocking rates of the simulation (ar: 0.01-0.1, 0.003 incr, " \
          "25 runs each data point)")
    print("[2] Analytical blocking rates of MMCC queue ar: (0.01-0.1, 0.003 incr)")
    print("[3] Options 1 and 2 on the same graph")
    print("[4] Server untilisation of the simulation (ar: 0.01-0.1, 0.003 incr, " \
          "25 runs per data point)")
    
    print("[x] Exit")

    return input()

if __name__ == "__main__":
    main()

