# MMCCSimulations

A repository containing the source code and report for an M/M/C/C Queue, and M1-M2/M/C/C Queue implementation in Python. This repository is considered as the sumbission for University of Exeter's ECMM424 Computer Modelling and Simulation Continuous Assessment.

## Directory Structure

**Report.pdf** contains the report of the program, including a code review, tests and validation, and the results from various exercises. Additionally, within the foreword,
a link to a YouTube video is included, which demontrates the runtime of the program, as well as a overall project presentation.

**/results/** contains the CSV files of the running of the simulation. Such data includes each customer's interal attributes and each server's internal attributes. By default,
this directory includes various validation CSVs and example CSVs, as well as structure CSVs to convey the meaning of each column.

**/logs/** contains the .log files for each runtime of the individual Queue simulations. By default, the .log files are only created when directly accessing the MMCCSimulation.py or M1M2MCCSimulation.py files, as including loggin during the main.py program would produce unnecessary data.

**/src/** contains the executable .py files for the program.

## /src/ Files

**main.py** is an executable and the main point of access for the program. It invokes a menu allowing for the application to compute and display various graphs, as well as find solutions for the various exercises included in the coursework specification

**MMCCSimulation.py** is a python file including all classes related to the M/M/C/C queue simulation. While not intended to be a point of access, executing the file completes an example M/M/C/C queue, with logging included.

**mmcc_val.py** is a python files which includes the algorithmic validation for the M/M/C/C queue simulation. The file is used within the main program and should not be executed by itself

**M1M2MCCSimulation.py** is a python file including all classes related to the M1-M2/M/C/C queue simulation. The file heavily relies on inheritance from the MMCCSimulation.py file. While not intended to be a point of acces, executing the file completes and example M1-M2/M/C/C queue simulation, with logging included.

**m1m2mcc_application.py** is a python file which contains various functions to apply the M1-M2/M/C/C queue simulation. It is not a point of access for the source code.
