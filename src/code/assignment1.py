'''
'''
from math import ceil
from typing import List

import logging

import time as timeMod
import numpy as np

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


class Customer:
    id : int = 0

    priority : int = 0

    birth_time : int = 0
    death_time : int = 0

    service_time : int | None = 0
    served_by : int | None

    rejected : bool = False

    def __init__(self, time : int, given_id : int, priority: int = 0) -> None:
        self.birth_time = time
        self.id = given_id
        self.priority = priority

    def reject(self, time : int) -> None:
        self.rejected = True
        self.service_time = None
        self.served_by = None
        self.death_time = time
    
    def serve(self, server : 'UniversalServer', time: int) -> None:
        if server.priority > self.priority:
            raise PriorityMismatchError(self.priority, server.priority)

        self.served_by = server.id
        self.service_time = time

    def kill(self, time : int) -> None:
        self.death_time = time

    def __str__(self) -> str:
        return f"Customer ID: {self.id} " \
            f"Birth: {self.birth_time}, Rejected: {self.rejected}, " \
            f"Server ID: {self.served_by}, " \
            f"Service Time: {self.service_time}, " \
            f"Death: {self.death_time}" 

    def __repr__(self) -> str:
        return f"CustomerObject({self.id}, {self.priority}," \
            f"{self.birth_time}"

    def to_csv(self) -> str:
        return f"{self.id},{self.priority},{self.birth_time}," \
        f"{self.rejected},{self.served_by},{self.service_time},{self.death_time}"

class UniversalServer:
    id : int = 0
    idle : bool = True

    priority : int = 0
    current_customer : Customer | None = None

    serve_time : int = 0
    idle_time : int = 0

    last_update_time : int = 0
    cust_served : int = 0

    rands = []

    def __init__(self, given_id : int) -> None:
        self.id = given_id

    def set_serve_time(self, rands : List[int]):
        self.rands = rands  # Python passes arrays by reference so this is just
                            # for ease of access / code clarity

    def serve(self, customer : Customer, time : int) -> int:
        self.update(time)
        time_to_serve = self.rands.pop(0)
        customer.serve(self, time_to_serve)
        self.current_customer = customer
        self.idle = False
        self.cust_served += 1

        return time_to_serve + time

    def finish_serve(self, time : int) -> None:
        self.current_customer.kill(time)
        self.current_customer = None
        self.update(time)
        self.idle = True

    def update(self, time : int) -> None:
        if self.idle:
            self.idle_time += (time-self.last_update_time)
            self.last_update_time = time
            return
        self.serve_time += (time-self.last_update_time)
        self.last_update_time = time

class UniversalSimulation:
    customer_count : int
    server_count : int
    service_avg : int
    arrival_rate : float

    rand_arrays : List[List[int]]
        # The first index contains the times of birth for the customers,
        # The following determines the time of processing for the servers
    time : int

    servers : List[UniversalServer]
    customers : List[Customer]

    customer_birth_times : List[int]
    next_events : List[int]

    def __init__(self,
                 customer_count : int,
                 server_count : int,
                 service_avg: int,
                 arrival_rate: int) -> None:

        self.customer_count = customer_count
        self.server_count = server_count
        self.service_avg = service_avg
        self.arrival_rate = arrival_rate
        self.next_events = []
        self.customers = []
        self.time = 0

        self.set_rand_array()
        self.create_servers()


    def set_rand_array(self) -> None:
        self.rand_arrays = []
        self.rand_arrays.append([ceil(np.random.exponential((1/self.arrival_rate)-0.5))
                            for _ in range(self.customer_count)])
            # We adjust the exp average by -.5 as the ceil function increases the average by 0.5

        self.customer_birth_times = self.rand_arrays[0].copy()
        self.next_events.append(self.customer_birth_times[0])
            # Add the first birth of customer to the event list

        for _ in range(self.server_count):
            self.rand_arrays.append([ceil(np.random.exponential(self.service_avg-0.5))
                                for _ in range(self.customer_count)])
            # We adjust the exp average by -.5 as the ceil function increases the average by 0.5

    def create_servers(self) -> None:
        self.servers = [UniversalServer(x) for x in range(self.server_count)]
        for i, serv in enumerate(self.servers):
            serv.rands = self.rand_arrays[i+1].copy()
            self.next_events.append(999999999)

    def birth_customer(self) -> None:
        customer = Customer(self.time, len(self.customers))
        self.customers.append(customer)

        # As we don't have a queue, if every server is full, the customer is turned away
        self.assign_customer(customer)
        return customer

    def assign_customer(self, customer : Customer) -> bool:
        available_servers = [serv for serv in self.servers if serv.idle]

        if len(available_servers) == 0:
            customer.reject(self.time)
            return False

        # The manner of choosing which server to pick can be assigned here, but
        # for now, we'll just go for the first
        chosen_serv = available_servers[0]
        next_event_time = chosen_serv.serve(customer, self.time)
        self.next_events[self.servers.index(chosen_serv)+1] = next_event_time
        return True

    def time_jump(self) -> None:
        next_time = min(self.next_events)
        self.time = next_time

    def run(self):
        # While there are still staged events...
        while min(self.next_events) < 999999999:
            self.time_jump()

            staged_events : List[int] = []
            for i, event_time in enumerate(self.next_events):
                if event_time == self.time:
                    staged_events.append(i)

            if staged_events[0] == 0:
                self.birth_customer()

                if self.customer_birth_times:
                    self.next_events[0] = self.time + self.customer_birth_times.pop(0)
                else:
                    self.next_events[0] = 999999999
                staged_events.pop(0)

            for index in staged_events:
                self.servers[index-1].finish_serve(self.time)
                self.next_events[index] = 999999999

        for cust in self.customers:
            logging.info(str(cust))
        return
    
    def output_results(self, dir_path : str = "../results/"):
        file_name = dir_path + f"csv_results_{round(timeMod.time())}.csv"
        with open(file_name, "w", encoding='utf-8') as file:
            for cust in self.customers:
                file.write(cust.to_csv() + "\n")


def main():
    logging.basicConfig(filename= f'../../logs/no-rank/{round(timeMod.time())}.txt',
                        encoding='utf-8',
                        level=logging.DEBUG)
    sim : UniversalSimulation = UniversalSimulation(
        100,
        5,
        100,
        1/10
    )

    sim.run()
    sim.output_results()
    return

if __name__ == "__main__":
    main()
