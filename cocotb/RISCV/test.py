import cocotb
import struct
import os
import sys
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles

@cocotb.test()
async def test_riscv(dut):
	dut._log.info("start")
	dut.rst_n.value = 0
	dut.IRQn.value = 1
	dut.NMIn.value = 1
	dut.D_in.value = 0
	c = Clock(dut.clk, 100, "ns")
	cocotb.start_soon(c.start())
	await ClockCycles(dut.clk, 5)
	await ClockCycles(dut.clk, 1)
	dut.rst_n.value = 1
	
	max_cycles = 2400000
	curr_cycle = 0
	memory = [0] * 65536
	no_rep = False
	fsize = os.path.getsize("C/baremetal.bin")
	with open("C/baremetal.bin", mode="rb") as file:
		aaaa = file.read()
		for i in range(0, fsize>>1):
			memory[i] = struct.unpack("B", aaaa[i*2:i*2+1])[0] + (struct.unpack("B", aaaa[i*2+1:i*2+2])[0] << 8)
	while curr_cycle < max_cycles:
		await Timer(12, "ns")
		address = dut.A.value.to_unsigned() >> 1
		if(dut.WEb_hi.value == 0 or dut.WEb_lo.value == 0):
			dut.D_in.value = 0
			previous = memory[address]
			busval = dut.D_out.value.to_unsigned()
			#dut._log.info(f"Memory write {dut.A.value} = {dut.D_out.value}")
			if(dut.WEb_lo.value == 0 and dut.WEb_hi.value == 0):
				memory[address] = busval
			elif(dut.WEb_lo.value == 0):
				previous &= 0xFF00
				busval &= 0x00FF
				memory[address] = previous | busval
			elif(dut.WEb_hi.value == 0):
				previous &= 0x00FF
				busval &= 0xFF00
				memory[address] = previous | busval
			if(address == 32767):
				#dut._log.info(f"Wrote a {dut.D_out.value.to_unsigned()} to debug address")
				if(dut.D_out.value == 0):
					break
				else:
					c = chr(dut.D_out.value.to_unsigned() & 0xFF)
					sys.stdout.write(c)
					sys.stdout.flush()
					if(c == '3'):
						dut.NMIn.value = 0
					else:
						dut.NMIn.value = 1
					if(no_rep and c == '\n'):
						no_rep = False
					elif(c == '\n' and no_rep == False):
						dut.IRQn.value = 0
						no_rep = True
					else:
						dut.IRQn.value = 1
			await FallingEdge(dut.clk)
			await RisingEdge(dut.clk)
		else:
			memval = memory[address]
			dut.D_in.value = memval
			await FallingEdge(dut.clk)
			await RisingEdge(dut.clk)
		curr_cycle = curr_cycle + 1
