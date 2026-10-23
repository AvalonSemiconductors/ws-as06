`default_nettype none

module channel2(
	input clk_i,
	input rst,
	output reg OP,
	output finished
);

wire [4:0] scale_ROM_idx;
localparam scale_bitsn1 = 4;
reg [15:0] scale_ROM;
always @(*) begin
	case(scale_ROM_idx)
	default: scale_ROM = 'hxxxxxxxx;
	0: scale_ROM = 'h0;
	1: scale_ROM = 'h36e6;
	2: scale_ROM = 'h3407;
	3: scale_ROM = 'hdc17;
	4: scale_ROM = 'h4987;
	5: scale_ROM = 'h7f87;
	6: scale_ROM = 'h6b2;
	7: scale_ROM = 'he043;
	8: scale_ROM = 'h5758;
	9: scale_ROM = 'h1718;
	10: scale_ROM = 'hae4e;
	11: scale_ROM = 'hf5b;
	12: scale_ROM = 'hf387;
	13: scale_ROM = 'h944f;
	14: scale_ROM = 'h714;
	15: scale_ROM = 'ha069;
	16: scale_ROM = 'haaed;
	17: scale_ROM = 'hb0f;
	18: scale_ROM = 'h53c;
	19: scale_ROM = 'hd3ad;
	endcase
end

wire [8:0] tune_ROM_idx;
localparam last_idx = 280;
localparam pc_bitsn1 = 8;
reg [8:0] tune_ROM;
always @(*) begin
	case(tune_ROM_idx)
	default: tune_ROM = 'hxxxxxxxx;
	0: tune_ROM = 'hf;
	1: tune_ROM = 'h3;
	2: tune_ROM = 'he1;
	3: tune_ROM = 'h1;
	4: tune_ROM = 'he1;
	5: tune_ROM = 'h5;
	6: tune_ROM = 'hc1;
	7: tune_ROM = 'h1;
	8: tune_ROM = 'hc1;
	9: tune_ROM = 'hf;
	10: tune_ROM = 'hd;
	11: tune_ROM = 'hf1;
	12: tune_ROM = 'h1;
	13: tune_ROM = 'hf1;
	14: tune_ROM = 'h5;
	15: tune_ROM = 'hb1;
	16: tune_ROM = 'h1;
	17: tune_ROM = 'hb1;
	18: tune_ROM = 'hf;
	19: tune_ROM = 'hd;
	20: tune_ROM = 'hf1;
	21: tune_ROM = 'h1;
	22: tune_ROM = 'hf1;
	23: tune_ROM = 'h5;
	24: tune_ROM = 'hb1;
	25: tune_ROM = 'h1;
	26: tune_ROM = 'hb1;
	27: tune_ROM = 'hf;
	28: tune_ROM = 'hd;
	29: tune_ROM = 'he1;
	30: tune_ROM = 'h1;
	31: tune_ROM = 'he1;
	32: tune_ROM = 'h5;
	33: tune_ROM = 'hc1;
	34: tune_ROM = 'h1;
	35: tune_ROM = 'hc1;
	36: tune_ROM = 'hf;
	37: tune_ROM = 'hd;
	38: tune_ROM = 'h101;
	39: tune_ROM = 'h1;
	40: tune_ROM = 'h101;
	41: tune_ROM = 'h5;
	42: tune_ROM = 'he1;
	43: tune_ROM = 'h1;
	44: tune_ROM = 'he1;
	45: tune_ROM = 'hf;
	46: tune_ROM = 'hd;
	47: tune_ROM = 'h111;
	48: tune_ROM = 'h1;
	49: tune_ROM = 'h111;
	50: tune_ROM = 'h5;
	51: tune_ROM = 'hc1;
	52: tune_ROM = 'h1;
	53: tune_ROM = 'hc1;
	54: tune_ROM = 'hf;
	55: tune_ROM = 'hf;
	56: tune_ROM = 'hf;
	57: tune_ROM = 'hf;
	58: tune_ROM = 'h5;
	59: tune_ROM = 'h2a;
	60: tune_ROM = 'h0;
	61: tune_ROM = 'h3a;
	62: tune_ROM = 'hf;
	63: tune_ROM = 'hf;
	64: tune_ROM = 'hf;
	65: tune_ROM = 'hf;
	66: tune_ROM = 'hf;
	67: tune_ROM = 'hf;
	68: tune_ROM = 'hf;
	69: tune_ROM = 'hf;
	70: tune_ROM = 'hf;
	71: tune_ROM = 'hf;
	72: tune_ROM = 'hf;
	73: tune_ROM = 'h4;
	74: tune_ROM = 'h17;
	75: tune_ROM = 'h3;
	76: tune_ROM = 'hc0;
	77: tune_ROM = 'h0;
	78: tune_ROM = 'hc0;
	79: tune_ROM = 'h4;
	80: tune_ROM = 'hc1;
	81: tune_ROM = 'hf;
	82: tune_ROM = 'hf;
	83: tune_ROM = 'hf;
	84: tune_ROM = 'hf;
	85: tune_ROM = 'hf;
	86: tune_ROM = 'hf;
	87: tune_ROM = 'hf;
	88: tune_ROM = 'hf;
	89: tune_ROM = 'hf;
	90: tune_ROM = 'hf;
	91: tune_ROM = 'h9;
	92: tune_ROM = 'h17;
	93: tune_ROM = 'h3;
	94: tune_ROM = 'hc0;
	95: tune_ROM = 'h0;
	96: tune_ROM = 'hc0;
	97: tune_ROM = 'h4;
	98: tune_ROM = 'hc1;
	99: tune_ROM = 'hf;
	100: tune_ROM = 'hf;
	101: tune_ROM = 'hf;
	102: tune_ROM = 'hf;
	103: tune_ROM = 'hf;
	104: tune_ROM = 'hf;
	105: tune_ROM = 'hf;
	106: tune_ROM = 'hf;
	107: tune_ROM = 'hf;
	108: tune_ROM = 'hf;
	109: tune_ROM = 'hf;
	110: tune_ROM = 'h5;
	111: tune_ROM = 'h130;
	112: tune_ROM = 'h0;
	113: tune_ROM = 'h130;
	114: tune_ROM = 'h0;
	115: tune_ROM = 'h131;
	116: tune_ROM = 'h1;
	117: tune_ROM = 'h121;
	118: tune_ROM = 'h1;
	119: tune_ROM = 'h101;
	120: tune_ROM = 'hf;
	121: tune_ROM = 'hf;
	122: tune_ROM = 'hf;
	123: tune_ROM = 'hf;
	124: tune_ROM = 'hf;
	125: tune_ROM = 'hf;
	126: tune_ROM = 'hf;
	127: tune_ROM = 'hf;
	128: tune_ROM = 'hf;
	129: tune_ROM = 'hf;
	130: tune_ROM = 'hf;
	131: tune_ROM = 'h1;
	132: tune_ROM = 'h130;
	133: tune_ROM = 'h0;
	134: tune_ROM = 'h130;
	135: tune_ROM = 'h0;
	136: tune_ROM = 'h131;
	137: tune_ROM = 'h1;
	138: tune_ROM = 'h121;
	139: tune_ROM = 'h1;
	140: tune_ROM = 'h103;
	141: tune_ROM = 'h7;
	142: tune_ROM = 'h73;
	143: tune_ROM = 'h3;
	144: tune_ROM = 'h77;
	145: tune_ROM = 'h95;
	146: tune_ROM = 'h81;
	147: tune_ROM = 'h73;
	148: tune_ROM = 'hf;
	149: tune_ROM = 'h3;
	150: tune_ROM = 'h71;
	151: tune_ROM = 'h5;
	152: tune_ROM = 'h77;
	153: tune_ROM = 'ha5;
	154: tune_ROM = 'h91;
	155: tune_ROM = 'h83;
	156: tune_ROM = 'hf;
	157: tune_ROM = 'h3;
	158: tune_ROM = 'h83;
	159: tune_ROM = 'h3;
	160: tune_ROM = 'h87;
	161: tune_ROM = 'hc5;
	162: tune_ROM = 'ha1;
	163: tune_ROM = 'hd3;
	164: tune_ROM = 'hf;
	165: tune_ROM = 'h71;
	166: tune_ROM = 'h1;
	167: tune_ROM = 'h51;
	168: tune_ROM = 'h5;
	169: tune_ROM = 'h51;
	170: tune_ROM = 'h1;
	171: tune_ROM = 'h51;
	172: tune_ROM = 'h5;
	173: tune_ROM = 'h51;
	174: tune_ROM = 'h1;
	175: tune_ROM = 'h6e;
	176: tune_ROM = 'h8;
	177: tune_ROM = 'h73;
	178: tune_ROM = 'h3;
	179: tune_ROM = 'h77;
	180: tune_ROM = 'h95;
	181: tune_ROM = 'h81;
	182: tune_ROM = 'h73;
	183: tune_ROM = 'hf;
	184: tune_ROM = 'h3;
	185: tune_ROM = 'h71;
	186: tune_ROM = 'h5;
	187: tune_ROM = 'h77;
	188: tune_ROM = 'ha5;
	189: tune_ROM = 'h91;
	190: tune_ROM = 'h83;
	191: tune_ROM = 'hf;
	192: tune_ROM = 'h3;
	193: tune_ROM = 'h83;
	194: tune_ROM = 'h3;
	195: tune_ROM = 'h87;
	196: tune_ROM = 'hc5;
	197: tune_ROM = 'ha1;
	198: tune_ROM = 'hd3;
	199: tune_ROM = 'hf;
	200: tune_ROM = 'h71;
	201: tune_ROM = 'h1;
	202: tune_ROM = 'h51;
	203: tune_ROM = 'h5;
	204: tune_ROM = 'h51;
	205: tune_ROM = 'h1;
	206: tune_ROM = 'h51;
	207: tune_ROM = 'h5;
	208: tune_ROM = 'h51;
	209: tune_ROM = 'h1;
	210: tune_ROM = 'h6b;
	211: tune_ROM = 'h63;
	212: tune_ROM = 'hf;
	213: tune_ROM = 'hf;
	214: tune_ROM = 'hf;
	215: tune_ROM = 'hf;
	216: tune_ROM = 'hf;
	217: tune_ROM = 'hf;
	218: tune_ROM = 'hf;
	219: tune_ROM = 'hf;
	220: tune_ROM = 'hf;
	221: tune_ROM = 'hf;
	222: tune_ROM = 'h3;
	223: tune_ROM = 'h11;
	224: tune_ROM = 'hf;
	225: tune_ROM = 'hf;
	226: tune_ROM = 'hf;
	227: tune_ROM = 'hf;
	228: tune_ROM = 'hf;
	229: tune_ROM = 'hf;
	230: tune_ROM = 'hf;
	231: tune_ROM = 'hf;
	232: tune_ROM = 'hf;
	233: tune_ROM = 'hf;
	234: tune_ROM = 'hf;
	235: tune_ROM = 'hd;
	236: tune_ROM = 'h11;
	237: tune_ROM = 'hf;
	238: tune_ROM = 'hf;
	239: tune_ROM = 'hf;
	240: tune_ROM = 'hf;
	241: tune_ROM = 'hf;
	242: tune_ROM = 'hf;
	243: tune_ROM = 'hf;
	244: tune_ROM = 'hf;
	245: tune_ROM = 'hf;
	246: tune_ROM = 'hf;
	247: tune_ROM = 'hf;
	248: tune_ROM = 'h1;
	249: tune_ROM = 'h11;
	250: tune_ROM = 'hf;
	251: tune_ROM = 'hf;
	252: tune_ROM = 'hf;
	253: tune_ROM = 'hf;
	254: tune_ROM = 'hf;
	255: tune_ROM = 'hf;
	256: tune_ROM = 'hf;
	257: tune_ROM = 'hf;
	258: tune_ROM = 'hf;
	259: tune_ROM = 'hf;
	260: tune_ROM = 'hf;
	261: tune_ROM = 'hd;
	262: tune_ROM = 'h11;
	263: tune_ROM = 'hf;
	264: tune_ROM = 'h5;
	265: tune_ROM = 'h23;
	266: tune_ROM = 'h23;
	267: tune_ROM = 'h23;
	268: tune_ROM = 'h23;
	269: tune_ROM = 'h23;
	270: tune_ROM = 'h23;
	271: tune_ROM = 'h23;
	272: tune_ROM = 'h23;
	273: tune_ROM = 'h23;
	274: tune_ROM = 'h23;
	275: tune_ROM = 'h7;
	276: tune_ROM = 'h43;
	277: tune_ROM = 'hf;
	278: tune_ROM = 'hf;
	279: tune_ROM = 'hf;
	280: tune_ROM = 'hf;
	endcase
end

reg [pc_bitsn1:0] PC;
assign tune_ROM_idx = PC;
wire [3:0] len = tune_ROM[3:0];
assign scale_ROM_idx = tune_ROM[scale_bitsn1+4:4];

reg [15:0] lfsr;
reg [18:0] timeout_lfsr;
reg [8:0] break_lfsr;
reg [3:0] qn_counter;
reg just_reset;
reg [1:0] master_clkdiv;

assign finished = PC == last_idx;

always @(posedge clk_i) begin
	master_clkdiv <= rst ? 0 : master_clkdiv - 1;
	if(rst) begin
		lfsr <= 0;
		timeout_lfsr <= 1;
		PC <= 0;
		OP <= 0;
		qn_counter <= 0;
		just_reset <= 0;
		break_lfsr <= 1;
	end else if(master_clkdiv == 0) begin
		lfsr <= {lfsr[14:0], lfsr[15] ^ lfsr[13] ^ lfsr[12] ^ lfsr[10]};
		if(lfsr == 1 || just_reset) begin
			if(break_lfsr == 1) OP <= !OP;
			lfsr <= scale_ROM;
			just_reset <= 0;
		end
		if(break_lfsr != 1) break_lfsr <= {break_lfsr[7:0], break_lfsr[8] ^ break_lfsr[4]};
		
		timeout_lfsr <= {timeout_lfsr[17:0], timeout_lfsr[18] ^ timeout_lfsr[17] ^ timeout_lfsr[16] ^ timeout_lfsr[13]};
		if(timeout_lfsr == 1) begin
			qn_counter <= qn_counter + 1;
			if(qn_counter == len) begin
				PC <= finished ? PC : PC + 1;
				qn_counter <= 0;
				just_reset <= 1'b1;
				break_lfsr <= 8'h02;
			end
		end
	end
end

endmodule

`default_nettype wire
