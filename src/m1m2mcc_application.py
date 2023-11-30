from M1M2MCCSimulation import M1M2MCCSimulation
from typing import List
import math

# Config:
CUSTOMERS = 20
SERVERS = [14,2]
SERVICE_AVG = [100, 100]
ARRIVAL_RATES = [0.1, 0.05]

def main():
    sim : M1M2MCCSimulation = M1M2MCCSimulation(
            10,
            SERVERS,
            SERVICE_AVG,
            ARRIVAL_RATES
        )
    sim.run()
    sim.output_results()
    return

def question2_2() -> float:
    sim : M1M2MCCSimulation = M1M2MCCSimulation(
            1000,
            SERVERS,
            SERVICE_AVG,
            ARRIVAL_RATES
        )

def get_average_abp(ars : List[float]) -> float:
    
    abp : float = 0.0
    for _ in range(10):
        sim = None
        print(sim)
        sim = M1M2MCCSimulation(
                    1000,
                    SERVERS,
                    SERVICE_AVG,
                    ars
                    )
        sim.run()

        print(sim.get_abp())
        abp += sim.get_abp()

    print(abp / 10)
    return abp / 10



if __name__ == "__main__":
    get_average_abp([0.1, 0])

