`timescale 1ns / 1ps

module uart_test(
    input clk_100MHz,       // basys 3 FPGA clock signal
    input reset,            // btnR    
    input rx,               // USB-RS232 Rx
    output tx,              // USB-RS232 Tx
    output [3:0] an,        // 7 segment display digits
    output [0:6] seg,       // 7 segment display segments
    output [7:0] LED        // data byte display
    );
    
    // Connection Signals
    wire rx_full, rx_empty;
    wire [7:0] rec_data, rec_data1;
    reg send_data;          // Trigger to send data

    // Special ASCII character (e.g., newline 0x0A)
    parameter SPECIAL_CHAR = 8'h26;

    // Complete UART Core
    uart_top UART_UNIT
        (
            .clk_100MHz(clk_100MHz),
            .reset(reset),
            .read_uart(send_data),
            .write_uart(send_data),
            .rx(rx),
            .write_data(rec_data1),
            .rx_full(rx_full),
            .rx_empty(rx_empty),
            .read_data(rec_data),
            .tx(tx)
        );
    
    // Logic to detect the special character and trigger data send
    always @(posedge clk_100MHz or posedge reset) begin
        if (reset) begin
            send_data <= 0;
        end else begin
            if (!rx_empty && rec_data == SPECIAL_CHAR) begin
                send_data <= 1;
            end else begin
                send_data <= 0;
            end
        end
    end

    // Signal Logic    
    assign rec_data1 = rec_data + 1;    // add 1 to ascii value of received data (to transmit)
    
    // Output Logic
    assign LED = rec_data;              // data byte received displayed on LEDs
    assign an = 4'b1110;                // using only one 7 segment digit 
    assign seg = {~rx_full, 2'b11, ~rx_empty, 3'b111};
endmodule
