""""""
from assignment1 import (MMCCSimulation, Customer,
                        UniversalServer, PriorityMismatchError)
from math import ceil
from typing import List

import time
import numpy as np

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
    
    def produce_server_rand_arrays(self):
        for priority, ammount in enumerate(self.server_ammounts):
            for _ in range(ammount):
                self.rand_arrays.append([ceil(np.random.exponential(self.service_avg[priority]))
                                         for _ in range(self.customer_count)])

    def create_servers(self):
        self.servers = []
        curr_id = 0
        for priority, ammount in enumerate(self.server_ammounts):
            self.servers = [UniversalServer(curr_id + x, priority) for x in range(ammount)]
            curr_id += 1

        for i, server in enumerate(self.servers):
            server.rands = self.rand_arrays[i+1].copy()
            self.next_events.append(999999999)

    def get_available_servers(self, customer : Customer) -> bool:
        return [server for server in self.servers if (
            server.idle and server.priority <= customer.priority)]

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

