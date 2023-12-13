module sevenseg(
    input clk,               // Nexys A7 clock
    input [6:0] confidence_score,          // Temp data from i2c master
    output reg [6:0] SEG,           // 7 Segments of Displays
    output reg [3:0] NAN = 4'hF,    // 4 Anodes of 8 turned OFF
    output reg [3:0] AN             // 4 Anodes of 8 to display Temp
    );
   
    // Binary to BCD conversion of temperature data
    wire [3:0] tens, ones;
    assign tens = confidence_score / 10;           // Tens value of temp data
    assign ones = confidence_score % 10;           // Ones value of temp data
   
   
 
   
    // To select each digit in turn
    reg [1:0] anode_select;         // 2 bit counter for selecting each of 4 digits
    reg [16:0] anode_timer;         // counter for digit refresh
   
    // Logic for controlling digit select and digit timer
  always @(posedge clk) begin
        // 1ms x 4 displays = 4ms refresh period
        if(anode_timer == 99_999) begin         // The period of 100MHz clock is 10ns (1/100,000,000 seconds)
            anode_timer <= 0;                   // 10ns x 100,000 = 1ms
            anode_select <=  anode_select + 1;
        end
        else
            anode_timer <=  anode_timer + 1;
    end
   
    // Logic for driving the 4 bit anode output based on digit select
    always @(anode_select) begin
        case(anode_select)
            2'b00 : AN = 4'b1110;   // Turn on ones digit
            2'b01 : AN = 4'b1101;   // Turn on tens digit
            2'b10 : AN = 4'b1011;   // Turn on hundreds digit
            2'b11 : AN = 4'b0111;   // Turn on thousands digit
        endcase
    end
   
    always @*
        case(anode_select)               
            2'b00 : begin       // TEMPERATURE ONES DIGIT
                        case(ones)
                            4'b0000 : SEG = 7'b0000001;
                            4'b0001 : SEG = 7'b1001111;
                            4'b0010 : SEG = 7'b0010010;
                            4'b0011 : SEG = 7'b0000110;
                            4'b0100 : SEG = 7'b1001100;
                            4'b0101 : SEG = 7'b0100100;
                            4'b0110 : SEG = 7'b0100000;
                            4'b0111 : SEG = 7'b0001111;
                            4'b1000 : SEG = 7'b0000000;
                            4'b1001 : SEG = 7'b0001100;
                        endcase
                    end
                   
            2'b01 : begin       // TEMPERATURE TENS DIGIT
                        case(tens)
                            4'b0000 : SEG = 7'b0000001;
                            4'b0001 : SEG = 7'b1001111;
                            4'b0010 : SEG = 7'b0010010;
                            4'b0011 : SEG = 7'b0000110;
                            4'b0100 : SEG =  7'b1001100;
                            4'b0101 : SEG = 7'b0100100;
                            4'b0110 : SEG = 7'b0100000;
                            4'b0111 : SEG = 7'b0001111;
                            4'b1000 : SEG = 7'b0000000;
                            4'b1001 : SEG = 7'b0001100;
                        endcase
                    end
            default: SEG = 7'b1111111;
        endcase
   
endmodule
