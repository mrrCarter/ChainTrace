`timescale 1ns / 1ps

module uart_top
    #(
        parameter   DBITS = 8,          // number of data bits in a word
                    SB_TICK = 16,       // number of stop bit / oversampling ticks
                    BR_LIMIT = 651,     // baud rate generator counter limit
                    BR_BITS = 10,       // number of baud rate generator counter bits
                    FIFO_EXP = 3        // exponent for number of FIFO addresses (2^2 = 4)
    )
    (
        input clk_100MHz,               // FPGA clock
        input reset,                    // reset
        input read_uart,                // button
        input rx,                       // serial data in
        input [DBITS*(2**FIFO_EXP)-1:0] write_data, // data from Tx FIFO
        output rx_full,                 // do not write data to FIFO
        output rx_empty,                // no data to read from FIFO
        output tx,                      // serial data out
        output [DBITS*(2**FIFO_EXP)-1:0] read_data   // data to Rx FIFO
    );
    
    // Connection Signals
    wire tick;                          // sample tick from baud rate generator
    wire rx_done_tick;                  // data word received
    wire tx_done_tick;                  // data transmission complete
    wire tx_empty;                      // Tx FIFO has no data to transmit
    wire tx_fifo_not_empty;             // Tx FIFO contains data to transmit
    wire [DBITS-1:0] tx_fifo_out;       // from Tx FIFO to UART transmitter
    wire [DBITS-1:0] rx_data_out;       // from UART receiver to Rx FIFO
    
    // Instantiate Modules for UART Core
    baud_rate_generator 
        #(
            .M(BR_LIMIT), 
            .N(BR_BITS)
         ) 
        BAUD_RATE_GEN   
        (
            .clk_100MHz(clk_100MHz), 
            .reset(reset),
            .tick(tick)
         );
    
    uart_receiver
        #(
            .DBITS(DBITS),
            .SB_TICK(SB_TICK)
         )
         UART_RX_UNIT
         (
            .clk_100MHz(clk_100MHz),
            .reset(reset),
            .rx(rx),
            .sample_tick(tick),
            .data_ready(rx_done_tick),
            .data_out(rx_data_out)
         );
    
    fifo
        #(
            .DATA_SIZE(DBITS),
            .ADDR_SPACE_EXP(FIFO_EXP)
         )
         FIFO_RX_UNIT
         (
            .clk_100Mhz(clk_100MHz),
            .reset(reset),
            .write_to_fifo(rx_done_tick),
	        .read_from_fifo(rx_full),
	        .write_data_in(rx_data_out),
	        .read_data_out(read_data),
	        .empty(rx_empty),
	        .full(rx_full)            
	      );
	   
	wire tx_read_fifo;   
	   
    larger_fifo
        #(
            .DATA_SIZE(DBITS),
            .ADDR_SPACE_EXP(FIFO_EXP)
         )
         FIFO_TX_UNIT
         (
            .clk_100MHz(clk_100MHz),
            .reset(reset),
		    .write_to_fifo(read_uart),    //load the 64 bits when button pressed
	        .read_from_fifo(tx_read_fifo),    //whenever not transmitting, send to transmitter
	        .write_data_in(write_data),   //put 64 bits in memory
	        .read_data_out(tx_fifo_out),  //ascii to output
	        .empty(tx_empty)  //output for display
	      );
	      
        assign tx_read_fifo = tx_done_tick;	 
             
    uart_transmitter
        #(
            .DBITS(DBITS),
            .SB_TICK(SB_TICK)
         )
         UART_TX_UNIT
         (
            .clk_100MHz(clk_100MHz),
            .reset(reset),
            .tx_start(tx_fifo_not_empty),
            .sample_tick(tick),
            .data_in(tx_fifo_out),
            .tx_done(tx_done_tick),
            .tx(tx)
         );
    
    
    // Signal Logic
    assign tx_fifo_not_empty = ~tx_empty;
  
endmodule