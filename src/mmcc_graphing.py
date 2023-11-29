import matplotlib.pyplot as plt
import numpy as np

from assignment1 import MMCCSimulation
from mmcc_val import loss_rate
from typing import List

def main():
    choice = menu()

    # CONFIG
    RUNS = 25
    CUSTOMERS = 10000
    SERVERS = 16
    SERVICE_TIME = 100

    while choice != "1" and choice != "x":
        choice = menu()

    if choice == "x":
        return

    sim_data_points : List[float] = []
    ts_data_points : List[float] = []
    ana_data_points : List[float] = []

    total_sim_time : int = 0
    for x in range(10, 101, 3):
        ar = x / 1000
        avg_block_rate = 0
        ts_avg_block_rate = 0

        server_util_list : List[float] = [0 for _ in range(SERVERS)]

        for _ in range(RUNS):
            sim : MMCCSimulation = MMCCSimulation(
                    CUSTOMERS,
                    SERVERS,
                    SERVICE_TIME,
                    ar
                    )
            sim.run()
            avg_block_rate += sim.find_loss_rate()

            simts : MMCCSimulation = MMCCSimulation(
                    CUSTOMERS,
                    SERVERS,
                    SERVICE_TIME*10,
                    ar/10)
            
            simts.run()

            for i, server in enumerate(sim.servers):
                server_util_list[i] += server.serve_time

            total_sim_time += sim.time
            ts_avg_block_rate += simts.find_loss_rate()

        ts_avg_block_rate /= RUNS
        avg_block_rate /= RUNS
        norm_serv_utilisation = [round(time / total_sim_time,4) for time in server_util_list]

        ts_data_points.append(round(ts_avg_block_rate, 4))
        sim_data_points.append(round(avg_block_rate, 4))
        ana_data_points.append(round(loss_rate(ar, 1/SERVICE_TIME, SERVERS),4))

    print(sim_data_points)
    print(ts_data_points)
    print(ana_data_points)




def menu():
    print("Select what to test and graph for MMCC queue:\n")
    print("[1] Blocking rates of the simulation (ar: 0.01-0.1, 0.003 incr, " \
          "25 runs each data point)")
    print("[2] Analytical blocking rates of MMCC queue ar: (0.01-0.1, 0.003 incr)")
    print("[3] Options 1 and 2 on the same graph")
    print("[4] 10x Time stretched blocking rate of the simulation, on the same graph as 3")
    
    print("[x] Exit")

    return input()

if __name__ == "__main__":
    main()

