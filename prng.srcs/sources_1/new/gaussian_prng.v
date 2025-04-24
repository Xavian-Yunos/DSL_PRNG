`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 20.04.2025 13:44:13
// Design Name: 
// Module Name: gaussian_prng
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module gaussian_prng(
    input clk,
    input rstn,
    input [11:0] adc_data, 
    output reg [15:0] gaussian_out
);

    reg [15:0] lfsr1, lfsr2, lfsr3;
    reg [15:0] sum;
    reg [3:0] count;

    // LFSR for generating uniform random numbers
    always @(posedge clk or negedge rstn) begin
        if (!rstn) begin
            lfsr1 <= {adc_data, 4'b001}; // Seed LFSR with ADC data
            lfsr2 <= {adc_data, 4'b010};
            lfsr3 <= {adc_data, 4'b100};
        end 
        else begin
            lfsr1 <= {lfsr1[14:0], lfsr1[15] ^ lfsr1[13] ^ lfsr1[12] ^ lfsr1[10]};
            lfsr2 <= {lfsr1[14:0], lfsr1[15] ^ lfsr1[14] ^ lfsr1[12] ^ lfsr1[3]};
            lfsr3 <= {lfsr1[14:0], lfsr1[15] ^ lfsr1[4] ^ lfsr1[2] ^ lfsr1[1]};
        end
    end

    // Accumulate random numbers using CLT
    always @(posedge clk or negedge rstn) begin
        if (!rstn) begin
            sum <= 0;
            count <= 0;
            gaussian_out <= 0;
        end else begin
            if (count < 4'b1111) begin // Accumulate 8 random numbers (adjust if needed)
                sum <= sum + lfsr1 + lfsr2 + lfsr3;
                count <= count + 1'b1;
            end else begin
                // Scale and center the result
                gaussian_out <= (sum >> 2) + 16'h0000; // Adjust shift and offset for desired range
                sum <= 0;
                count <= 0;
            end
        end
    end

endmodule
