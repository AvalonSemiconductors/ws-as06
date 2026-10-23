`default_nettype none

module vga(
`ifdef USE_POWER_PINS
	inout wire VSS,
	inout wire VDD,
`endif
	input clk_i,
	input rst_override_n,
	
	input [24:0] io_in,
	output [25:0] io_out,
	output [25:0] io_oe,
	
	input [2:0] demo_sel,
	
	output [11:0] dac_r,
	output [11:0] dac_g,
	output [11:0] dac_b,
	output [11:0] dac_audio
);

wire reset_n = io_in[0] & rst_override_n;
assign io_oe[0] = 0;
assign io_out[0] = 0;
assign io_oe[8:1] = 0;
assign io_out[8:1] = 8'hFF;
assign io_oe[16:9] = 8'hFF;

reg [7:0] scr_out;
reg [7:0] scr_io;
reg [7:0] scr_oe;
tt_um_waferspace_vga_screensaver vga_scr(
	.ui_in(io_in[8:1]),
	.uo_out(scr_out),
	.uio_in(io_in[24:17]),
	.uio_out(scr_io),
	.uio_oe(scr_oe),
	.ena(1'b1),
	.clk(clk_i),
	.rst_n(reset_n && demo_sel == 6)
);

wire [7:0] tile_out;
wire [7:0] tile_io;
wire [7:0] tile_oe;
wire [11:0] tile_sound;
tt_um_toivoh_demo_4tile vga_4tile(
	.ui_in(io_in[8:1]),
	.uo_out(tile_out),
	.uio_in(io_in[24:17]),
	.uio_out(tile_io),
	.uio_oe(tile_oe),
	.ena(1'b1),
	.clk(clk_i),
	.rst_n(reset_n && demo_sel == 4),
	.sound(tile_sound)
);

wire [7:0] drop_out;
wire [7:0] drop_io;
wire [7:0] drop_oe;
tt_um_rejunity_vga_test01 vga_drop(
	.ui_in(io_in[8:1]),
	.uo_out(drop_out),
	.uio_in(io_in[24:17]),
	.uio_out(drop_io),
	.uio_oe(drop_oe),
	.ena(1'b1),
	.clk(clk_i),
	.rst_n(reset_n && demo_sel == 3)
);

wire [31:0] demo_argb;
wire demo_hsync;
wire demo_vsync;
vga_demo demo(
	.clk(clk_i),
	.rst_n(reset_n && demo_sel == 0),
	.argb(demo_argb),
	.hsync(demo_hsync),
	.vsync(demo_vsync)
);

wire [3:0] blinker_out;
wire [2:0] blinker_dac;
blinker blinker(
	.clk_i(clk_i),
	.rst(!(reset_n && demo_sel == 0)),
	.io_out(blinker_out),
	.dac_out(blinker_dac)
);

wire [23:0] controller_rgb;
wire controller_hsync;
wire controller_vsync;
wire controller_hblank;
wire controller_vblank;
wire controller_registered;
controller controller(
	.clk(clk_i),
	.rst_n(reset_n && demo_sel == 5),
	.r(controller_rgb[23:16]),
	.g(controller_rgb[15:8]),
	.b(controller_rgb[7:0]),
	.ui_in(io_in[8:1]),
	.registered(controller_registered),
	.hsync(controller_hsync),
	.vsync(controller_vsync),
	.hblank(controller_hblank),
	.vblank(controller_vblank)
);

assign io_oe[25] = 1'b1;
blink blink(
	.clk(clk_i),
	.LED(io_out[25])
);

reg [7:0] out_sel;
reg [7:0] io_sel;
reg [7:0] oe_sel;
reg [11:0] audio_sel;
assign io_out[16:9] = out_sel;
assign io_out[24:17] = io_sel;
assign io_oe[24:17] = oe_sel;
always @(*) begin
	case(demo_sel)
		default: begin
			out_sel = 0;
			io_sel = 0;
			oe_sel = 0;
			audio_sel = 12'hFFF;
		end
		0: begin
			out_sel = {demo_hsync, 3'b000, demo_vsync, 3'b000};
			io_sel = {4'h0, blinker_out};
			oe_sel = 8'h0F;
			audio_sel = {blinker_dac, blinker_dac, blinker_dac, blinker_dac};
		end
		6: begin
			out_sel = scr_out;
			io_sel = scr_io;
			oe_sel = scr_oe;
			audio_sel = 12'hFFF;
		end
		4: begin
			out_sel = tile_out;
			io_sel = tile_io;
			oe_sel = tile_oe;
			audio_sel = tile_sound;
		end
		3: begin
			out_sel = drop_out;
			io_sel = drop_io;
			oe_sel = drop_oe;
			audio_sel = {drop_io, 4'hF};
		end
		5: begin
			out_sel = {controller_hsync, 3'b000, controller_vsync, 3'b000};
			io_sel = {5'h0, controller_hblank, controller_vblank, controller_registered};
			oe_sel = 7;
			audio_sel = 12'hFFF;
		end
	endcase
end

wire [1:0] r2 = {out_sel[0], out_sel[4]};
wire [1:0] g2 = {out_sel[1], out_sel[5]};
wire [1:0] b2 = {out_sel[2], out_sel[6]};
wire vsync = out_sel[3];
wire hsync = out_sel[7];
wire is = demo_sel == 0;
wire i2 = demo_sel == 5;
wire [7:0] r_inv = 8'hFF - (is ? demo_argb[23:16] : (i2 ? controller_rgb[23:16] : {r2,r2,r2,r2}));
wire [7:0] g_inv = 8'hFF - (is ? demo_argb[15:8] : (i2 ? controller_rgb[15:8] : {g2,g2,g2,g2}));
wire [7:0] b_inv = 8'hFF - (is ? demo_argb[7:0] : (i2 ? controller_rgb[7:0] : {b2,b2,b2,b2}));
assign dac_r = {r_inv, r_inv[7:4]};
assign dac_g = {g_inv, g_inv[7:4]};
assign dac_b = {b_inv, b_inv[7:4]};
assign dac_audio = 12'hFFF - audio_sel;

generate
for (genvar i=0; i<25; i++) begin : the_extra_diodes
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

(* keep *)
gf180mcu_as_sc_mcu7t3v3__diode_2 output_tie_25 (
	`ifdef USE_POWER_PINS
	.VNW    (VDD),
	.VPW    (VSS),
	.VDD    (VDD),
	.VSS    (VSS),
	`endif
	.DIODE(io_out[25])
);
(* keep *)
gf180mcu_as_sc_mcu7t3v3__diode_2 output_enable_tie_25 (
	`ifdef USE_POWER_PINS
	.VNW    (VDD),
	.VPW    (VSS),
	.VDD    (VDD),
	.VSS    (VSS),
	`endif
	.DIODE(io_oe[25])
);

generate
for (genvar i=0; i<12; i++) begin : the_dac_extra_diodes_2
	(* keep *)
	gf180mcu_as_sc_mcu7t3v3__diode_2 dac_r_tie (
		`ifdef USE_POWER_PINS
		.VNW    (VDD),
		.VPW    (VSS),
		.VDD    (VDD),
		.VSS    (VSS),
		`endif
		.DIODE(dac_r[i])
	);
	(* keep *)
	gf180mcu_as_sc_mcu7t3v3__diode_2 dac_g_tie (
		`ifdef USE_POWER_PINS
		.VNW    (VDD),
		.VPW    (VSS),
		.VDD    (VDD),
		.VSS    (VSS),
		`endif
		.DIODE(dac_g[i])
	);
	(* keep *)
	gf180mcu_as_sc_mcu7t3v3__diode_2 dac_b_tie (
		`ifdef USE_POWER_PINS
		.VNW    (VDD),
		.VPW    (VSS),
		.VDD    (VDD),
		.VSS    (VSS),
		`endif
		.DIODE(dac_b[i])
	);
	(* keep *)
	gf180mcu_as_sc_mcu7t3v3__diode_2 dac_audio_tie (
		`ifdef USE_POWER_PINS
		.VNW    (VDD),
		.VPW    (VSS),
		.VDD    (VDD),
		.VSS    (VSS),
		`endif
		.DIODE(dac_audio[i])
	);
end
endgenerate

generate
for (genvar i=0; i<3; i++) begin : the_dac_extra_diodes_3
	(* keep *)
	gf180mcu_as_sc_mcu7t3v3__diode_2 demo_sel_tie (
		`ifdef USE_POWER_PINS
		.VNW    (VDD),
		.VPW    (VSS),
		.VDD    (VDD),
		.VSS    (VSS),
		`endif
		.DIODE(demo_sel[i])
	);
end
endgenerate

endmodule

module blink(
    input clk,
    output LED
    );
integer counter;
reg state;
always @ (posedge clk) begin
    counter <= counter + 1;
     if(counter >= 8000000 )begin
        counter <=0;
        state <= !state;
     end 
end 
assign LED = state;        
endmodule

`default_nettype wire
