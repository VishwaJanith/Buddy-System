from tkinter import Tk, Canvas

class BuddySystem:
    def __init__(self, total_memory, gui):
        self.total_memory = total_memory
        self.memory = {total_memory: [(0, total_memory)]}  # Dictionary: size -> list of free blocks
        self.allocated = []  # List to track allocated blocks
        self.gui = gui  # Link to the GUI

    def allocate(self, size):
        block_size = self._find_nearest_power_of_two(size)

        while block_size <= self.total_memory:
            if block_size in self.memory and self.memory[block_size]:
                # Allocate the first available block of the required size
                block = self.memory[block_size].pop(0)
                self.allocated.append((block[0], block[1], block_size))  # Track allocated block with size
                print(f"Allocated {size} KB at address {block[0]}.")
                self.gui.visualize(self.memory, self.allocated)  # Update GUI after allocation
                return block

            # If no block is available, attempt to split larger blocks
            if not self._split_block(block_size):
                break

        print(f"Error: Unable to allocate {size} KB.")
        return None

    def deallocate(self, block):
        # Find the block in the allocated list by start and end address
        for allocated_block in self.allocated:
            if allocated_block[0] == block[0] and allocated_block[1] == block[1]:
                self.allocated.remove(allocated_block)  # Remove from allocated list
                size = allocated_block[2]
                self.memory.setdefault(size, []).append(block)  # Add back to free memory
                print(f"Deallocated block at address {block[0]} of size {size} KB.")
                self._merge_buddies(size, block)
                self.gui.visualize(self.memory, self.allocated)  # Update GUI after deallocation
                return

        print(f"Error: Block {block} not found in allocated memory.")

    def _find_nearest_power_of_two(self, size):
        power = 1
        while power < size:
            power *= 2
        return power

    def _split_block(self, size):
        larger_size = size * 2
        while larger_size <= self.total_memory:
            if larger_size in self.memory and self.memory[larger_size]:
                # Split a larger block into two smaller buddies
                block = self.memory[larger_size].pop(0)
                mid = (block[0] + block[1]) // 2
                smaller_size = larger_size // 2
                self.memory.setdefault(smaller_size, []).append((block[0], mid))
                self.memory[smaller_size].append((mid, block[1]))
                return True
            larger_size *= 2
        return False

    def _merge_buddies(self, size, block):
        buddy_address = block[0] ^ size  # XOR to find buddy address
        buddy = (buddy_address, buddy_address + size)

        if buddy in self.memory.get(size, []):
            self.memory[size].remove(buddy)
            self.memory[size].remove(block)
            merged_block = (min(block[0], buddy[0]), max(block[1], buddy[1]))
            self.memory.setdefault(size * 2, []).append(merged_block)
            print(f"Merged {size} KB blocks at addresses {block[0]} and {buddy[0]} into {size * 2} KB block.")
            self._merge_buddies(size * 2, merged_block)

    def display_memory(self):
        print("Memory State:")
        # Display free blocks
        for size in sorted(self.memory.keys(), reverse=True):
            for block in self.memory[size]:
                print(f"  1 block of {size} KB (free)")
        # Display allocated blocks
        for block in self.allocated:
            print(f"  1 block of {block[2]} KB (allocated)")

class BuddySystemGUI:
    def __init__(self, total_memory):
        self.total_memory = total_memory
        self.window = Tk()
        self.window.title("Buddy System Memory Visualization")
        self.canvas = Canvas(self.window, width=600, height=400, bg="white")
        self.canvas.pack()
        self.blocks = []  # Keep track of displayed blocks
        self._draw_memory_bar()

    def _draw_memory_bar(self):
        self.canvas.create_rectangle(50, 100, 550, 300, outline="black", width=2)
        self.blocks.append((50, 100, 550, 300))  # Entire memory block

    def visualize(self, memory, allocated):
        self.canvas.delete("block")  # Clear old visualization
        for size in memory:
            for block in memory[size]:
                x1, y1, x2, y2 = self._scale_block(block)
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="green", tags="block")
        for block in allocated:
            x1, y1, x2, y2 = self._scale_block(block)
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="red", tags="block")

    def _scale_block(self, block):
        scale_factor = 500 / self.total_memory
        return 50 + block[0] * scale_factor, 100, 50 + block[1] * scale_factor, 300

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    gui = BuddySystemGUI(1024)
    buddy_system = BuddySystem(1024, gui)  # Pass GUI instance to BuddySystem
    buddy_system.display_memory()

    print("\nStep 1: Allocate 100 KB")
    block1 = buddy_system.allocate(100)
    buddy_system.display_memory()

    print("\nStep 2: Allocate 200 KB")
    block2 = buddy_system.allocate(200)
    buddy_system.display_memory()

    print("\nStep 3: Allocate 128 KB")
    block3 = buddy_system.allocate(128)
    buddy_system.display_memory()

    print("\nStep 3: Deallocate 128 KB block")
    buddy_system.deallocate(block1)
    buddy_system.display_memory()

    print("\nStep 3: Deallocate 128 KB block")
    buddy_system.deallocate(block3)
    buddy_system.display_memory()

    

    gui.run()  # Start the GUI loop
