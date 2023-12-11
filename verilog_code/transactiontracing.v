`timescale 1ns / 1ps

module transactiontracing #(parameter n =1)(
input  clk,
input [9:0] time_stamp,
input in,
input [1:0]method_field,
input [29:0]value,
input new_wallet;
output reg [6:0] confidence_score
    );
   
   reg [6:0] moving_method;
   reg method_indicator;

 
   reg [6:0] moving_in;

   reg [63:0] moving_avg_value;

   reg [9:0] start_time, end_time;
   reg [6:0] total_running_sum;

   reg [6:0] inoutratio; 
//period and calculate confidence score
always @(posedge clk) begin
    if (new_wallet == 1){
        //what if it's the first transaction?
        //divison math is different
        //decimal math is different


        if(method_indicator == 1 || 100*(moving_method/total_running_sum) >= 15){
            m <= 15;
        }else if (100*(moving_method/total_running_sum) >= 10){
            m <= 10;
        }else if (100*(moving_method/total_running_sum) >= 5){
            m <= 5;
        }else{
            m<=0;
        }



        if(100*(moving_in/total_running_sum) >= 95 || 100*(moving_in/total_running_sum) <= 5 ){
            i <= 35;
        }else if (100*(moving_in/total_running_sum) >= 90 || 100*(moving_in/total_running_sum) <= 10){
            i <= 30;
        }else if (100*(moving_in/total_running_sum) >= 85|| 100*(moving_in/total_running_sum) <= 15 ){
            i <= 25;
        }else if (100*(moving_in/total_running_sum) >= 80 || 100*(moving_in/total_running_sum) <= 20 ){
            i <= 20;
        }else if (100*(moving_in/total_running_sum) >= 75 || 100*(moving_in/total_running_sum) <= 25 ){
            i <= 15;
        }else if (100*(moving_in/total_running_sum) >= 70 || 100*(moving_in/total_running_sum) <= 30){
            i <= 10;
        }else{
            m<=0;
        }


        if(moving_avg_value/total_running_sum >= value_degree5){
            v <= 20;
        }else if (moving_avg_value/total_running_sum >= value_degree4){
            v <= 17;
        }else if (moving_avg_value/total_running_sum >= value_degree3){
            v <= 14;
        }else if (moving_avg_value/total_running_sum >= value_degree2){
            v <= 10;
        }else if (moving_avg_value/total_running_sum >= value_degree1){
            v <= 7;
        }else{
            v <=0;
        }

        if((start_time-end_time)/total_running_sum >= 3600){
            p <= 30;
        }else if ((start_time-end_time)/total_running_sum >= 1800){
            p <= 25;
        }else if ((start_time-end_time)/total_running_sum >= 720){
            p <= 20;
        }else if ((start_time-end_time)/total_running_sum >= 60){
            p <= 15;
        }else if ((start_time-end_time)/total_running_sum >= 1){
            p <= 5;
        }else{
            p <=0;
        }



    
    }else{
        end_time <= time_stamp;
    }
    total_running_sum <= total_running_sum +1;
    end

   always @(m)begin 
     method_indicator <= 0;
   end
   always @(p)begin 
     start_time <=time_stamp;
   end
   always @(m, v, i , p)begin 
    confidence_score <= m+i+v+p;
   end
     
       
       
       

endmodule
