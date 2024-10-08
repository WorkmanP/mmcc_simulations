'''
'''
from math import ceil, exp
from typing import List

import logging

import time as timeMod
import numpy as np


class Customer:
    """Class representing each a customer to be served
    by a service. 

    @attributes:
        id -- the customers unique ID, ordered by birth, earlier<later
        birth_time -- the global time of customer creation and queue entering
        death_time -- the global time a customer is finished being served
        service_time -- the time spent being served
        served_by -- the server ID of the instance serving the customer
        rejected -- a bool containing whether the customer was rejected
    """
    id : int = 0

    birth_time : int = 0
    death_time : int = 0

    service_time : int | None = 0
    served_by : int | None = None

    rejected : bool = False

    def __init__(self, time : int, given_id : int) -> None:
        self.birth_time = time
        self.id = given_id

    def reject(self, time : int) -> None:
        """Used to set internal attributes to represent a customer has been rejected

        @parameters
            time - the global time of rejection
        """
        self.rejected = True
        self.service_time = None
        self.served_by = None
        self.death_time = time
        logging.info("Rejecting and killing customer %s", repr(self))
    
    def serve(self, server : 'UniversalServer', time: int) -> None:
        """Used to set interal attributes to represent currently being served

        @parameters:
            server -- the server object which is serving the customer
            time -- the global time a cutomer beings to be served
        """
        self.served_by = server.id
        self.service_time = time
        logging.info("Serving customer %s with server: %s", repr(self), repr(server))

    def kill(self, time : int) -> None:
        """Used to set internal parameters to represent a cutomer has
        been completed an no longer needs to be considered

        @parameters:
            time -- the global time a customer is finished with
        """
        self.death_time = time
        logging.info("Killing customer %s", repr(self))

    def __str__(self) -> str:
        return f"Customer ID: {self.id} " \
            f"Birth: {self.birth_time}, Rejected: {self.rejected}, " \
            f"Server ID: {self.served_by}, " \
            f"Service Time: {self.service_time}, " \
            f"Death: {self.death_time}" 

    def __repr__(self) -> str:
        return f"CustomerObject({self.id}," \
            f"{self.birth_time})"

    def to_csv(self) -> str:
        """Represent the current state of the customer in CSV format:
        the structure is as follows:
        ID,Priority[not used for this simulation],Birth Time,Death Time,
        Rejected,ServerID(None if rejected), Service Time(None if rejected),
        Death Time
        """
        return f"{self.id},0,{self.birth_time}," \
        f"{self.rejected},{self.served_by},{self.service_time},{self.death_time}"

class UniversalServer:
    """A Class representing all servers within the MMCC queue
    
    @attributes:
        id      -- the unique server id
        idle    -- whether the server is idle
        current_customer    -- The current customer object being served
        serve_time      -- the total time spent serving customers
        idle_time       -- the total time spent idle
        last_update_time   -- the last time since update()
        cust_served     -- the ammount of customers served
        rands           -- the list of random numbers used for service time
    """
    id : int
    idle : bool = True
    current_customer : Customer | None = None

    serve_time : int = 0
    idle_time : int = 0
    last_update_time : int = 0
    cust_served : int = 0

    rands = []

    def __init__(self, given_id : int) -> None:
        self.id = given_id

    def set_serve_time(self, rands : List[int]):
        """Set the given random array to the servers internal memory.
        The memory is removed throughout the runtime of the program.

        @parameters:
            rands -- The time steps required to complete each service 
        """
        self.rands = rands  # Python passes arrays by reference so this is just
                            # for ease of access / code clarity
        logging.info("Set server: {%s random string", repr(self))

    def serve(self, customer : Customer, time : int) -> int:
        """Set a server to serve a customer

        @parameters:
            customer -- The customer to be served by the server
            time -- The time of the service start

        @returns:
            The time thaat the server completes its service
        """
        self.update(time)
        time_to_serve = self.rands.pop(0)
        customer.serve(self, time_to_serve)
        self.current_customer = customer
        self.idle = False
        self.cust_served += 1
        string = f"Assigned server: {repr(self)} customer: {repr(customer)}. Time to serve: " \
                f"{time_to_serve}, finish time: {time + time_to_serve}"
        logging.info(string)

        return time_to_serve + time

    def finish_serve(self, time : int) -> None:
        """Kill the current customer and clean-up interal attributes at
        time of completed service

        @parameters:
            time -- the simulation time of the completed service
        """
        logging.info("Completed server: %s service of customer: %s",
                     repr(self),
                     repr(self.current_customer))
        self.current_customer.kill(time)
        self.current_customer = None
        self.update(time)
        self.idle = True

    def update(self, time : int) -> None:
        """Update time dependent attributes when changing idle state

        @parameters:
            time -- the simulation time of the update.
        """
        logging.info("Updating server: %s internal attributes", repr(self))
        if self.idle:
            self.idle_time += (time-self.last_update_time)
            self.last_update_time = time
            return
        self.serve_time += (time-self.last_update_time)
        self.last_update_time = time

    def __str__(self) -> str:
        return f"Server ID: {self.id} " \
            f"Idle: {self.idle}, Idle time: {self.idle_time}, " \
            f"Current Customer: {repr(self.current_customer)}, " \
            f"Customers Served: {self.cust_served}, " \
            f"Total service time: {self.serve_time}"

    def __repr__(self) -> str:
        return f"UniversalServer({self.id})"

    def to_csv(self) -> str:
        """Convert the server information into csv format"""
        return f"{self.id},0,{self.idle},{self.idle_time},{self.cust_served}," \
            f"{self.serve_time}"

