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
	c = Clock(dut.clk, 30.72, "ns")
	cocotb.start_soon(c.start())
	await ClockCycles(dut.clk, 5)
	dut.rst_n.value = 1
	await RisingEdge(dut.vsync)
	await ClockCycles(dut.clk, 5000)
