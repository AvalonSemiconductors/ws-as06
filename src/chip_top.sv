// SPDX-FileCopyrightText: © 2025 Project Template Contributors
// SPDX-License-Identifier: Apache-2.0

`default_nettype none

// Power/ground pads for core and I/O
`define NUM_DVDD_PADS 6
`define NUM_DVSS_PADS 8

`define NUM_VDD_PADS 2
`define NUM_VSS_PADS 2

// Signal pads
`define NUM_INPUT_PADS 5
`define NUM_BIDIR_PADS 46
`define NUM_ANALOG_PADS 4

`ifdef SRAM_gf180mcu_ocd_ip_sram
`define gf180mcu_xxx_ip_sram__sram512x8m8wm1 gf180mcu_ocd_ip_sram__sram512x8m8wm1
`else
`define gf180mcu_xxx_ip_sram__sram512x8m8wm1 gf180mcu_fd_ip_sram__sram512x8m8wm1
`endif

`ifdef PAD_gf180mcu_ocd_io
`define gf180mcu_xxx_io__vdd gf180mcu_ocd_io__vdd
`define gf180mcu_xxx_io__vss gf180mcu_ocd_io__vss
`define gf180mcu_xxx_io__dvdd gf180mcu_ocd_io__dvdd
`define gf180mcu_xxx_io__dvss gf180mcu_ocd_io__dvss
`define gf180mcu_xxx_io__in_s gf180mcu_ocd_io__in_s
`define gf180mcu_xxx_io__in_c gf180mcu_ocd_io__in_c
`define gf180mcu_xxx_io__bi_24t gf180mcu_ocd_io__bi_24t
`define gf180mcu_xxx_io__asig_5p0 gf180mcu_ocd_io__asig_5p0
`else
`define gf180mcu_xxx_io__vdd gf180mcu_fd_io__dvdd
`define gf180mcu_xxx_io__vss gf180mcu_fd_io__dvss
`define gf180mcu_xxx_io__dvdd gf180mcu_fd_io__dvdd
`define gf180mcu_xxx_io__dvss gf180mcu_fd_io__dvss
`define gf180mcu_xxx_io__in_s gf180mcu_fd_io__in_s
`define gf180mcu_xxx_io__in_c gf180mcu_fd_io__in_c
`define gf180mcu_xxx_io__bi_24t gf180mcu_fd_io__bi_24t
`define gf180mcu_xxx_io__asig_5p0 gf180mcu_fd_io__asig_5p0
`endif

