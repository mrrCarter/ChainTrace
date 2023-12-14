# ChainTrace

## Overview
ChainTrace is an innovative tool designed for real-time analysis of blockchain transactions. Utilizing FPGA's computational capabilities, it aims to trace transactions, identify suspicious patterns, and flag potential endpoints in cryptocurrency networks.

Here is a link to our demo video: 

## Features
- Real-time data ingestion from blockchain APIs
- Advanced transaction tracing using FPGA
- Pattern recognition to detect suspicious activities
- Endpoint detection for potential illicit cash-out points

## Running This Project
1. Download all files in our verilog_code and FPGA_constraints folders. Create a new Vivado project with the Nexys A7 100T as the selected board, and add all the files as design sources, the constraint file as a constraint, and the testbench file as a simulation source. Program the FPGA board by connecting the board to your PC via microUSB-to-USB, Synthesize, Implement, Generating bitstream, and finally, program the device.
2. Download the python files and add a config.py file. Go to etherscan and generate an API key. Assign the api key value to API_KEY. Then run the project by running the python code and giving an ethereum wallet id as an input.

## Code
1. TRACING ALGORITHM --> Takes in data from ethereum transaction objects and uses the values inside the objects to calculate a confidence score (0-100) of how likely that wallet is to be assoicated with a scam.
2. UART CONNECTION --> Establishes a connection with the python script in the PC and the algorithm on the fpga board using the UART protocol. Takes in the data using a FIFO and stores the data to be processed by the algorithm. This part of our code was implemented using the code from FPGAdude/Digital-Design/UART and changed to meet the specifications of our project.
4. PYTHON SCRIPT --> The python code communicates with the Etherscan API to get the transaction data required for the algorithm to work. It then parses this data into a minimized version of itself and starts a serial communication with the port that the FPGA is connected to.

## Team
- Carter: carther@bu.edu
- Anna: afinn12@bu.edu
- Leo: leophung@bu.edu
- Kursat: kalyamac@bu.edu

