import os
import re


class LFSR:
    def __init__(self, size, state, taps):
        '''
        Initializes the LFSR.

        :param size: Register size in bits.
        :param state: Initial state as a binary string (e.g., '0110').
        :param taps: Tap positions (0-based indexing) for XOR feedback.
        '''
        self.size = size  # Register size
        self.taps = taps  # Tap positions for feedback
        self.initial_state = state  # Store initial state
        self.state = int(state, 2)  # Convert binary string to integer

    def get_size(self):
        '''Returns the current register size.'''
        return self.size

    def set_size(self, new_size):
        '''
        Sets a new register size and adjusts the state.
        - If new size is larger, pad with leading zeros.
        - If new size is smaller, truncate from MSB.
        '''
        if new_size <= 0:
            raise ValueError('Register size must be greater than zero.')

        old_state = self.get_state()
        new_state = old_state[-new_size:].zfill(new_size)
        self.size = new_size
        self.state = int(new_state, 2)
        self.initial_state = new_state

    def get_state(self):
        '''Returns the current state as a binary string.'''
        return f'{self.state:0{self.size}b}'

    def set_state(self, new_state):
        '''Sets a new state for the LFSR.'''
        if len(new_state) != self.size or not all(c in '01' for c in new_state):
            raise ValueError('New state must be a binary string of the same length.')
        self.state = int(new_state, 2)

    def reset(self):
        '''Resets the LFSR to its initial state.'''
        self.state = int(self.initial_state, 2)

    def next_bit(self):
        '''Generates the next bit and updates the LFSR state.'''
        feedback = 0
        for tap in self.taps:
            feedback ^= (self.state >> (self.size - tap)) & 1
        self.state = (self.state >> 1) | (feedback << (self.size - 1))
        return feedback


    def generate_bits(self, length):
        '''Generates a sequence of bits from the LFSR.'''
        self.reset()
        bits = [self.next_bit() for _ in range(length+1)] # Indexing +1
        return bits

    def print_state_table(self, length):
        '''Generates a Table of bits from the LFSR.'''
        self.reset()
        print('General LFSR Output: \n')
        print('=' * (self.size * 6 + 15))  # Adjust table width dynamically
        header = '|  t  |   ' + '   |  '.join([f'r{i}' for i in range(self.size - 1, -1, -1)]) +  '  | '
        print(header)
        print('=' * (self.size * 6 + 15))
        for _ in range(length+1): # Indexing +1
            bits = self.get_state()
            next_bit = self.next_bit()
            # Print time step, state bits, and output bit
            print(f'| {_:2}  |   ' + '   |   '.join(bits) + f'  |  next: {next_bit}')
            print('-' * (self.size * 6 + 15))  # Row separator


def main_menu():
    '''
    Implements LFSR.
    - Menu User Input
    - Choose Basic or Genral
    '''
    try:
        print('Linear Feedback Shift RegisterLFSR Implementation\n')
        print('1. Basic LFSR Implementation ')
        print('2. General (Reconfigurable) LFSR \n')
        choice = int(input('Choose Implementation: '))
        if choice == 1:
            os.system('cls')
            basic_lfsr('0110', 21)
        elif choice == 2:
            os.system('cls')
            general_lfsr()

    except Exception as e:
        print('Error : ', e)

def basic_lfsr(state, length):
    '''
    Implements LFSR with a fixed feedback function.
    - Initial state: 0110 (binary)
    - Tap positions: (4,1)
    - Length: Number of bits to generate
    '''
    state = int(state, 2)  # Convert binary string to integer
    bit_length = 4  # Fixed register size

    print('Basic LFSR Output: \n')
    print('=' * 39)
    print('|  t  |  r3   |  r2   |  r1   |  r0   |')
    print('=' * 39)

    for i in range(length):
        '''
        shifts the bits 3 places to the right
        extracts the rightmost bit (after shifting)
        '''
        next_bit = ((state >> 3) & 1) ^ (state & 1)  # XOR bits at pos 4 and 1
        bits = list(f'{state:04b}')

        # Print time step, state bits, and output bit
        print(f'|  {i:2} |   {bits[0]}   |   {bits[1]}   |   {bits[2]}   |   {bits[3]}   |  next: {next_bit}')
        print('-' * 39)  # Row separator
        state = (state >> 1) | (next_bit << (bit_length - 1))  # Shift right and insert new bit

def general_lfsr():
    '''
    Implements LFSR with a Reconfigurable feedback function.
    - Size: Input User
    - Initial state: Input User
    - Tap positions: Input User
    - Length: Number of bits to generate
    - Class Base Function
    '''
    size = int(input('size : '))
    state = input('state : ')
    taps = input('taps : ')
    length = int(input('length : '))
    taps = list(map(int, re.findall(r'\d+', taps)))

    lfsr = LFSR(size, state, taps)
    lfsr.print_state_table(length)


if __name__ == '__main__':
    main_menu()
