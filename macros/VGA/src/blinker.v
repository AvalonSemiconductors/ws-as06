`default_nettype none

module blinker(
	input clk_i,
	input rst,
	output [3:0] io_out,
	output [2:0] dac_out
);

wire [3:0] finished;
wire all_finished = &finished;

channel0 voice0(
	.clk_i(clk_i),
	.rst(rst | all_finished),
	.OP(io_out[0]),
	.finished(finished[0])
);

channel1 voice1(
	.clk_i(clk_i),
	.rst(rst | all_finished),
	.OP(io_out[1]),
	.finished(finished[01])
);

channel2 voice2(
	.clk_i(clk_i),
	.rst(rst | all_finished),
	.OP(io_out[2]),
	.finished(finished[2])
);

channel3 voice3(
	.clk_i(clk_i),
	.rst(rst | all_finished),
	.OP(io_out[3]),
	.finished(finished[3])
);

assign dac_out = io_out[0] + io_out[1] + io_out[2] + io_out[3];

endmodule

`default_nettype wire
