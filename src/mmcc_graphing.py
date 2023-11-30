import matplotlib.pyplot as plt
import numpy as np

from assignment1 import MMCCSimulation
from mmcc_val import loss_rate
from typing import List



SERVERS = 16
CUSTOMERS = 2000
SERVICE_TIME = 100
RUNS = 25

def main():

    while True:
        choice = menu()
        match choice:
            case "x":
                return
            case "1":
                full_simulation_output()
            case "2":
                full_simulation_output(True) 
            case "3":
                server_utilisation()
            case _:
                pass
        


def full_simulation_output( ts : bool = False ):
    """Docstring to do.
    """
    sim_data_points : List[float] = []
    ts_data_points : List[float] = []
    ana_data_points : List[float] = []

    total_sim_time : int = 0

    simts : MMCCSimulation | None = None

    x_values : List[float] = [x/1000 for x in range(10,101,3)]
    for x in x_values:
        avg_block_rate = 0
        ts_avg_block_rate = 0

        server_util_list : List[float] = [0 for _ in range(SERVERS)]

        for _ in range(RUNS):
            sim : MMCCSimulation = MMCCSimulation(
                    CUSTOMERS,
                    SERVERS,
                    SERVICE_TIME,
                    x)
            sim.run()
            avg_block_rate += sim.find_loss_rate()

            if ts:
                simts : MMCCSimulation = MMCCSimulation(
                        CUSTOMERS,
                        SERVERS,
                        SERVICE_TIME*10,
                        x/10)
            
                simts.run()
                ts_avg_block_rate += simts.find_loss_rate()

        if ts:
            ts_avg_block_rate /= RUNS
            ts_data_points.append(round(ts_avg_block_rate, 4))

        avg_block_rate /= RUNS

        sim_data_points.append(round(avg_block_rate, 4))
        ana_data_points.append(round(loss_rate(x, 1/SERVICE_TIME, SERVERS),4))

    
    if ts:
        lines = [sim_data_points, ts_data_points, ana_data_points]
        labels = ["Standard Simulation", "10x Increased timesteps", "Analytical"]
    else:
        lines = [sim_data_points, ana_data_points]
        labels = ["Standard Simulation", "Analytical"]
    
    plot_lines(lines, labels, x_values)


def plot_lines(array_of_lines : List[List[float]], line_labels : List[str], x_axis : List[float]):
    """Print the arrays of lines given on the same axis"""
    for line, lab in zip(array_of_lines, line_labels):
        plt.plot(x_axis, line, label=lab)
    ax = plt.gca()
    
    
    max_dif = max(array_of_lines[-1])/100
    ax.set_ylim([min(array_of_lines[-1])-max_dif, max_dif * 101])
    plt.legend()
    plt.show()
    
def server_utilisation():
    """Produce a heatmap for the server utilisation of a various amounts of arrival rates"""
    total_sim_time : int = 0

    x_values = [x/1000 for x in range(10, 101, 3)]
    
    server_utils : List[List[float]] = []
    for x in x_values:
        server_utilisation : List[float] = [0.0 for x in range(SERVERS)]
        
        for _ in range(RUNS):
            sim : MMCCSimulation = MMCCSimulation(
                    CUSTOMERS,
                    SERVERS,
                    SERVICE_TIME,
                    x)
            sim.run()

            for index, server in enumerate(sim.servers):
                server_utilisation[index] += server.serve_time / sim.time

        for index, value in enumerate(server_utilisation):
            server_utilisation[index] = round(value / RUNS, 4)

        server_utils.append(server_utilisation)
    


    output = np.rot90(server_utils)
    
    plt.imshow(output, interpolation=('nearest'))
    plt.colorbar()
    plt.show()

def menu():
    print("Select what to test and graph for MMCC queue:\n")
    print("[1] Blocking rates (ar: 0.01-0.1, 0.003 incr, " \
          " runs each data point), with analytical results")
    print("[2] Option (1) with additional 10x timescaled results")
    print("[3] Display heatmap of server utilisation")
    print("[x] Exit")

    return input()

if __name__ == "__main__":
    main()

