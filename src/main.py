import matplotlib.pyplot as plt
import numpy as np

from MMCCSimulation import MMCCSimulation
from mmcc_val import loss_rate, find_for_loss_rate
from m1m2mcc_application import question2_2
from typing import List

SERVERS = 16
CUSTOMERS = 2000
SERVICE_TIME = 100
RUNS = 25

def main():
    while True:
        print("--------------------------------")
        choice = menu()

        print("--------------------------------")
        match choice:
            case "x":
                return
            case "1":
                full_simulation_output()
            case "2":
                full_simulation_output(True) 
            case "3":
                server_utilisation()
            case "4":
                find_max_value(0.01)
            case "5":
                print(find_for_loss_rate(1/SERVICE_TIME, SERVERS, 0.01))
            case "6":
                question2_2([0.1, None], 0.02)
            case "7":
                question2_2([None, 0.03], 0.02)
            case _:
                pass

        input("<Enter> to continue")



def full_simulation_output( ts : bool = False ):
    """Docstring to do.
    """
    sim_data_points : List[float] = []
    ts_data_points : List[float] = []
    ana_data_points : List[float] = []

    simts : MMCCSimulation | None = None

    x_values : List[float] = [x/1000 for x in range(10,101,3)]
    for x in x_values:
        avg_block_rate = 0
        ts_avg_block_rate = 0

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

    plt.xlabel("Arrival Rate (calls / second)")
    plt.ylabel("Block probability")
    ax.set_title("Blocking probability for M/M/C/C Queue.\n(service average: 100)")

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

    fig, ax = plt.subplots()

    output = np.rot90(server_utils)

    im = ax.imshow(output, interpolation='nearest')
    ax.set_xticks(np.arange(len(server_utils)), labels=[
        (3*x+1)/1000  if x%3 == 0 else "" for x in range(3, 34, 1)
        ])
    ax.set_yticks(np.arange(SERVERS), labels=[
        x  if x%3 == 0 else "" for x in range(SERVERS-1, -1, -1)
        ])
    plt.setp(ax.get_xticklabels(), rotation=60, ha="right",
             rotation_mode="anchor")

    plt.xlabel("Arrival Rate (calls / second)")
    plt.ylabel("Server ID")
    ax.set_title("Server Utilisation for M/M/C/C Queue.\n(service average: 100)")
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel("Average proportion of time in service")
    plt.show()


def find_max_value(max_blocking_prob : float = 0.01) -> None:

    values : List[float] = []
    for _ in range(10):
        values.append(mmcc_max_value(max_blocking_prob))

    min_val = min(values)
    max_val = max(values)

    print(f"Simulation puts the arrival rate between {min_val} and {max_val}")

def mmcc_max_value(max_blocking_prob : float = 0.01) -> float:
    """Implement a binary search of the simulation to find the highest arrival
    rate where the blocking probability does not exceed the max_blocking_prob

    @parameters:
        max_blocking_prob -- The target blocking probability to get
    """
    test_arrival_rate : float = 0.5
    cycle : int = 2
    epsilon : float = 0.0001
    
    while True:

        value : float = get_average_loss_rate(test_arrival_rate)

        if (value + epsilon) < max_blocking_prob:
            test_arrival_rate += 0.5**cycle
        elif (value - epsilon) > max_blocking_prob:
            test_arrival_rate -= 0.5**cycle
        elif cycle > 30:
            print("Could not resolve answer, restarting...")
            test_arrival_rate = 0.5
            cycle = 1
            epsilon *= 2
        else:
            print(f"Found block rate of {round(value, 4)}, for arrival rate {test_arrival_rate}")
            return test_arrival_rate
        
        cycle += 1
        
def get_average_loss_rate(ar : float, runs : int = 25):
    """Get the average loss rate for a simulation with a given arrival rate

    @parameters:
        ar -- arrival rate, between 0-1
        runs -- how many simulations to complete before getting the loss rate
    """
    avg_loss_rate : float = 0
    for _ in range(runs): 
        sim : MMCCSimulation = MMCCSimulation(
                2000,
                SERVERS,
                SERVICE_TIME,
                ar 
            )
        sim.run()
        avg_loss_rate += sim.find_loss_rate()
    
    return avg_loss_rate / runs

def menu():
    print("Select what to test and graph for M/M/C/C queue:\n")
    print("[1] Blocking rates (ar: 0.01-0.1, 0.003 incr, " \
          "25 runs each data point), with analytical results")
    print("[2] Option (1) with additional 10x timescaled results")
    print("[3] Display heatmap of server utilisation")
    print("[4] Get best arrival rate for a max blocking prob of 0.01")
    print("[5] Get analytical best arrival rate for max blocking prob 0.01")
    print("\nSelect what to test and graph for M1M2/M/C/C queue:\n")
    print("[6] Max arrival rate for ABP<0.02 for 0.1 new arrival rate")
    print("[7] Max arrival rate for ABP<0.02 for 0.03 handover rate")
    print("\n[x] Exit")

    return input()

if __name__ == "__main__":
    main()

