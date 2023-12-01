from M1M2MCCSimulation import M1M2MCCSimulation
from typing import List

# Config:
CUSTOMERS = 20
SERVERS = [14,2]
SERVICE_AVG = [100, 100]
ARRIVAL_RATES = [0.1, 0.05]

def question2_2(arrival_rates : List[float | None], target_abp : float) -> float:
    none_indices : List[int] = []

    for i, rate in enumerate(arrival_rates):
        if rate is None:
            none_indices.append(i)

    if len(none_indices) != 1:
        raise ValueError("arrival_rates must contain only one none value")

    arrival_rates[none_indices[0]] = 0.0
    if get_average_abp(arrival_rates) > target_abp:
        print("Target ABP is not possible to achieve as set arrival rates")
        print("already cause the ABP to be higher than the target")
        return

    cycle : int = 2
    epsilon : float = 0.0001
    arrival_rates[none_indices[0]] = 0.5

    while True:
        abp : float = get_average_abp(arrival_rates)

        if abp + epsilon < target_abp:
            arrival_rates[none_indices[0]] += 0.5**cycle
        elif abp - epsilon > target_abp:
            arrival_rates[none_indices[0]] -= 0.5**cycle
        else:
            print(f"Suitable arrival rates found: {str(arrival_rates)}")
            return arrival_rates

        if cycle > 30:
            epsilon *= 2
            arrival_rates[none_indices[0]] = 0.5
            cycle = 1

        cycle += 1

def get_average_abp(ars : List[float]) -> float:
    
    abp : float = 0.0
    for _ in range(50):
        sim = M1M2MCCSimulation(
                    2000,
                    SERVERS,
                    SERVICE_AVG,
                    ars
                    )
        sim.run()
        abp += sim.get_abp()

    return abp / 10



if __name__ == "__main__":
    question2_2([0.1, None], 0.02)
    question2_2([None, 0.03], 0.02)

