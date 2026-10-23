(* blackbox *)
module fl_vga3(
`ifdef USE_POWER_PINS
	inout wire VSS,
	inout wire VDD,
`endif
	input clk,
	input clk_n,
	output hsync,
	output vsync,
	output [23:0] rgb,
	input io_in,
	input rst_override_n
);

endmodule
