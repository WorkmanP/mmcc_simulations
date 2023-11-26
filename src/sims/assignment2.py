""""""

from math import ceil
from typing import List

import logging

import time as time_module
import numpy as np

from assignment1 import (MMCCSimulation, Customer,
                        UniversalServer)

class PriorityMismatchError(Exception):
    """Exception raised when a customer is being served by a server
    which they should not have access to.
    
    @attributes:
        customer_priority -- the customers priority
        server_priority -- the servers priority
        message -- explaination of the error
    """

    def __init__(self, customer_priority : int, server_priority : int) -> None:
        self.customer_priority = customer_priority
        self.server_priority = server_priority

        self.message =  f"""Customer does not have adequate priority to be served
             by this server. ({customer_priority} < {server_priority})
            """.strip("\n", "")
        super().__init__(self.message)

class PriorityCustomer(Customer):
    """Overriding the Customer class adding priority functionality and service
    A customer can only use servers of a less than or equal to priority

    @parameters:
        priority -- A represention of which rank of servers a customer can use
    """
    priority : int
    def __init__(self, time: int, given_id: int, priority: int = 0) -> None:
        self.priority = priority
        super().__init__(time, given_id)

    def serve(self, server : 'PriorityServer', time : int):
        """Overrides the Customer serve method. Compares the priority of
        the customer and the server, and judges if they are compatable

        @parameters:
            server -- The priority server to serve the customer
            time -- The simulation time of the start of the service

        @raises:
            PriorityMismatchError -- Where server and customer priority is incompatable
        """
        if server.priority > self.priority:
            raise PriorityMismatchError(self.priority, server.priority)
        super().serve(server, time)

    def __str__(self) -> str:
        return f"Customer ID: {self.id}, Priority: {self.priority} " \
            f"Birth: {self.birth_time}, Rejected:{self.rejected}, " \
            f"Server ID: {self.served_by}, " \
            f"Service Time: {self.service_time}, " \
            f"Death: {self.death_time}" 

    def to_csv(self) -> str:-----------------------------------------------
        """Used to represent the current state of the customer in CSV format:
        the structure is as follows:
        ID,Priority,Birth Time,Death Time,
        Rejected,ServerID(None if rejected), Service Time(None if rejected),
        Death Time
        """
        return f"{self.id},{self.priority},{self.birth_time}," \
            f"{self.rejected},{self.served_by},{self.service_time}," \
            f"{self.death_time}"


class PriorityServer(UniversalServer):
    """Overrides the UniversalServer class adding priority functionality
    a server can serve only serve customers with a >= priority

    @parameters:
        priority -- A representation of which customers the server should serve"""
    priority : int

    def __init__(self, given_id: int, priority: int = 0) -> None:
        self.priority = priority
        super().__init__(given_id)

    def __str__(self) -> str:
        return f"Server ID: {self.id}, Priority: {self.priority} " \
            f"Idle: {self.idle}, Idle time: {self.idle_time}, " \
            f"Current Customer: {repr(self.current_customer)}, " \
            f"Customers Served: {self.cust_served}, " \
            f"Total service time: {self.serve_time}"

    def __repr__(self) -> str:
        return f"PriorityServer({self.id}, {self.priority})"

    def to_csv(self) -> str:
        """Converts the server type to a CSV, the representation is as follows:
        ID,Priority,Idle,Idle_time,CustomersServed,TotalServeTime

        @returns:
            A CSV representation of the state and historical use of the server
        """
        return f"{self.id},{self.priority},{self.idle},{self.idle_time}," \
            f"{self.cust_served},{self.serve_time}"

class M1M2MCCSimulation(MMCCSimulation):
    """"""
    server_ammounts : List[int]
    customer_priority_bias : List[float]
    service_avg : List[int] # Override old type as prioirities could have diff rates
    servers : List[PriorityServer] = []

    def __init__(self,
                 customer_count : int,
                 server_ammounts : List[int],
                 service_avg : List[float],
                 arrival_rate : float,
                 customer_priority_bias : List[float],
                 start_time : int = round(time_module.time())
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
        curr_id = 0
        for priority, ammount in enumerate(self.server_ammounts):
            for x in range(ammount):
                self.servers.append(PriorityServer(curr_id + x, priority))
            curr_id += 1

        for i, server in enumerate(self.servers):
            server.rands = self.rand_arrays[i+1].copy()
            self.next_events.append(999999999)

    def birth_customer(self) -> None:
        cust_priority = self.gen_customer_priority()
        customer = PriorityCustomer(self.time, len(self.customers), cust_priority)
        self.customers.append(customer)

        # As we don't have a queue, if every server is full, the customer is turned away
        self.assign_customer(customer)
        return customer
    
    def gen_customer_priority(self) -> int:
        rand_number = np.random.rand() * sum(self.customer_priority_bias)

        boundary_val = 0
        for index, value in enumerate(self.customer_priority_bias):
            boundary_val += value
            if boundary_val > rand_number:
                return index

    def get_available_servers(self, customer : PriorityCustomer = None) -> List[UniversalServer]:
        if customer is None:
            raise TypeError("customer parameter can not be None")
        return [server for server in self.servers if (
            server.idle and server.priority <= customer.priority)]

    def output_results(self, dir_path : str = "../../results/rank/"):
        file_name = dir_path + f"customers/{self.start_time}.csv"
        with open(file_name, "w", encoding='utf-8') as file:
            for cust in self.customers:
                file.write(cust.to_csv() + "\n")

        file_name = dir_path + f"servers/{self.start_time}.csv"
        with open(file_name, "w", encoding='utf-8') as file:
            for serv in self.servers:
                file.write(serv.to_csv() + "\n")


def main():
    start_time = round(time_module.time())
    logging.basicConfig(filename= f'../../logs/rank/{start_time}.log',
                        encoding='utf-8',
                        level=logging.DEBUG)

    sim : M1M2MCCSimulation = M1M2MCCSimulation(
        100,
        [5,5],
        [5,5],
        0.5,
        [0.5,0.5],
        round(time_module.time()))
    sim.run()
    sim.output_results()
    return

if __name__ == "__main__":
    main()

