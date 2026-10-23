`default_nettype none

module riscv(
`ifdef USE_POWER_PINS
	inout wire VSS,
	inout wire VDD,
`endif
	input clk_i,
	input rst_override_n,
	
	input [45:0] io_in,
	output [45:0] io_out,
	output [45:0] io_oe,
	
	output [11:0] dac
);

wire reset_n = io_in[2] & rst_override_n;
assign io_out[2:0] = 0;
assign io_oe[2:0] = 0;
assign io_oe[39:35] = 5'h1F;
wire D_oe;
assign io_oe[18:3] = {16{D_oe}};
assign io_oe[34:19] = 16'hFFFF;
assign io_oe[45] = 0;
assign io_out[45] = 0;
assign io_oe[44] = 1'b1;

cpurv32 cpu(
	.clk_i(clk_i),
	.rst_n(reset_n),
	.IRQn(io_in[0]),
	.NMIn(io_in[45]),
	.ALE(io_out[35]),
	.OEb(io_out[38]),
	.WEb_lo(io_out[37]),
	.WEb_hi(io_out[36]),
	.A_o(io_out[34:19]),
	.D_o(io_out[18:3]),
	.D_i(io_in[18:3]),
	.D_oe(D_oe),
	.MLn(io_out[39]),
	.port_val(io_out[43:40]),
	.port_dir(io_oe[43:40]),
	.port_in(io_in[43:40]),
	.TXD(io_out[44]),
	.RXD(io_in[1]),
	.dac(dac)
);

generate
for (genvar i=0; i<46; i++) begin : the_extra_diodes
	(* keep *)
	gf180mcu_as_sc_mcu7t3v3__diode_2 input_tie (
		`ifdef USE_POWER_PINS
		.VNW    (VDD),
		.VPW    (VSS),
		.VDD    (VDD),
		.VSS    (VSS),
		`endif
		.DIODE(io_in[i])
	);
	(* keep *)
	gf180mcu_as_sc_mcu7t3v3__diode_2 output_tie (
		`ifdef USE_POWER_PINS
		.VNW    (VDD),
		.VPW    (VSS),
		.VDD    (VDD),
		.VSS    (VSS),
		`endif
		.DIODE(io_out[i])
	);
	(* keep *)
	gf180mcu_as_sc_mcu7t3v3__diode_2 output_enable_tie (
		`ifdef USE_POWER_PINS
		.VNW    (VDD),
		.VPW    (VSS),
		.VDD    (VDD),
		.VSS    (VSS),
		`endif
		.DIODE(io_oe[i])
	);
end
endgenerate

generate
for (genvar i=0; i<12; i++) begin : the_dac_extra_diodes_2
	(* keep *)
	gf180mcu_as_sc_mcu7t3v3__diode_2 dac_tie (
		`ifdef USE_POWER_PINS
		.VNW    (VDD),
		.VPW    (VSS),
		.VDD    (VDD),
		.VSS    (VSS),
		`endif
		.DIODE(dac[i])
	);
end
endgenerate

endmodule
