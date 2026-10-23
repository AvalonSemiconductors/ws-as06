`default_nettype none
`timescale 1ns/1ps

module tb (
	input clk,
	
	input IRQn,
	input NMIn,
	output [15:0] A,
	output [15:0] D_out,
	input [15:0] D_in,
	output ALE,
	output OEb,
	output MLn,
	output WEb_lo,
	output WEb_hi,
	input rst_n
);

wire [45:0] iopads;

assign iopads[2] = rst_n;
assign iopads[0] = IRQn;
assign iopads[45] = NMIn;
assign ALE = iopads[35];
assign OEb = iopads[38];
assign WEb_lo = iopads[37];
assign WEb_hi = iopads[36];
assign A = iopads[34:19];
assign D_out = iopads[18:3];
assign iopads[3] = OEb ? 1'bz : D_in[0];
assign iopads[4] = OEb ? 1'bz : D_in[1];
assign iopads[5] = OEb ? 1'bz : D_in[2];
assign iopads[6] = OEb ? 1'bz : D_in[3];
assign iopads[7] = OEb ? 1'bz : D_in[4];
assign iopads[8] = OEb ? 1'bz : D_in[5];
assign iopads[9] = OEb ? 1'bz : D_in[6];
assign iopads[10] = OEb ? 1'bz : D_in[7];
assign iopads[11] = OEb ? 1'bz : D_in[8];
assign iopads[12] = OEb ? 1'bz : D_in[9];
assign iopads[13] = OEb ? 1'bz : D_in[10];
assign iopads[14] = OEb ? 1'bz : D_in[11];
assign iopads[15] = OEb ? 1'bz : D_in[12];
assign iopads[16] = OEb ? 1'bz : D_in[13];
assign iopads[17] = OEb ? 1'bz : D_in[14];
assign iopads[18] = OEb ? 1'bz : D_in[15];
assign MLn = iopads[39];

`ifdef USE_POWER_PINS
tri1 vddcore;
tri0 vsscore;
`endif

tri1 design_sel_0;
tri0 design_sel_1;
tri0 design_sel_2;
tri1 design_sel_3;
tri0 design_sel_4;

wire weh = !clk;

chip_top chip_top(
`ifdef USE_POWER_PINS
	.VDD(vddcore),
	.VSS(vsscore),
	.DVDD(vddcore),
	.DVSS(vsscore),
`endif
	.clk_PAD(weh),
	.input_PAD({design_sel_4, design_sel_3, design_sel_2, design_sel_1, design_sel_0}),
	.bidir_PAD(iopads)
);

endmodule

`default_nettype wire
