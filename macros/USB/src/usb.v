`default_nettype none

module usb(
`ifdef USE_POWER_PINS
	inout wire VSS,
	inout wire VDD,
`endif
	input clk_i,
	input rst_override_n,
	
	input [2:0] io_in,
	input [13:0] io_in_buffered,
	output [15:0] io_out,
	output [7:0] io_oe
);

tt_um_urish_usb_cdc usb(
	.ui_in(io_in_buffered[7:0]),
	.uo_out(io_out[15:8]),
	.uio_in({io_in_buffered[13:8], io_in[2:1]}),
	.uio_out(io_out[7:0]),
	.uio_oe(io_oe),
	.ena(1'b1),
	.clk(clk_i),
	.rst_n(rst_override_n && io_in[0])
);

endmodule

`default_nettype wire
