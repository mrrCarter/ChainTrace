module transactiontracing_tb ();
reg clk;
reg [30:0] time_stamp;
reg in;
reg [1:0]method_field;
reg [19:0]value;
reg new_wallet;
wire [6:0] confidence_score;
  wire [6:0] m, i, v, p;

  transactiontracing uut(.clk(clk),.time_stamp(time_stamp),.in(in),.method_field(method_field),.value(value),.new_wallet(new_wallet),.confidence_score(confidence_score), .m(m),.i(i),.v(v),.p(p));

initial begin
    //initial transaction
    clk = 0;
    time_stamp = 31'b0000000000000000000000000000000;
    in = 0;
    method_field = 2'b10;
    value = 20'b00000000000000000000;
    new_wallet = 1;
 
    //1st transaction
    #25
    time_stamp = 31'b1100011001111011111011000011111;
    in = 1;
    method_field = 2'b10;
    value = 20'b00000000100001111111;
    new_wallet = 0;
  $display("Confidence score = %d", confidence_score);

    //2nd transaction
    #20
    time_stamp = 31'b1100011001111100001111000110011;
    in = 1;
    method_field = 2'b10;
    value = 20'b11000010100001111111;
    new_wallet = 0;
  $display("Confidence score = %d", confidence_score);  

    //3rd transaction
    #20
    time_stamp = 31'b1100011010000001110010111001111;
    in = 1;
    method_field = 2'b10;
    value = 20'b01101100110011001000;
    new_wallet = 0;
  $display("Confidence score = %d", confidence_score);  

    //4th transaction
    #20
    time_stamp = 31'b1100011010000001111000010001011;
    in = 0;
    method_field = 2'b10;
    value = 20'b01010000110101110101;
    new_wallet = 0;
  $display("Confidence score = %d", confidence_score);  

    //5th transaction
    #20
    time_stamp = 31'b1100011010110000001110010010011;
    in = 1;
    method_field = 2'b10;
    value = 20'b00010010101101010011;
    new_wallet = 0;
  $display("Confidence score = %d", confidence_score);  

    //6th transaction
    #20
    time_stamp = 31'b1100011010110000001110010010011;
    in = 1;
    method_field = 2'b10;
    value = 20'b10010000110000110000;
    new_wallet = 0;
  $display("Confidence score = %d", confidence_score);  

    //7th transaction
    #20
    time_stamp = 31'b1100011010110000001111111100111;
    in = 1;
    method_field = 2'b10;
    value = 20'b11000000100011111100;
    new_wallet = 0;
  $display("Confidence score = %d", confidence_score);  

    //8th transaction
    #20
    time_stamp = 31'b1100011011010011000110000110011;
    in = 1;
    method_field = 2'b10;
    value = 20'b01010000110010111011;
    new_wallet = 0;
  $display("Confidence score = %d", confidence_score);  

    //9th transaction
    #20
    time_stamp = 31'b1100011011010011000110001001011;
    in = 1;
    method_field = 2'b10;
    value = 20'b00010000100111110000;
    new_wallet = 0;
  $display("Confidence score = %d", confidence_score);  

    //10th transaction
    #20
    time_stamp = 31'b1100011011010011001001010010011;
    in = 1;
    method_field = 2'b10;
    value = 20'b01100000100001011101;
    new_wallet = 0;
  $display("Confidence score = %d", confidence_score);  

    //11th transaction
    #20
    time_stamp = 31'b1100011011010101111001111101011;
    in = 1;
    method_field = 2'b10;
    value = 20'b01100000100010011000;
    new_wallet = 0;
  $display("Confidence score = %d", confidence_score);  

    //12th transaction
    #20
    time_stamp = 31'b1100011011010101111100101110011;
    in = 1;
    method_field = 2'b10;
    value = 20'b11100000100000110100;
    new_wallet = 0;
  $display("Confidence score = %d", confidence_score);  


    //13th transaction
    #20
    time_stamp = 31'b1100011011010101111101011110011;
    in = 1;
    method_field = 2'b10;
    value = 20'b11100000101110111000;
    new_wallet = 0;
  $display("Confidence score = %d", confidence_score);  

    //14th transaction
    #20
    time_stamp = 31'b1100011011011000011111000110011;
    in = 1;
    method_field = 2'b10;
    value = 20'b11101100110001001110;
    new_wallet = 1;

  #20 $display("Confidence score = %d , m = %d, i = %d, v = %d, p = %d", confidence_score, m, i, v, p);  
 
 
   #20
    time_stamp = 31'b1100011001111011111011000011111;
    in = 1;
    method_field = 2'b11;
    value = 20'b00000000000000011111;
    new_wallet = 0;
  $display("New Wallet: Confidence score = %d", confidence_score);

    //2nd transaction
    #20
    time_stamp = 31'b1100011001111100001111000110011;
    in = 0;
    method_field = 2'b11;
    value = 20'b00000000000000011111;
    new_wallet = 0;
  $display("Confidence score = %d", confidence_score);  

    //3rd transaction
    #20
    time_stamp = 31'b1100011010000001110010111001111;
    in = 1;
    method_field = 2'b11;
    value = 20'b00000000000000001000;
    new_wallet = 0;
  $display("Confidence score = %d", confidence_score);  

    //4th transaction
    #20
    time_stamp = 31'b1100011010000001111000010001011;
    in = 0;
    method_field = 2'b11;
    value = 20'b00000000000000110101;
    new_wallet = 0;
  $display("Confidence score = %d", confidence_score);  

    //5th transaction
    #20
    time_stamp = 31'b1100011010110000001110010010011;
    in = 1;
    method_field = 2'b11;
    value = 20'b00000000000000010011;
    new_wallet = 0;
  $display("Confidence score = %d", confidence_score);  

    //6th transaction
    #20
    time_stamp = 31'b1100011010110000001110010010011;
    in = 0;
    method_field = 2'b11;
    value = 20'b00000000000000110000;
    new_wallet = 0;
  $display("Confidence score = %d", confidence_score);  

    //7th transaction
    #20
    time_stamp = 31'b1100011010110000001111111100111;
    in = 1;
    method_field = 2'b11;
    value = 20'b00000000000000001100;
    new_wallet = 0;
  $display("Confidence score = %d", confidence_score);  

    //8th transaction
    #20
    time_stamp = 31'b1100011011010011000110000110011;
    in = 0;
    method_field = 2'b11;
    value = 20'b00000000000010111011;
    new_wallet = 0;
  $display("Confidence score = %d", confidence_score);  

    //9th transaction
    #20
    time_stamp = 31'b1100011011010011000110001001011;
    in = 1;
    method_field = 2'b11;
    value = 20'b00000000000011110000;
    new_wallet = 0;
  $display("Confidence score = %d", confidence_score);  

    //10th transaction
    #20
    time_stamp = 31'b1100011011010011001001010010011;
    in = 0;
    method_field = 2'b11;
    value = 20'b00000000000001011101;
    new_wallet = 0;
  $display("Confidence score = %d", confidence_score);  

    //11th transaction
    #20
    time_stamp = 31'b1100011011010101111001111101011;
    in = 1;
    method_field = 2'b11;
    value = 20'b00000000000000011000;
    new_wallet = 0;
  $display("Confidence score = %d", confidence_score);  

    //12th transaction
    #20
    time_stamp = 31'b1100011011010101111100101110011;
    in = 0;
    method_field = 2'b11;
    value = 20'b00000000000000110100;
    new_wallet = 0;
  $display("Confidence score = %d", confidence_score);  


    //13th transaction
    #20
    time_stamp = 31'b1100011011010101111101011110011;
    in = 1;
    method_field = 2'b11;
    value = 20'b00000000101110111000;
    new_wallet = 0;
  $display("Confidence score = %d", confidence_score);  

    //14th transaction
    #20
    time_stamp = 31'b1100011011011000011111000110011;
    in = 0;
    method_field = 2'b11;
    value = 20'b00000000000001001110;
    new_wallet = 1;

  #20 $display("Confidence score = %d , m = %d, i = %d, v = %d, p = %d", confidence_score, m, i, v, p);  
 

end

always begin
    #20 clk = ~clk;
end

endmodule