class MMCCSimulation:
    """The MMCCSimulation body. A simulation for a service and customers,
    where once all services are filled, customers are rejected completely.
    Used for Modelling and Simulation CA1, assignment 1.

    @attributes:
        customer_count -- The number of customers the simulation runs for
        server_count -- The number of servers for the simulation
        service_avg -- The exponential-average service time
        arrival_rate -- The exponential-average customer arrival time
        rand_arrays -- Arrays containing the random values above.
                    -- Note, as apposed to server-rands, this does not change
                    -- at run time.
        servers -- The list of all active servers
        customers -- The list of all Alive and Killed customers
        customer_birth_times -- The times a customer is born
        next_events -- An array of all future staged event timings
    """
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
                 arrival_rate: float,
                 start = round(timeMod.time())) -> None:
        logging.info("Initialising simulation")
        self.customer_count = customer_count
        self.server_count = server_count
        self.service_avg = service_avg
        self.arrival_rate = arrival_rate
        self.start_time = start

        self.next_events = []
        self.servers = []
        self.customers = []
        self.time = 0

        self.set_rand_array()
        self.create_servers()
        
        for array in self.rand_arrays:
            logging.info("Rands: %s", str(array))
 

    def set_rand_array(self) -> None:
        """Set the random arrays to the interal attributes of the class"""
        self.rand_arrays = []
        logging.info("Setting random arrays for the simulation")
        # Generate Customers

        self.rand_arrays.append(discrete_exponential(1/self.arrival_rate, self.customer_count))

        self.customer_birth_times = self.rand_arrays[0].copy()
        self.next_events.append(self.customer_birth_times.pop(0))
            # Add the first birth of customer to the event list
        self.produce_server_rand_arrays()
        logging.info("Finished random arrays for the simulation")

    def produce_server_rand_arrays(self):
        """Create the server random arrays values"""
        for _ in range(self.server_count):
            self.rand_arrays.append(discrete_exponential(self.service_avg, self.customer_count))

        logging.info("Finished setting server random arrays")

    def create_servers(self) -> None:
        """Initialise all the servers for the class"""
        self.servers = [UniversalServer(x) for x in range(self.server_count)]
        for i, serv in enumerate(self.servers):
            serv.rands = self.rand_arrays[i+1].copy()
            self.next_events.append(999999999)
            logging.info("Finished initialising server: %s", repr(serv))

    def birth_customer(self, priority : int | None = None) -> None:
        """Initialise a customer at a given time. Only produced one instance
        as it is only run when a customer 'joins' the simulation Priority included as interface"""
        customer = Customer(self.time, len(self.customers))
        self.customers.append(customer)
        
        logging.info("Created customer: %s", repr(customer))
        # As we don't have a queue, if every server is full, the customer is turned away
        self.assign_customer(customer)
        return customer

    def assign_customer(self, customer : Customer) -> bool:
        """Assign a customer to a server. The current method choses the server
        with the lowest ID. If no available server is found, kills the customer

        @parameters:
            customer -- The customer to be served
        """
        available_servers = self.get_available_servers(customer)

        if len(available_servers) == 0:
            logging.info("No available servers at this time for customer %s", repr(customer))
            customer.reject(self.time)
            return False

        # The manner of choosing which server to pick can be assigned here, but
        # for now, we'll just go for the lowest ID
        logging.info("Available servers found for customer %s", repr(customer))
        chosen_serv = available_servers[0]
        next_event_time = chosen_serv.serve(customer, self.time)
        self.next_events[self.servers.index(chosen_serv)+1] = next_event_time
        return True

    def get_available_servers(self, customer : Customer = None)-> List[UniversalServer]:
        """Produce a list of all available servers.

        @parameters:
            customer -- the Customer to be served (included for interface reasons)

        @returns:
            A list of all the available server objects
        """
        return [serv for serv in self.servers if serv.idle]

    def jump_next_event(self) -> List[int]:
        """Move the simulation time to the next staged event. Probably less
        efficient than a for loop, but hey ho.

        @returns:
            A list of all the indices of staged events that has been jumped to
        """
        next_time = min(self.next_events)
        logging.info("Moving time forward: %s -> %s", self.time, next_time)
        self.time = next_time

        staged_events : List[int] = []
        for i, event_time in enumerate(self.next_events):
            if event_time == self.time:
                staged_events.append(i)

        logging.info("Staged event(s) found at index %s", str(staged_events))
        return staged_events

    def run(self):
        """Run the MMCC Simulation with the given parameters
        """
        logging.info("Running simulation")
        # While there are still staged events...
        while min(self.next_events) < 999999999:
            staged_events = self.jump_next_event()

            if staged_events[0] == 0:
                self.birth_customer()

                if self.customer_birth_times:
                    self.next_events[0] = self.time + self.customer_birth_times.pop(0)
                else:
                    self.next_events[0] = 999999999

            for index in staged_events:
                if index == 0:
                    continue

                self.servers[index-1].finish_serve(self.time)
                self.next_events[index] = 999999999

        for server in self.servers:
            server.update(self.time)
            # Update to include end of service stint.

        logging.info("Simulation Completed:")
        logging.info("Final states:")
        logging.info("Simulation time: %s", self.time)
        logging.info("Customers:")
        for cust in self.customers:
            logging.info(str(cust))
        
        logging.info("Servers:")
        for serv in self.servers:
            logging.info(str(serv))

        logging.info("Loss rate: %s", str(self.find_loss_rate()))
        return
    
    def find_loss_rate(self) -> float:
        """Get the proprtion of customers lost"""
        total_lost = 0
        for cust in self.customers:
            if cust.rejected:
                total_lost += 1

        return total_lost / (len(self.customers) - self.server_count)

    def output_results(self, dir_path : str = "../results/no-rank/"):
        """Output the results of the simulation to a given file path. The given
        path must contain two directories, 'customers' and 'servers'. The file outputs
        are in csv formats.

        @parameters:
            dir_path -- The Directory to output the files to

        @outputs:
            Two CSV files {time_since_unix_epoch}.csv in servers and customers
            containing the CSV representations of all servers andd customers respectively
        """
        file_name = dir_path + f"customers/{self.start_time}.csv"
        with open(file_name, "w", encoding='utf-8') as file:
            for cust in self.customers:
                file.write(cust.to_csv() + "\n")

        file_name = dir_path + f"servers/{self.start_time}.csv"
        with open(file_name, "w", encoding='utf-8') as file:
            for serv in self.servers:
                file.write(serv.to_csv() + "\n")

def discrete_exponential(avg_time : float, quant : int = 1) -> List[int]:
    return list(np.random.geometric(1/avg_time, size=quant))

def poisson_process(avg_time : int, quant : int = 1) -> List[int]:
    return list(np.random.poisson(avg_time, size=quant))

def main():
    """The main body of the program, called if program run as __main__"""
    start_time = round(timeMod.time())
    logging.basicConfig(filename= f'../logs/no-rank/{start_time}.log',
                        encoding='utf-8',
                        level=logging.DEBUG)
    sim : MMCCSimulation = MMCCSimulation(
        15,
        4,
        100,
        1/10,
        start = start_time
    )
    print(sim.customer_birth_times)
    sim.run()
    sim.output_results()
    print(sim.find_loss_rate())
    return

if __name__ == "__main__":
    main()
