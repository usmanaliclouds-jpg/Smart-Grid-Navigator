import tkinter as tk
from tkinter import messagebox
import heapq
import random
import time

class PathfindingAgent:
    def __init__(self, win):
        self.win = win
        self.win.title("Smart Grid Navigator")
        self.win.configure(bg="#1e1e2e")
        
        self.rows = 15
        self.cols = 15
        self.size = 30
        self.density = 0.3
        
        self.start = (2, 2)
        self.goal = (4,4)
        self.agent_pos = self.start
        
        self.walls = set()
        self.current_path = []
        self.running = False
        
        self.make_gui()

    def make_gui(self):
        top_frame = tk.Frame(self.win, bg="#1e1e2e")
        top_frame.pack(pady=8)
        
        tk.Label(top_frame, text="Rows:", bg="#1e1e2e", fg="#cdd6f4", font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.row_entry = tk.Entry(top_frame, width=5, bg="#313244", fg="#cdd6f4", insertbackground="#cdd6f4", relief="flat")
        self.row_entry.insert(0, str(self.rows))
        self.row_entry.pack(side=tk.LEFT, padx=2)
        
        tk.Label(top_frame, text="Cols:", bg="#1e1e2e", fg="#cdd6f4", font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.col_entry = tk.Entry(top_frame, width=5, bg="#313244", fg="#cdd6f4", insertbackground="#cdd6f4", relief="flat")
        self.col_entry.insert(0, str(self.cols))
        self.col_entry.pack(side=tk.LEFT, padx=2)

        tk.Button(top_frame, text="Resize Grid", command=self.update_grid_size,
                  bg="#89b4fa", fg="#1e1e2e", relief="flat", font=("Segoe UI", 9, "bold"),
                  padx=8, cursor="hand2").pack(side=tk.LEFT, padx=10)

        mid_frame = tk.Frame(self.win, bg="#1e1e2e")
        mid_frame.pack(pady=5)
        
        self.algo_var = tk.StringVar(value="A*")
        tk.OptionMenu(mid_frame, self.algo_var, "A*", "Greedy BFS").pack(side=tk.LEFT, padx=5)
        
        self.heur_var = tk.StringVar(value="Manhattan")
        tk.OptionMenu(mid_frame, self.heur_var, "Manhattan", "Euclidean").pack(side=tk.LEFT, padx=5)

        btn_frame = tk.Frame(self.win, bg="#1e1e2e")
        btn_frame.pack(pady=6)
        
        tk.Button(btn_frame, text="▶ Run Agent", command=self.start_agent,
                  bg="#a6e3a1", fg="#1e1e2e", relief="flat", font=("Segoe UI", 9, "bold"),
                  padx=10, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="⚡ Generate Maze", command=self.make_random_map,
                  bg="#f38ba8", fg="#1e1e2e", relief="flat", font=("Segoe UI", 9, "bold"),
                  padx=10, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="↺ Reset", command=self.clear_board,
                  bg="#fab387", fg="#1e1e2e", relief="flat", font=("Segoe UI", 9, "bold"),
                  padx=10, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        self.stats = tk.Label(self.win, text="Nodes Expanded: 0 | Cost: 0 | Time: 0ms",
                              bg="#1e1e2e", fg="#a6adc8", font=("Segoe UI", 9))
        self.stats.pack(pady=3)

        self.canvas = tk.Canvas(self.win, bg="#1e1e2e", highlightthickness=0)
        self.canvas.pack(padx=10, pady=8)
        self.canvas.bind("<Button-1>", self.toggle_wall)
        self.canvas.bind("<B1-Motion>", self.add_wall_drag)
        
        self.draw_boxes()

    def update_grid_size(self):
        try:
            self.rows = int(self.row_entry.get())
            self.cols = int(self.col_entry.get())
            self.start = (0, 0)
            self.goal = (self.rows-1, self.cols-1)
            self.clear_board()
        except ValueError:
            messagebox.showerror("Error", "Rows and Cols must be numbers!")

    def clear_board(self):
        self.walls.clear()
        self.running = False
        self.agent_pos = self.start
        self.current_path = []
        self.draw_boxes()

    def draw_boxes(self):
        self.canvas.config(width=self.cols * self.size, height=self.rows * self.size)
        self.canvas.delete("all")
        self.rects = {}
        
        for r in range(self.rows):
            for c in range(self.cols):
                color = "#313244"
                if (r, c) == self.agent_pos: color = "#ffffff"
                elif (r, c) == self.goal: color = "#f38ba8"
                elif (r, c) in self.walls: color = "#e64553"
                
                x1, y1 = c * self.size, r * self.size
                x2, y2 = x1 + self.size, y1 + self.size
                
                self.rects[(r, c)] = self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#1e1e2e")

    def toggle_wall(self, event):
        r, c = event.y // self.size, event.x // self.size
        if 0 <= r < self.rows and 0 <= c < self.cols and (r, c) not in [self.start, self.goal, self.agent_pos]:
            if (r, c) in self.walls:
                self.walls.remove((r, c))
                self.canvas.itemconfig(self.rects[(r, c)], fill="#313244")
            else:
                self.walls.add((r, c))
                self.canvas.itemconfig(self.rects[(r, c)], fill="#e64553")

    def add_wall_drag(self, event):
        r, c = event.y // self.size, event.x // self.size
        if 0 <= r < self.rows and 0 <= c < self.cols and (r, c) not in [self.start, self.goal, self.agent_pos]:
            self.walls.add((r, c))
            self.canvas.itemconfig(self.rects[(r, c)], fill="#45475a")

    def make_random_map(self):
        self.clear_board()
        for r in range(self.rows):
            for c in range(self.cols):
                if random.random() < self.density and (r, c) not in [self.start, self.goal]:
                    self.walls.add((r, c))
        self.draw_boxes()

    def get_h(self, node, target):
        r1, c1 = node
        r2, c2 = target
        if self.heur_var.get() == "Manhattan":
            return abs(r1 - r2) + abs(c1 - c2)
        return ((r1 - r2)**2 + (c1 - c2)**2)**0.5

    def get_neighbors(self, node):
        r, c = node
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols and (nr, nc) not in self.walls:
                neighbors.append((nr, nc))
        return neighbors

    def find_path(self, start_node):
        start_t = time.time()
        pq = [(0, 0, start_node, [start_node])]
        visited_costs = {start_node: 0}
        nodes_expanded = 0
        
        for r in range(self.rows):
            for c in range(self.cols):
                if (r,c) not in self.walls and (r,c) not in [self.agent_pos, self.goal]:
                    self.canvas.itemconfig(self.rects[(r,c)], fill="#313244")

        while pq:
            f, g, curr, path = heapq.heappop(pq)
            nodes_expanded += 1
            
            if curr != start_node and curr != self.goal:
                self.canvas.itemconfig(self.rects[curr], fill="#89dceb")
            
            if curr == self.goal:
                exec_time = int((time.time() - start_t) * 1000)
                self.stats.config(text=f"Nodes Expanded: {nodes_expanded} | Cost: {g} | Time: {exec_time}ms")
                
                for node in path:
                    if node != start_node and node != self.goal:
                        self.canvas.itemconfig(self.rects[node], fill="#cba6f7")
                        
                return path

            for n in self.get_neighbors(curr):
                new_g = g + 1
                if n not in visited_costs or new_g < visited_costs[n]:
                    visited_costs[n] = new_g
                    h = self.get_h(n, self.goal)
                    priority = (new_g + h) if self.algo_var.get() == "A*" else h
                    
                    heapq.heappush(pq, (priority, new_g, n, path + [n]))
                    if n != self.goal:
                        self.canvas.itemconfig(self.rects[n], fill="#f9e2af")
                        
            self.win.update()
        return None

    def start_agent(self):
        if self.running: return
        self.running = True
        self.current_path = self.find_path(self.agent_pos)
        
        if self.current_path:
            self.move_agent()
        else:
            messagebox.showinfo("Done", "No path found!")
            self.running = False

    def move_agent(self):
        if not self.running or not self.current_path:
            return
            
        next_step = self.current_path.pop(0)
        
        if self.agent_pos != self.start:
            self.canvas.itemconfig(self.rects[self.agent_pos], fill="#cba6f7")
            
        self.agent_pos = next_step
        
        if self.agent_pos != self.goal:
            self.canvas.itemconfig(self.rects[self.agent_pos], fill="#ffffff")
        
        if self.agent_pos == self.goal:
            messagebox.showinfo("Success", "Target Reached!")
            self.running = False
            return

        if random.random() < 0.05:
            empty_spots = [(r, c) for r in range(self.rows) for c in range(self.cols) 
                           if (r, c) not in self.walls and (r, c) not in [self.agent_pos, self.goal]]
            if empty_spots:
                new_wall = random.choice(empty_spots)
                self.walls.add(new_wall)
                self.canvas.itemconfig(self.rects[new_wall], fill="#e64553")
                
                if new_wall in self.current_path:
                    self.current_path = self.find_path(self.agent_pos)
                    if not self.current_path:
                        messagebox.showinfo("Trapped", "Obstacles completely blocked the path!")
                        self.running = False
                        return

        self.win.after(300, self.move_agent)

if __name__ == "__main__":
    root = tk.Tk()
    app = PathfindingAgent(root)
    root.mainloop()
