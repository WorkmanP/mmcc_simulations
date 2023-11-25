""""""
from assignment1 import (MMCCSimulation, Customer,
                        UniversalServer, PriorityMismatchError)
from typing import List
import time

class M1M2MCCSimulation(MMCCSimulation):
    """"""
    server_ammounts : List[int]
    customer_priority_bias : List[float]
    service_avg : List[int] # Override old type as prioirities could have diff rates

    def __init__(self,
                 customer_count : int,
                 server_ammounts : List[int],
                 service_avg : List[float],
                 arrival_rate : float,
                 customer_priority_bias : List[float],
                 start_time : int = round(time.time())
                 ) -> None:
        self.server_ammounts = server_ammounts
        self.customer_priority_bias = customer_priority_bias
        super().__init__(customer_count,
                         sum(server_ammounts),
                         service_avg,
                         arrival_rate,
                         start_time)
    
    def set_rand_array(self):
        print("test")

    def create_servers(self):
        print("test2")


def main():
    print("in main")
    return

if __name__ == "__main__":
    print("hello")
    sim : M1M2MCCSimulation = M1M2MCCSimulation(
            10,
            [5,5],
            [5,5],
            0.5,
            [0.5,0.5],
            time.time())
    main()

