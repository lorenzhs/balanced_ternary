#!/usr/bin/env python3
# Author: Lorenz Hübschle-Schneider
# Lincense: MIT
# encoding: utf-8

# Some fun with Balanced Ternary numbers
class BT(object):
	# Get the balanced ternary representation for an integer
	def int2bt(value):
		if value == 0:
			return ['0']

		# Check for negative numbers
		negate = (value < 0)
		if negate:
			value *= -1

		ret, remainder = [], 0
		while value >= 0 and not (value == 0 and remainder == 1):
			remainder, value = value % 3, value // 3
			if remainder == 0:
				ret.append('0')
			elif remainder == 1:
				ret.append('+')
			else:
				ret.append('-')
				value += 1
		ret.reverse()

		if negate:
			ret = BT.negate(ret)

		return ret

	# Convert a balanced ternary number back into an integer
	def bt2int(value):
		if type(value) == str: # parse strings like '--+0'
			return BT.bt2int(list(value))
		result, exponent = 0, len(value) - 1
		for index, element in enumerate(value):
			delta = 3 ** (exponent - index)
			if element == '+':
				result += delta
			elif element == '-':
				result -= delta
		return result

	def pretty(value):
		return '{val} ({int})'.format(val=''.join(value), int=BT.bt2int(value))

	# negate a BT value (multiply by -1)
	def negate(value):
		result = value[:]  # make a copy
		for index, element in enumerate(result):
			if element == '+':
				result[index] = '-'
			elif element == '-':
				result[index] = '+'
		return result

	def is_negative(value):
		return len(value) > 0 and BT.trunc(value)[0] == '-'

	def is_zero(value):
		return all(map(lambda x: x == '0', value))

	def _align_to_length(value, length):
		assert len(value) <= length
		return ['0'] * (length - len(value)) + value

	def trunc(value):
		for index, elem in enumerate(value):
			if elem != '0':
				return value[index:]
		return ['0']

	def align(valueA, valueB):
		length = max(len(valueA), len(valueB))
		return (BT._align_to_length(valueA, length), BT._align_to_length(valueB, length))

	# add two trits (and a carry), returning (sum, carry)
	def trit_add(trit1, trit2, carry='0'):
		# this is the lame version but of course you can also do this conditionally
		table = {'+': 1, '0': 0, '-': -1}
		value = sum(map(lambda x: table[x], [trit1, trit2, carry]))
		if value == -3:
			return ('0', '-')
		elif value == -2:
			return ('+', '-')
		elif value == -1:
			return ('-', '0')
		elif value == 0:
			return ('0', '0')
		elif value == 1:
			return ('+', '0')
		elif value == 2:
			return ('-', '+')
		elif value == 3:
			return ('0', '+')

	# add to balanced ternary values
	def add(valueA, valueB):
		fst, snd = BT.align(valueA, valueB)
		result, carry = [], '0'
		for x, y in reversed(list(zip(fst, snd))):
			digit, carry = BT.trit_add(x, y, carry)
			result.append(digit)
		if carry != '0':
			result.append(carry)
		return list(reversed(result))

	# subtract valueB from valueA
	def sub(valueA, valueB):
		return BT.add(valueA, BT.negate(valueB))

	def mul(valueA, valueB):
		if len(valueB) < len(valueA):
			return mul(valueB, valueA)
		result = ['0']
		if BT.is_zero(valueA) or BT.is_zero(valueB):
			return result  # no need to multiply by zero

		for index, elem in enumerate(reversed(valueA)):
			if elem == '0':
				continue  # nothing to do in this iteration
			temp = valueB if elem == '+' else BT.negate(valueB)
			temp += ['0'] * index  # pad to get alignment right
			result = BT.add(result, temp)
		return result

	def div(valueA, valueB):
		if BT.is_zero(valueB):
			raise ZeroDivisionError("Division of {list} ({int}) by zero!"
				.format(list=valueA, int=BT.bt2int(valueA)))

		valA, valB = BT.trunc(valueA), BT.trunc(valueB)
		# 0 / foo = 0
		if BT.is_zero(valA):
			return ['0']
		# foo / 1 = foo
		if valB == ['+']:
			return valA
		# foo / -1 = -foo
		if valB == ['-']:
			return BT.negate(valA)

		# foo / -x = -(foo / x) (remainder unchanged)
		if BT.is_negative(valB):
			(quotient, remainder) = BT.div(valA, negate(valB))
			return (negate(quotient), remainder)
		# -foo / x = -(foo / x) (remainder negated)
		if BT.is_negative(valA):
			(quotient, remainder) = BT.div(negate(valA), valB)
			return (negate(quotient), negate(remainder))

		quotient, remainder = ['0'], valA[:]
		while True:  # I kinda need a ">=" here...
			new_remainder = BT.sub(remainder, valB)
			if BT.is_negative(new_remainder):
				break
			remainder = new_remainder
			quotient = BT.add(quotient, ['+'])
		return (quotient, BT.trunc(remainder))

# Execute an operation on two arguments and print the result in a pretty manner
def pretty(intA, intB, op, op_name):
	valA, valB = BT.int2bt(intA), BT.int2bt(intB)
	res = op(valA, valB)
	out = ''
	if type(res) == tuple:  # for operations with multiple results like div
		out = ", ".join(map(lambda x : BT.pretty(x), res))
	else:
		out = BT.pretty(res)

	print('{A} {op} {B} = {R}'
		.format(A=BT.pretty(valA), op=op_name, B=BT.pretty(valB), R=out))

if __name__ == '__main__':
	pretty(5, 6, BT.add, 'add')
	pretty(8, -13, BT.sub, 'sub')
	pretty(-4, 5, BT.mul, 'mul')
	pretty(1337, 42, BT.div, 'div')
