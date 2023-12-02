""""""

from math import ceil
from typing import List

import logging

import time as time_module
import numpy as np

from MMCCSimulation import (MMCCSimulation, Customer,
                        UniversalServer, discrete_exponential,
                        poisson_process)

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
    
    def __repr__(self) -> str:
        return f"CustomerObject({self.id},{self.priority}," \
            f"{self.birth_time})"

    def to_csv(self) -> str:
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
    """ The object containing the logic for a M1/M2/M/C/C Queue
    
    @attributes:
        server_ammounts     -- A list where the index is the priority and the value is 
                            the ammount of servers for that priority
        service_avg         -- A list of the average service time for each server priority
        servers             -- Altered to [PriorityServer] type
        customers           -- Altered to [PriorityCustomer] type
    """
    server_ammounts : List[int] # [14,2]
    service_avg : List[int] # Override old type as prioirities could have diff rates
    servers : List[PriorityServer] = []
    customers : List[PriorityCustomer]

    def __init__(self,
                 customer_count : int,
                 server_ammounts : List[int],
                 service_avg : List[float],
                 arrival_rates : List[float],
                 start_time : int = round(time_module.time())
                 ) -> None:
        self.server_ammounts = server_ammounts
        self.arrival_rates = arrival_rates
        super().__init__(customer_count,
                         sum(server_ammounts),
                         service_avg,
                         arrival_rates,
                         start_time)

        logging.info("server ammounts: %s", str(server_ammounts))

        for array in self.customer_birth_times[1:]:
            self.next_events.append(array.pop(0))
        
    def set_rand_array(self) -> None:
        """Set the random arrays for the customer creation and the servers"""
        self.rand_arrays = []

        if self.arrival_rates[0] == 0.0:
            self.rand_arrays.append([99999999999 for _ in range(self.customer_count)])
        else:
            self.rand_arrays.append(discrete_exponential(1/self.arrival_rates[0], self.customer_count))
        self.customer_birth_times : List[List[int]] = []
        self.customer_birth_times.append(self.rand_arrays[0].copy())

        self.next_events.append(self.customer_birth_times[0].pop(0))
        self.produce_server_rand_arrays()

        for rate in self.arrival_rates[1:]:
            if rate == 0:
                self.rand_arrays.append([99999999999 for _ in range(self.customer_count)])
            else:
                self.rand_arrays.append(discrete_exponential(1/rate, self.customer_count))
            self.customer_birth_times.append(self.rand_arrays[-1].copy())


    def produce_server_rand_arrays(self):
        for priority, ammount in enumerate(self.server_ammounts):
            for _ in range(ammount):
                self.rand_arrays.append(discrete_exponential(
                    self.service_avg[priority],
                    self.customer_count))

    def create_servers(self):
        curr_id = 0
        for priority, ammount in enumerate(self.server_ammounts):
            for x in range(ammount):
                self.servers.append(PriorityServer(curr_id + x, priority))
            curr_id += 1
        for i, server in enumerate(self.servers):
            server.rands = self.rand_arrays[i+1].copy()
            self.next_events.append(999999999)

    def birth_customer(self, priority : int) -> None:
        customer = PriorityCustomer(self.time, len(self.customers), priority)
        self.customers.append(customer)

        # As we don't have a queue, if every server is full, the customer is turned away
        self.assign_customer(customer)
        return customer

    def get_available_servers(self, customer : PriorityCustomer = None) -> List[UniversalServer]:
        if customer is None:
            raise TypeError("customer can not be None")
        output = [server for server in self.servers if (
            server.idle and server.priority <= customer.priority)]
        return output

    def output_results(self, dir_path : str = "../results/rank/"):
        file_name = dir_path + f"customers/{self.start_time}.csv"
        with open(file_name, "w", encoding='utf-8') as file:
            for cust in self.customers:
                file.write(cust.to_csv() + "\n")

        file_name = dir_path + f"servers/{self.start_time}.csv"
        with open(file_name, "w", encoding='utf-8') as file:
            for serv in self.servers:
                file.write(serv.to_csv() + "\n")


    def run(self):
        while min(self.next_events) < 999999:
            staged_events = self.jump_next_event()

            for index in staged_events:
                if 1 <= index < 1 + len(self.servers):
                    self.servers[index-1].finish_serve(self.time)
                    self.next_events[index] = 99999999
                    continue
                
                if index == 0:
                    priority = index
                else:
                    priority = index - len(self.servers)
                

                self.birth_customer(priority)

                if self.customer_birth_times[priority] and len(self.customers)<self.customer_count-1:
                    self.next_events[index] = self.time + self.customer_birth_times[priority].pop(0)
                else:
                    self.next_events[index] = 999999999

    def get_abp(self):
        new_calls_accepted : int = 0
        new_calls_total : int = 0

        handover_accepted : int = 0
        handover_total : int = 0

        for cust in self.customers:
            if cust.priority == 0:
                new_calls_total += 1

                if not cust.rejected:
                    new_calls_accepted += 1

            else:
                handover_total += 1

                if not cust.rejected:
                    handover_accepted += 1
        
        if new_calls_total == 0:
            cbp = 0
        else:
            cbp : float = 1 - (new_calls_accepted / new_calls_total)

        if handover_total == 0:
            hbp = 0
        else:
            hbp : float = 1 - (handover_accepted / handover_total)
        
        return cbp + 10 * hbp

def test():
    start_time = round(time_module.time())
    logging.basicConfig(filename= f'../logs/rank/{start_time}.log',
                        encoding='utf-8',
                        level=logging.DEBUG)

    sim : M1M2MCCSimulation = M1M2MCCSimulation(
        10,
        [3,2],
        [50,50],
        [0.1, 0.08],
        round(time_module.time()))
    sim.run()
    sim.output_results()
    return

if __name__ == "__main__":
    test()
