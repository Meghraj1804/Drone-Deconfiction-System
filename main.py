import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from visualization_module import TrajectoryVisualizer
import threading
import os


class TrajectoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Trajectory Visualizer")
        self.root.attributes('-fullscreen', True)

        self.filenames = []
        self.durations = []
        self.visualizer = None

        self._build_layout()

    def _build_layout(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # === Left: Visualization ===
        self.left_frame = tk.Frame(self.main_frame, bg="white")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # === Right: Controls ===
        self.right_frame = tk.Frame(self.main_frame, padx=10, pady=10)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # File selection
        self.load_button = tk.Button(self.right_frame, text="Load Trajectories", command=self.load_files)
        self.load_button.pack(pady=(0, 10))


        
        # === Trajectory Table ===
        self.traj_label = tk.Label(self.right_frame, text="Trajectories & Durations:")
        self.traj_label.pack(pady=(5, 0))

        self.traj_table_frame = tk.Frame(self.right_frame)
        self.traj_table_frame.pack(fill=tk.X, pady=(0, 10))

        self.traj_rows = []  # Will hold tuples of (filename_label, duration_entry)


        # Start animation button
        self.start_button = tk.Button(self.right_frame, text="Start Animation", command=self.start_animation, state=tk.DISABLED)
        self.start_button.pack(pady=(10, 5))

        # Collision report table
        self.report_label = tk.Label(self.right_frame, text="Collision Report:")
        self.report_label.pack(pady=(10, 5))
        self.report_table = ttk.Treeview(self.right_frame, columns=("dots", "coord", "time"), show="headings", height=10)
        self.report_table.heading("dots", text="Drones")
        self.report_table.heading("coord", text="Coordinates")
        self.report_table.heading("time", text="Time (s)")
        self.report_table.pack(fill=tk.X, pady=5)

        # Quit button
        self.quit_button = tk.Button(self.right_frame, text="Quit", command=self.root.quit)
        self.quit_button.pack(pady=10)

    def load_files(self):
        files = filedialog.askopenfilenames(
            title="Select Trajectory JSON Files",
            filetypes=[("JSON files", "*.json")]
        )

        if not files:
            return

        self.filenames = list(files)

        # Clear previous entries
        for widget in self.traj_table_frame.winfo_children():
            widget.destroy()
        self.traj_rows.clear()

        # Populate table
        for i, file in enumerate(self.filenames):
            filename = os.path.basename(file)

            label = tk.Label(self.traj_table_frame, text=filename[:-5])
            label.grid(row=i, column=0, sticky="w", padx=5, pady=2)

            entry = tk.Entry(self.traj_table_frame, width=10)
            entry.insert(0, "10.0")  # default duration
            entry.grid(row=i, column=1, padx=5, pady=2)

            self.traj_rows.append((label, entry))

        self.start_button.config(state=tk.NORMAL)


    def start_animation(self):
        # Validate durations
        durations = []
        for _, entry in self.traj_rows:
            try:
                val = float(entry.get().strip())
                if val < 2.0:
                    raise ValueError
                durations.append(val)
            except ValueError:
                messagebox.showerror(
                    "Invalid Duration",
                    "Each duration must be a number and at least 2 seconds."
                )
                return

        # Clear previous collision report
        for item in self.report_table.get_children():
            self.report_table.delete(item)

        # Stop and destroy previous visualizer
        if self.visualizer:
            self.visualizer.stop()
            self.visualizer = None

        # Clear left_frame (old canvas)
        for widget in self.left_frame.winfo_children():
            widget.destroy()

        # Threaded run to keep UI responsive
        def run():
            self.visualizer = TrajectoryVisualizer(
                filenames=self.filenames,
                durations=durations
            )

            def report_callback(name1, name2, pos, t):
                dots = f"{os.path.basename(name1)[:-5]} & {os.path.basename(name2)[:-5]}"
                coord = f"({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})"
                time_str = f"{t:.2f}"
                self.report_table.insert("", "end", values=(dots, coord, time_str))

            self.visualizer.set_collision_callback(report_callback)
            self.visualizer.show_on(self.left_frame)
            self.visualizer.animate()

        threading.Thread(target=run, daemon=True).start()



if __name__ == "__main__":
    root = tk.Tk()
    app = TrajectoryApp(root)
    root.mainloop()
