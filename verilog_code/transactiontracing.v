module transactiontracing (
input  clk,
input [30:0] time_stamp,
input in,
input [1:0]method_field,
input [19:0]value,
input new_wallet,
  output reg [6:0] confidence_score,
  output reg [6:0] m, i, v, p
    );
   
   reg [6:0] moving_method;
   reg method_indicator;
   reg [6:0] moving_in;
   reg [63:0] moving_avg_value;
   reg [9:0] start_time, end_time;
   reg [6:0] total_running_sum;
   reg [6:0] m, i, v, p;



   
parameter  tether = 2'b00, monero = 2'b01, other_method = 2'b10;


//initialize
initial begin
    moving_method = 0;
    method_indicator=0;
    total_running_sum =0;
    moving_in=0;
end


//method
always @(posedge clk) begin
    case (method_field)
    tether: begin
        method_indicator <= 1;
    end
    monero: begin
        method_indicator <= 1;
    end
    other_method: begin
        moving_method <= moving_method+1;
    end
    endcase
end


//in/out ratio
always @(posedge clk) begin
    case (in)
    1: begin
        moving_in<=moving_in+1;
    end
    endcase
end


 //value
  // value threshold each degree
    reg [13:0]value_degree1 = 14'b10011100010000;
    reg [15:0]value_degree2 = 16'b1100001101010000;
    reg [16:0]value_degree3 = 17'b11000011010100000;
    reg [17:0]value_degree4 = 18'b110000110101000000;
    reg [18:0]value_degree5 = 19'b1100001101010000000;
    reg [2:0] value_indicator;

always @(posedge clk) begin
    moving_avg_value <= moving_avg_value + value;
    end
   

//period and calculate confidence score
always @(posedge clk) begin
  if (new_wallet == 0) begin
    end_time <= time_stamp;
    total_running_sum <= total_running_sum +1;
  end
end
 
 
 always @(posedge clk) begin
        if(method_indicator == 1 || 100*(moving_method/total_running_sum) >= 15)
            m <= 15;
        else if (100*(moving_method/total_running_sum) >= 10)
            m <= 10;
        else if (100*(moving_method/total_running_sum) >= 5)
            m <= 5;
        else
            m<=0;
 end
       


//inout ratio
  always @(posedge clk) begin
        if(100*(moving_in/total_running_sum) >= 95 || 100*(moving_in/total_running_sum) <= 5 )
            i <= 35;
        else if (100*(moving_in/total_running_sum) >= 90 || 100*(moving_in/total_running_sum) <= 10)
            i <= 30;
        else if (100*(moving_in/total_running_sum) >= 85|| 100*(moving_in/total_running_sum) <= 15 )
            i <= 25;
        else if (100*(moving_in/total_running_sum) >= 80 || 100*(moving_in/total_running_sum) <= 20 )
            i <= 20;
        else if (100*(moving_in/total_running_sum) >= 75 || 100*(moving_in/total_running_sum) <= 25 )
            i <= 15;
        else if (100*(moving_in/total_running_sum) >= 70 || 100*(moving_in/total_running_sum) <= 30)
            i <= 10;
        else
            i<=0;
  end



//value
  always @(posedge clk) begin
        if(moving_avg_value/total_running_sum >= value_degree5)
            v <= 20;
        else if (moving_avg_value/total_running_sum >= value_degree4)
            v <= 17;
        else if (moving_avg_value/total_running_sum >= value_degree3)
            v <= 14;
        else if (moving_avg_value/total_running_sum >= value_degree2)
            v <= 10;
        else if (moving_avg_value/total_running_sum >= value_degree1)
            v <= 7;
        else
            v <=0;
  end

//frequency
  always @(posedge clk) begin
        if((start_time-end_time)/total_running_sum >= 3600)
            p <= 30;
        else if ((start_time-end_time)/total_running_sum >= 1800)
            p <= 25;
        else if ((start_time-end_time)/total_running_sum >= 720)
            p <= 20;
        else if ((start_time-end_time)/total_running_sum >= 60)
            p <= 15;
        else if ((start_time-end_time)/total_running_sum >= 1)
            p <= 5;
        else
            p <=0;
  end
 
 
 
   always @(posedge clk)begin
     if (new_wallet == 1) begin
     method_indicator <= 0;
     moving_method <=0;
   end
   end
 
  always @(posedge clk)begin
    if (new_wallet == 1) begin
     moving_avg_value <=0;
   end
  end
 
  always @(posedge clk)begin
    if (new_wallet == 1) begin
     moving_in <=0;
   end
  end
 
   always @(posedge clk)begin
     if (new_wallet == 1) begin
     start_time <=time_stamp;
   end  
   end
 
   always @(posedge clk)begin
     if (new_wallet == 1) begin
     total_running_sum<=0;
   end
   end
       
 
 
   always @(m, v, i , p)begin
    confidence_score <= m+i+v+p;
   end
 
           
       

endmodule