module chip_top #(
	// Power/ground pads for I/O
	parameter NUM_DVDD_PADS = `NUM_DVDD_PADS,
	parameter NUM_DVSS_PADS = `NUM_DVSS_PADS,
	
	// Power/ground pads for core
	parameter NUM_VDD_PADS = `NUM_VDD_PADS,
	parameter NUM_VSS_PADS = `NUM_VSS_PADS,
	
	// Signal pads
	parameter NUM_INPUT_PADS = `NUM_INPUT_PADS,
	parameter NUM_BIDIR_PADS = `NUM_BIDIR_PADS,
	parameter NUM_ANALOG_PADS = `NUM_ANALOG_PADS
	)(
	`ifdef USE_POWER_PINS
	inout  wire VDD,
	inout  wire VSS,
	inout  wire DVDD,
	inout  wire DVSS,
	`endif
	
	inout  wire clk_PAD,
	
	inout  wire [NUM_INPUT_PADS-1:0] input_PAD,
	inout  wire [NUM_BIDIR_PADS-1:0] bidir_PAD
);
	
	wire clk_PAD2CORE;
	
	wire [NUM_INPUT_PADS-1:0] design_sel;
	
	wire [NUM_BIDIR_PADS-1:0] bidir_PAD2CORE;
	wire [NUM_BIDIR_PADS-1:0] bidir_CORE2PAD;
	wire [NUM_BIDIR_PADS-1:0] bidir_CORE2PAD_OE;
	wire [NUM_BIDIR_PADS-1:0] bidir_CORE2PAD_CS;
	wire [NUM_BIDIR_PADS-1:0] bidir_CORE2PAD_SL;
	wire [NUM_BIDIR_PADS-1:0] bidir_CORE2PAD_IE;
	wire [NUM_BIDIR_PADS-1:0] bidir_CORE2PAD_PU;
	wire [NUM_BIDIR_PADS-1:0] bidir_CORE2PAD_PD;
	
	wire [NUM_ANALOG_PADS-1:0] analog_PAD;
	
	wire [NUM_BIDIR_PADS-1:0] io_in_buffered;
	
	`ifdef USE_POWER_PINS
	`ifdef PAD_gf180mcu_fd_io
	assign VDD = DVDD;
	assign VSS = DVSS;
	`endif
	`endif
	
	generate
	for (genvar i=0; i<NUM_DVDD_PADS; i++) begin : dvdd_pads
		(* keep *)
		`gf180mcu_xxx_io__dvdd pad (
			`ifdef USE_POWER_PINS
			.DVDD   (DVDD),
			.DVSS   (DVSS),
			.VDD    (VDD),
			.VSS    (VSS)
			`endif
		);
	end
	for (genvar i=0; i<NUM_DVSS_PADS; i++) begin : dvss_pads
		(* keep *)
		`gf180mcu_xxx_io__dvss pad (
			`ifdef USE_POWER_PINS
			.DVDD   (DVDD),
			.DVSS   (DVSS),
			.VDD    (VDD),
			.VSS    (VSS)
			`endif
		);
	end
	for (genvar i=0; i<NUM_VDD_PADS; i++) begin : vdd_pads
		(* keep *)
		`gf180mcu_xxx_io__vdd pad (
			`ifdef USE_POWER_PINS
			.DVDD   (DVDD),
			.DVSS   (DVSS),
			.VDD    (VDD),
			.VSS    (VSS)
			`endif
		);
	end
	for (genvar i=0; i<NUM_VSS_PADS; i++) begin : vss_pads
		(* keep *)
		`gf180mcu_xxx_io__vss pad (
			`ifdef USE_POWER_PINS
			.DVDD   (DVDD),
			.DVSS   (DVSS),
			.VDD    (VDD),
			.VSS    (VSS)
			`endif
		);
	end
	endgenerate
	
	(* keep *)
	`gf180mcu_xxx_io__in_c clk_pad (
		`ifdef USE_POWER_PINS
		.DVDD   (DVDD),
		.DVSS   (DVSS),
		.VDD    (VDD),
		.VSS    (VSS),
		`endif
		
		.Y      (clk_PAD2CORE),
		.PAD    (clk_PAD),
		
		.PU     (1'b0),
		.PD     (1'b0)
	);
	
	generate
	for (genvar i=0; i<NUM_INPUT_PADS; i++) begin : inputs
		(* keep *)
		`gf180mcu_xxx_io__in_c pad (
			`ifdef USE_POWER_PINS
			.DVDD   (DVDD),
			.DVSS   (DVSS),
			.VDD    (VDD),
			.VSS    (VSS),
			`endif
			
			.Y      (design_sel[i]),
			.PAD    (input_PAD[i]),
			
			.PU     (1'b1),
			.PD     (1'b0)
		);
	end
	endgenerate
	
	generate
	for (genvar i=0; i<NUM_BIDIR_PADS; i++) begin : bidir
		(* keep *)
		`gf180mcu_xxx_io__bi_24t pad (
			`ifdef USE_POWER_PINS
			.DVDD   (DVDD),
			.DVSS   (DVSS),
			.VDD    (VDD),
			.VSS    (VSS),
			`endif
			
			.A      (bidir_CORE2PAD[i]),
			.OE     (bidir_CORE2PAD_OE[i]),
			.Y      (bidir_PAD2CORE[i]),
			.PAD    (bidir_PAD[i]),
			
			.CS     (bidir_CORE2PAD_CS[i]),
			.SL     (bidir_CORE2PAD_SL[i]),
			.IE     (bidir_CORE2PAD_IE[i]),
			
			.PU     (bidir_CORE2PAD_PU[i]),
			.PD     (bidir_CORE2PAD_PD[i])
		);
	end
	endgenerate
	
	generate
	for (genvar i=0; i<NUM_ANALOG_PADS; i++) begin : analog
		(* keep *)
		apad pad (
			`ifdef USE_POWER_PINS
			.DVDD   (DVDD),
			.DVSS   (DVSS),
			.VDD    (VDD),
			.VSS    (VSS),
			`endif
			.ASIG5V(),
			.WEH(analog_PAD[i])
		);
	end
	endgenerate
	
	// Input repeaters for slower designs
	generate
	for(genvar i = 0; i < NUM_BIDIR_PADS; i++) begin : input_repeaters
		(* keep *)
		gf180mcu_as_sc_mcu7t3v3__buff_16 rebuff(
		`ifdef USE_POWER_PINS
			.VNW    (VDD),
			.VPW    (VSS),
			.VDD    (VDD),
			.VSS    (VSS),
		`endif
			.A(bidir_PAD2CORE[i]),
			.Y(io_in_buffered[i])
		);
	end
	endgenerate
	
	//DACs
	reg [11:0] daci0;
	reg [11:0] daci1;
	reg [11:0] daci2;
	reg [11:0] daci3;
	(* keep *)
	r2r_dac_buffered dac_0(
	`ifdef USE_POWER_PINS
		.VSS(VSS),
		.VDD(VDD),
	`endif
		.D0(daci0[0]),
		.D1(daci0[1]),
		.D2(daci0[2]),
		.D3(daci0[3]),
		.D4(daci0[4]),
		.D5(daci0[5]),
		.D6(daci0[6]),
		.D7(daci0[7]),
		.D8(daci0[8]),
		.D9(daci0[9]),
		.D10(daci0[10]),
		.D11(daci0[11]),
		.OUT(analog_PAD[0])
	);
	(* keep *)
	r2r_dac_buffered dac_1(
	`ifdef USE_POWER_PINS
		.VSS(VSS),
		.VDD(VDD),
	`endif
		.D0(daci1[0]),
		.D1(daci1[1]),
		.D2(daci1[2]),
		.D3(daci1[3]),
		.D4(daci1[4]),
		.D5(daci1[5]),
		.D6(daci1[6]),
		.D7(daci1[7]),
		.D8(daci1[8]),
		.D9(daci1[9]),
		.D10(daci1[10]),
		.D11(daci1[11]),
		.OUT(analog_PAD[1])
	);
	(* keep *)
	r2r_dac_buffered dac_2(
	`ifdef USE_POWER_PINS
		.VSS(VSS),
		.VDD(VDD),
	`endif
		.D0(daci2[0]),
		.D1(daci2[1]),
		.D2(daci2[2]),
		.D3(daci2[3]),
		.D4(daci2[4]),
		.D5(daci2[5]),
		.D6(daci2[6]),
		.D7(daci2[7]),
		.D8(daci2[8]),
		.D9(daci2[9]),
		.D10(daci2[10]),
		.D11(daci2[11]),
		.OUT(analog_PAD[2])
	);
	(* keep *)
	r2r_dac_buffered dac_3(
	`ifdef USE_POWER_PINS
		.VSS(VSS),
		.VDD(VDD),
	`endif
		.D0(daci3[0]),
		.D1(daci3[1]),
		.D2(daci3[2]),
		.D3(daci3[3]),
		.D4(daci3[4]),
		.D5(daci3[5]),
		.D6(daci3[6]),
		.D7(daci3[7]),
		.D8(daci3[8]),
		.D9(daci3[9]),
		.D10(daci3[10]),
		.D11(daci3[11]),
		.OUT(analog_PAD[3])
	);
	
	wire re_clk;
	(* keep *)
	gf180mcu_as_sc_mcu7t3v3__clkbuff_12 clkrebuff1(
	`ifdef USE_POWER_PINS
		.VNW    (VDD),
		.VPW    (VSS),
		.VDD    (VDD),
		.VSS    (VSS),
	`endif
		.A(clk_PAD2CORE),
		.Y(re_clk)
	);
	
	//For all FeatherLane generated layouts
	wire sel_fl_mcpu32 = design_sel == 5'h1D;
	wire sel_fl_rv32i  = design_sel == 5'h1E;
	wire sel_fl_vga3   = design_sel == 5'h1C;
	wire phi1 = (sel_fl_mcpu32 | sel_fl_rv32i | sel_fl_vga3) ? bidir_PAD2CORE[0] : re_clk;
	wire phi2 = bidir_PAD2CORE[1] & (sel_fl_mcpu32 | sel_fl_rv32i | sel_fl_vga3);
	
	wire [6:0] fl_mcpu32_port_dir;
	wire [6:0] fl_mcpu32_port_out;
	wire fl_mcpu32_le;
	wire [15:0] fl_mcpu32_address;
	wire fl_mcpu32_oeb;
	wire fl_mcpu32_web;
	wire [15:0] fl_mcpu32_dout;
	wire fl_mcpu32_bus_enable;
	wire [11:0] fl_mcpu32_dac;
	
	wire [45:0] io_out_riscv;
	wire [45:0] io_oe_riscv;
	wire [11:0] dac_riscv;
	
	wire is_vga = design_sel[4:3] == 2'b01 && design_sel != 10 && design_sel != 9;
	wire [25:0] io_out_vga;
	wire [25:0] io_oe_vga;
	wire [11:0] vga_dac_r;
	wire [11:0] vga_dac_g;
	wire [11:0] vga_dac_b;
	wire [11:0] vga_dac_audio;
	
	wire select_6502;
	wire [45:0] io_out_65x;
	wire [45:0] io_oe_65x;
	
	wire [15:0] io_out_usb;
	wire [7:0] io_oe_usb;
	
	wire [45:0] io_out_mcpu;
	wire [9:0] io_oe_mcpu;
	wire [11:0] mcpu_dac;
	
	wire fl_vga3_hsync;
	wire fl_vga3_vsync;
	wire [23:0] fl_vga3_rgb;
	
	wire fl_rv32i_le;
	wire [15:0] fl_rv32i_address;
	wire fl_rv32i_oeb;
	wire fl_rv32i_web_lo;
	wire fl_rv32i_web_hi;
	wire [15:0] fl_rv32i_dout;
	wire fl_rv32i_bus_enable;
	wire [5:0] fl_rv32i_port_dir;
	wire [5:0] fl_rv32i_port_out;
	wire [11:0] fl_rv32i_dac;
	
	reg [45:0] io_out_sel;
	reg [45:0] io_oe_sel;
	reg [45:0] io_cs_sel;
	reg [45:0] io_pd_sel;
	reg [45:0] io_pu_sel;
	reg [45:0] io_sl_sel;
	assign bidir_CORE2PAD_IE = ~bidir_CORE2PAD_OE;
	assign bidir_CORE2PAD = io_out_sel;
	assign bidir_CORE2PAD_OE = io_oe_sel;
	assign bidir_CORE2PAD_CS = io_cs_sel;
	assign bidir_CORE2PAD_PD = io_pd_sel;
	assign bidir_CORE2PAD_PU = io_pu_sel;
	assign bidir_CORE2PAD_SL = io_sl_sel;
	always @(*) begin
		//Defaults
		daci0 = 12'h0;
		daci1 = 12'h0;
		daci2 = 12'h0;
		daci3 = 12'h0;
		io_out_sel = 46'h0;
		io_oe_sel = 46'h0;
		io_cs_sel = 46'h0;
		io_pu_sel = {bidir_CORE2PAD_IE[45:1], 1'b0};
		io_pd_sel = {45'h0, bidir_CORE2PAD_IE[0]};
		io_sl_sel = 46'h0;
		if(sel_fl_mcpu32) begin
			io_oe_sel = {fl_mcpu32_port_dir[6:1], 1'b1, 1'b1, fl_mcpu32_port_dir[0], 1'b1, 1'b1, 16'hFFFF, {16{fl_mcpu32_bus_enable}}, 3'b000};
			io_out_sel = {fl_mcpu32_port_out[6:1], fl_mcpu32_bus_enable, fl_mcpu32_oeb, fl_mcpu32_port_out[0], fl_mcpu32_web, fl_mcpu32_le, fl_mcpu32_address, fl_mcpu32_dout, 3'b010};
			io_cs_sel = {~fl_mcpu32_port_dir[6:1], 37'h0, 1'b1, 2'b0};
			io_pd_sel = {~fl_mcpu32_port_dir[6:1], 38'h0, 2'b11};
			io_pu_sel = {43'h0, 1'b1, 2'b0};
			daci0 = fl_mcpu32_dac;
		end else if(design_sel == 2) begin
			io_oe_sel = 46'h3FFFFFFFFFFF;
			io_out_sel = 46'h155555555555;
			daci0 = 12'hFFF;
			daci1 = 12'hC00;
			daci2 = 12'h800;
			daci3 = 12'h400;
		end else if(design_sel == 3) begin
			daci0 = bidir_PAD2CORE[12:1];
		end else if(design_sel == 9) begin
			io_oe_sel = io_oe_riscv;
			io_out_sel = io_out_riscv;
			daci0 = dac_riscv;
			io_pu_sel = {2'b00, bidir_CORE2PAD_IE[43:40], 37'h0, 1'b0, 2'b11};
			io_pd_sel = 0;
			io_sl_sel = {1'b0, 1'b1, 44'h0};
		end else if(is_vga) begin
			io_oe_sel[25:0] = io_oe_vga;
			io_out_sel[25:0] = io_out_vga;
			daci0 = vga_dac_audio;
			daci1 = vga_dac_r;
			daci2 = vga_dac_g;
			daci3 = vga_dac_b;
		end else if(design_sel[4:1] == 0) begin
			io_oe_sel = io_oe_65x;
			io_out_sel = io_out_65x;
			io_cs_sel = select_6502 ? {35'h0, 1'b1, 1'b0, 2'b11, 7'h0} : {35'h0, 2'b11, 4'h0, 1'b1, 4'h0};
			io_pd_sel = 0;
			io_pu_sel = select_6502 ? {4'hF, 14'h0, 1'b1, 12'h0, 1'b1, 8'h0, 1'b1, 2'h1, 1'b1, 1'b0, 1'b1} : {4'hF, 14'h0, 1'b1, 14'h0, 1'b1, 3'h0, 2'b11, 1'b0, 1'b1, 5'h0};
		end else if(design_sel == 4) begin
			io_oe_sel[24:0] = {8'hFF, io_oe_usb, 8'h00, 1'b0};
			io_out_sel[24:0] = {io_out_usb, 8'h00, 1'b0};
			io_pu_sel[10:9] = 2'b00;
			io_sl_sel[10:9] = io_oe_usb[1:0] & ~io_in_buffered[26:25];
			io_pu_sel[26:25] = 2'b00;
			io_pd_sel[26:25] = 2'b11;
		end else if(design_sel == 10) begin
			io_out_sel = io_out_mcpu;
			io_oe_sel = {io_oe_mcpu[9:4], 2'b11, io_oe_mcpu[3], 2'b11, 16'hFFFF, {16{io_oe_mcpu[2]}}, 1'b0, io_oe_mcpu[1:0]};
			io_cs_sel = {~io_oe_mcpu[9:4], 2'b00, ~io_oe_mcpu[3], 18'h0, 16'h0, 1'b1, ~io_oe_mcpu[1:0]};
			io_pd_sel = {~io_oe_mcpu[9:4], 2'b00, ~io_oe_mcpu[3], 18'h0, 16'h0, 1'b1, ~io_oe_mcpu[1:0]};
			io_pu_sel = 0;
			daci0 = mcpu_dac;
		end else if(sel_fl_vga3) begin
			io_oe_sel[4:0] = 5'b11100;
			io_out_sel[4] = fl_vga3_vsync;
			io_out_sel[3] = fl_vga3_hsync;
			daci1 = {fl_vga3_rgb[23:16], fl_vga3_rgb[23:20]};
			daci2 = {fl_vga3_rgb[15:8], fl_vga3_rgb[15:12]};
			daci3 = {fl_vga3_rgb[7:0], fl_vga3_rgb[7:4]};
		end else if(sel_fl_rv32i) begin
			io_oe_sel = {fl_rv32i_port_dir, 1'b1, 1'b1, 1'b1, 1'b1, 1'b1, 16'hFFFF, {16{fl_rv32i_bus_enable}}, 3'b000};
			io_out_sel = {fl_rv32i_port_out, fl_rv32i_bus_enable, fl_rv32i_oeb, fl_rv32i_web_lo, fl_rv32i_web_hi, fl_rv32i_le, fl_rv32i_address, fl_rv32i_dout, 3'b010};
			io_cs_sel = {43'h0, 1'b1, 2'b0};
			io_pd_sel = {~fl_rv32i_port_dir, 38'h0, 2'b11};
			io_pu_sel = {43'h0, 1'b1, 2'b0};
			daci0 = fl_rv32i_dac;
		end
	end
	
	(* keep *)
	riscv riscv(
	`ifdef USE_POWER_PINS
		.VSS(VSS),
		.VDD(VDD),
	`endif
		.clk_i(clk_PAD2CORE),
		.rst_override_n(design_sel == 9),
		.io_in(bidir_PAD2CORE),
		.io_out(io_out_riscv),
		.io_oe(io_oe_riscv),
		.dac(dac_riscv)
	);
	
	wire [2:0] vga_demo_sel;
	(* keep *)
	gf180mcu_as_sc_mcu7t3v3__buff_16 rebuff2(
	`ifdef USE_POWER_PINS
		.VNW    (VDD),
		.VPW    (VSS),
		.VDD    (VDD),
		.VSS    (VSS),
	`endif
		.A(design_sel[0]),
		.Y(vga_demo_sel[0])
	);
	(* keep *)
	gf180mcu_as_sc_mcu7t3v3__buff_16 rebuff3(
	`ifdef USE_POWER_PINS
		.VNW    (VDD),
		.VPW    (VSS),
		.VDD    (VDD),
		.VSS    (VSS),
	`endif
		.A(design_sel[1]),
		.Y(vga_demo_sel[1])
	);
	(* keep *)
	gf180mcu_as_sc_mcu7t3v3__buff_16 rebuff4(
	`ifdef USE_POWER_PINS
		.VNW    (VDD),
		.VPW    (VSS),
		.VDD    (VDD),
		.VSS    (VSS),
	`endif
		.A(design_sel[2]),
		.Y(vga_demo_sel[2])
	);
	(* keep *)
	vga vga(
	`ifdef USE_POWER_PINS
		.VSS(VSS),
		.VDD(VDD),
	`endif
		.clk_i(clk_PAD2CORE),
		.rst_override_n(is_vga),
		.io_in(io_in_buffered[24:0]),
		.io_out(io_out_vga),
		.io_oe(io_oe_vga),
		.demo_sel(vga_demo_sel),
		.dac_r(vga_dac_r),
		.dac_g(vga_dac_g),
		.dac_b(vga_dac_b),
		.dac_audio(vga_dac_audio)
	);
	
	(* keep *)
	gf180mcu_as_sc_mcu7t3v3__buff_16 rebuff5(
	`ifdef USE_POWER_PINS
		.VNW    (VDD),
		.VPW    (VSS),
		.VDD    (VDD),
		.VSS    (VSS),
	`endif
		.A(design_sel[0]),
		.Y(select_6502)
	);
	(* keep *)
	as65x as65x(
	`ifdef USE_POWER_PINS
		.VSS(VSS),
		.VDD(VDD),
	`endif
		.clk_i(clk_PAD2CORE),
		.rst_override_n(design_sel[4:1] == 0),
		.io_in(bidir_PAD2CORE),
		.io_out(io_out_65x),
		.io_oe(io_oe_65x),
		.select_6502(select_6502)
	);
	
	(* keep *)
	usb usb(
	`ifdef USE_POWER_PINS
		.VSS(VSS),
		.VDD(VDD),
	`endif
		.clk_i(clk_PAD2CORE),
		.rst_override_n(design_sel == 4),
		.io_in({bidir_PAD2CORE[10:9], bidir_PAD2CORE[0]}),
		.io_in_buffered({io_in_buffered[16:11], io_in_buffered[8:1]}),
		.io_out(io_out_usb),
		.io_oe(io_oe_usb)
	);
	
	(* keep *)
	fl_mcpu32 fl_mcpu32(
	`ifdef USE_POWER_PINS
		.VSS(VSS),
		.VDD(VDD),
	`endif
		.clk(phi1),
		.clk_n(phi2),
		.rst_n(io_in_buffered[2]),
		.rst_override_n(sel_fl_mcpu32),
		.din(io_in_buffered[18:3]),
		.port_dir(fl_mcpu32_port_dir),
		.port_out(fl_mcpu32_port_out),
		.port_in({io_in_buffered[45:40], io_in_buffered[37]}),
		.dac(fl_mcpu32_dac),
		.le(fl_mcpu32_le),
		.address(fl_mcpu32_address),
		.oeb(fl_mcpu32_oeb),
		.web(fl_mcpu32_web),
		.dout(fl_mcpu32_dout),
		.bus_enable(fl_mcpu32_bus_enable)
	);
	
	(* keep *)
	wrapped_mcpu wrapped_mcpu(
	`ifdef USE_POWER_PINS
		.VSS(VSS),
		.VDD(VDD),
	`endif
		.clk_i(clk_PAD2CORE),
		.rst_override_n(design_sel == 10),
		.io_in_buffered({io_in_buffered[45:40], io_in_buffered[37], io_in_buffered[18:0]}),
		.io_out(io_out_mcpu),
		.io_oe(io_oe_mcpu),
		.dac(mcpu_dac)
	);
	
	(* keep *)
	fl_vga3 fl_vga3(
	`ifdef USE_POWER_PINS
		.VSS(VSS),
		.VDD(VDD),
	`endif
		.clk(phi1),
		.clk_n(phi2),
		.hsync(fl_vga3_hsync),
		.vsync(fl_vga3_vsync),
		.rgb(fl_vga3_rgb),
		.io_in(io_in_buffered[2]),
		.rst_override_n(sel_fl_vga3)
	);
	
	(* keep *)
	fl_rv32i fl_rv32i(
	`ifdef USE_POWER_PINS
		.VSS(VSS),
		.VDD(VDD),
	`endif
		.clk(phi1),
		.clk_n(phi2),
		.rst_n(bidir_PAD2CORE[2] && sel_fl_rv32i),
		.din(bidir_PAD2CORE[18:3]),
		.le(fl_rv32i_le),
		.address(fl_rv32i_address),
		.oeb(fl_rv32i_oeb),
		.web_lo(fl_rv32i_web_lo),
		.web_hi(fl_rv32i_web_hi),
		.dout(fl_rv32i_dout),
		.bus_enable(fl_rv32i_bus_enable),
		.port_in(io_in_buffered[45:40]),
		.port_out(fl_rv32i_port_out),
		.port_dir(fl_rv32i_port_dir),
		.dac(fl_rv32i_dac)
	);
	
	(* keep *) avali avali ();
	(* keep *) deepai deepai ();
	(* keep *) td td ();
	
	// Do not remove, necessary for tapeout
	(* keep *) gf180mcu_ws_ip__qrcode_id qrcode_id ();
	(* keep *) gf180mcu_ws_ip__shuttle_id shuttle_id ();
	(* keep *) gf180mcu_ws_ip__project_id project_id ();
	(* keep *) gf180mcu_ws_ip__marker marker ();
	
	// wafer.space logo - can be removed if desired
	(* keep *) gf180mcu_ws_ip__logo wafer_space_logo ();
	
endmodule

`default_nettype wire
