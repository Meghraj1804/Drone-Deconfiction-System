import numpy as np
# import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import json
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib import cm
import os

# Inside TrajectoryVisualizer class

class TrajectoryVisualizer:
    def __init__(self, filenames, durations=None):
        self.trajectories = []
        self.filenames = filenames
        self.trajectory_names = [os.path.basename(f) for f in filenames]
        self.durations = durations or [10.0] * len(filenames)
        self.n_colors = len(filenames)
        self.colors = cm.get_cmap('tab20', self.n_colors).colors
        self.points = []
        self.positions = []
        self.start_time = None
        self.canvas = None

        self._load_trajectories()
        self._setup_plot()

    def _load_trajectories(self):
        for fname in self.filenames:
            with open(fname, "r") as f:
                data = json.load(f)
                x = np.array([p["x"] for p in data])
                y = np.array([p["y"] for p in data])
                z = np.array([p["z"] for p in data])
                self.trajectories.append((x, y, z))

    def _setup_plot(self):
        # self.fig = plt.figure()
        # self.fig = Figure()
        # self.ax = self.fig.add_subplot(111, projection='3d')
        from matplotlib.figure import Figure  # At top

        self.fig = Figure(figsize=(5, 5))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.grid(False)

        self.ax.set_xlim(-3, 3)
        self.ax.set_ylim(-3, 3)
        self.ax.set_zlim(-3, 3)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.set_zticks([])


        self.fig.canvas.mpl_connect('scroll_event', self._on_scroll)

        # Plot faded trajectories
        for i, (x, y, z) in enumerate(self.trajectories):
            # self.ax.plot(x, y, z, color=self.colors[i], alpha=0.3)
             self.ax.plot(x, y, z, color=self.colors[i], alpha=0.9, label=f"{self.filenames[i][-18:-5]}")
        self.ax.legend(loc='upper left')
        # Initialize moving points
        self.points = [self.ax.plot([], [], [], marker='o', markersize=6, color=self.colors[i])[0]
                       for i in range(self.n_colors)]

    def _on_scroll(self, event):
        base_scale = 1.1
        scale_factor = 1 / base_scale if event.button == 'up' else base_scale

        def zoom_axis(lim, scale):
            center = (lim[0] + lim[1]) / 2
            range_ = (lim[1] - lim[0]) * scale / 2
            return (center - range_, center + range_)

        self.ax.set_xlim3d(zoom_axis(self.ax.get_xlim3d(), scale_factor))
        self.ax.set_ylim3d(zoom_axis(self.ax.get_ylim3d(), scale_factor))
        self.ax.set_zlim3d(zoom_axis(self.ax.get_zlim3d(), scale_factor))

        self.fig.canvas.draw_idle()

    def _check_collision(self, pos1, pos2, threshold=0.1):
        return np.linalg.norm(np.array(pos1) - np.array(pos2)) < threshold

    def animate(self):
        
        self.start_time = time.perf_counter()
        self._animation_running = True
        self._update_loop()

  
    def _update_loop(self):
        if not self._animation_running or not self.canvas:
            return

        now = time.perf_counter()
        elapsed = now - self.start_time
        all_done = True
        positions = []

        for i, (x, y, z) in enumerate(self.trajectories):
            total_time = self.durations[i]
            progress = min(elapsed / total_time, 1.0)
            if progress < 1.0:
                all_done = False

            index = int(progress * (len(x) - 1))
            pos = (x[index], y[index], z[index])
            positions.append(pos)

            self.points[i].set_data([pos[0]], [pos[1]])
            self.points[i].set_3d_properties([pos[2]])

        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                if self._check_collision(positions[i], positions[j]):
                    if self.collision_callback:
                        self.collision_callback(
                            self.trajectory_names[i],
                            self.trajectory_names[j],
                            positions[i],
                            elapsed
                        )

        self.canvas.draw()

        if not all_done:
            self.canvas.get_tk_widget().after(10, self._update_loop)


            
    def set_collision_callback(self, callback):
        self.collision_callback = callback

    def show_on(self, parent_widget):
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent_widget)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                
    def _color_name(self, rgb):
        import matplotlib.colors as mcolors
        return mcolors.to_hex(rgb)
    
    def stop(self):
        # Stop ongoing animation loop by setting flag
        self._animation_running = False
        # Safely destroy the canvas if it exists
        if hasattr(self, "canvas") and self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None


# if __name__ == "__main__":
#     import os

#     # Example test files (make sure these exist relative to the script location)
#     test_dir = os.path.join(os.path.dirname(__file__), "trajectories")
#     test_files = [
#         os.path.join(test_dir, "trajectory_01.json"),
#         os.path.join(test_dir, "trajectory_02.json"),
#         os.path.join(test_dir, "trajectory_03.json"),
#     ]

#     visualizer = TrajectoryVisualizer(test_files)
#     visualizer.animate()
