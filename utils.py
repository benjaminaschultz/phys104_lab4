from matplotlib import pyplot as plt
from IPython.display import display, clear_output
from ipywidgets import widgets
import time
import numpy as np
from matplotlib.patches import Circle


class OneDimensionalCollision(object):

    def __init__(self):

        self.fig = plt.figure(figsize=(7, 4))
        self.col_ax = self.fig.add_subplot(111)
        self.m2 = 5
        self.v2i = -6

        self.m1_selector_widget = widgets.FloatSlider(
            value=4.0,
            min=1.0,
            max=10.0,
            step=0.1,
            description='m_1 (kg):',
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='.1f',
        )
        self.m1_selector_widget.observe(self.refresh)

        self.v1_selector_widget = widgets.FloatSlider(
            value=6.0,
            min=1.0,
            max=10.0,
            step=0.1,
            description='v1_init (m/s):',
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='.1f',
        )
        self.v1_selector_widget.observe(self.refresh)

        self.generate_data()

        self.sweep_selector = widgets.SelectionSlider(
            options=[('{:0.2f}'.format(t), i) for i, t in enumerate(sorted(self.ts))],
            description='time = ',
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            layout=widgets.Layout(width='60%')
        )

        self.sweep_selector.observe(self.redraw)

        self.play_button = widgets.Button(description='Play')
        self.play_button.on_click(self.play)

        self.image_widget = widgets.Image(
            format='png',
            width=600,
        )

        self.v1_f_label = widgets.Label(f'v_1f: {self.v1f:0.2f} m/s')
        self.v2_f_label = widgets.Label(f'v_2f: {self.v2f:0.2f} m/s')

        self.control_panel = widgets.VBox([
            self.image_widget,
            widgets.VBox([
                self.m1_selector_widget,
                self.v1_selector_widget,
            ]),
            widgets.HBox([
                self.sweep_selector,
                self.play_button,
            ]),
            widgets.VBox([
                self.v1_f_label,
                self.v2_f_label,
            ])
        ])

        self.refresh()
        self.display_frame(0)
        self.interact()

    def play(self, event):
        for i in range(len(self.ts)):
            self.sweep_selector.value = i
            self.display_frame(i)
            time.sleep(1.0 / 24.)

    def generate_data(self, change=None):
        self.m1 = self.m1_selector_widget.value
        self.v1i = self.v1_selector_widget.value
        self.ts, self.x1s, self.x2s = self.gen_1d_collision_data()

    def refresh(self, change=None):
        if change and change['name'] != 'value':
            return

        progress = widgets.IntProgress(
            value=0,
            min=0,
            max=len(self.ts),
            step=1
        )
        self.control_panel.children = (
            widgets.Label('simulating data'),
            progress,
        )

        self.generate_data()
        for i, t in enumerate(self.ts):
            self.render_frame(i)
            progress.value = i

        self.v1_f_label = widgets.Label(f'v_1f: {self.v1f:0.2f} m/s')
        self.v2_f_label = widgets.Label(f'v_2f: {self.v2f:0.2f} m/s')

        self.control_panel.children = (
            self.image_widget,
            widgets.VBox([
                self.m1_selector_widget,
                self.v1_selector_widget,
            ]),
            widgets.HBox([
                self.sweep_selector,
                self.play_button,
            ]),
            widgets.VBox([
                self.v1_f_label,
                self.v2_f_label,
            ])
        )

        self.display_frame(self.sweep_selector.value)

    def redraw(self, change=None):
        self.display_frame(self.sweep_selector.value)

    def gen_1d_collision_data(self, tc=1, tf=2):

        m1 = self.m1
        v1i = self.v1i

        m2 = self.m2
        v2i = self.v2i

        n_steps = 12
        ts_bc = np.linspace(0, tc, n_steps)
        ts_ac = np.linspace(tc, tf, n_steps)
        x10 = -v1i * tc
        x20 = -v2i * tc

        x1_offset = np.sqrt(m1)
        x2_offset = np.sqrt(m2)

        v1f = (m1 * v1i - m2 * v1i + 2 * m2 * v2i) / (m1 + m2)
        v2f = v1i - v2i + v1f

        v2f = v1f + v1i - v2i
        self.v1f = v1f
        self.v2f = v2f

        x1s = np.concatenate((x10 + ts_bc * v1i, (ts_ac - tc) * v1f)) - x1_offset
        x2s = np.concatenate((x20 + ts_bc * v2i, (ts_ac - tc) * v2f)) + x2_offset
        ts = np.concatenate((ts_bc, ts_ac))
        return ts, x1s, x2s

    def render_frame(self, frame):
        x1 = self.x1s[frame]
        x2 = self.x2s[frame]

        self.col_ax.clear()
        self.col_ax.set_ylim(-5, 5)
        self.col_ax.set_xlim(
            min(np.min(self.x1s), np.min(self.x2s)),
            max(np.max(self.x1s), np.max(self.x2s)),
        )

        self.col_ax.set_aspect('equal')
        particle1 = Circle([x1, 0], radius=np.sqrt(self.m1), facecolor='red', alpha=0.5)
        particle2 = Circle([x2, 0], radius=np.sqrt(self.m2), facecolor='blue', alpha=0.5)

        self.col_ax.add_patch(particle1)
        self.col_ax.add_patch(particle2)
        self.fig.savefig(f'frame{frame}.png')

    def display_frame(self, frame):
        file = open(f"frame{frame}.png", "rb")
        image = file.read()
        self.image_widget.value = image

    def interact(self):
        display(self.control_panel)


class TwoDimensionalCollision(object):

    def __init__(self):

        self.fig = plt.figure(figsize=(7, 4))
        self.col_ax = self.fig.add_subplot(111)
        self.m2 = 5
        self.v2x = -4
        self.v2y = 3

        self.m1_selector_widget = widgets.FloatSlider(
            value=4.0,
            min=1.0,
            max=10.0,
            step=0.1,
            description='m_1 (kg):',
            orientation='horizontal',
            readout=True,
            continuous_update=False,
            readout_format='.1f',
        )
        self.m1_selector_widget.observe(self.refresh)

        self.v1x_selector_widget = widgets.FloatSlider(
            value=6.0,
            min=1.0,
            max=10.0,
            step=0.1,
            description='v1x (m/s):',
            orientation='horizontal',
            continuous_update=False,
            readout=True,
            readout_format='.1f',
        )
        self.v1y_selector_widget = widgets.FloatSlider(
            value=6.0,
            min=1.0,
            max=10.0,
            step=0.1,
            description='v1y (m/s):',
            orientation='horizontal',
            continuous_update=False,
            readout=True,
            readout_format='.1f',
        )
        self.v1x_selector_widget.observe(self.refresh)
        self.v1y_selector_widget.observe(self.refresh)

        self.generate_data()

        self.sweep_selector = widgets.SelectionSlider(
            options=[('{:0.2f}'.format(t), i) for i, t in enumerate(sorted(self.ts))],
            description='time = ',
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            layout=widgets.Layout(width='60%')
        )

        self.sweep_selector.observe(self.redraw)

        self.play_button = widgets.Button(description='Play')
        self.play_button.on_click(self.play)

        self.image_widget = widgets.Image(
            format='png',
            width=600,
        )

        self.v3x_label = widgets.Label(f'v_3x: {self.v3x:0.2f} m/s')
        self.v3y_label = widgets.Label(f'v_3y: {self.v3y:0.2f} m/s')

        self.control_panel = widgets.VBox([
            self.image_widget,
            widgets.VBox([
                self.m1_selector_widget,
                self.v1x_selector_widget,
                self.v1y_selector_widget,
            ]),
            widgets.VBox([
                self.sweep_selector,
                self.play_button,
            ]),
            widgets.VBox([
                self.v3x_label,
                self.v3y_label,
            ])
        ])

        self.refresh()
        self.display_frame(0)
        self.interact()

    def play(self, event):
        for i in range(len(self.ts)):
            self.sweep_selector.value = i
            self.display_frame(i)
            time.sleep(1.0 / 24.)

    def generate_data(self, change=None):
        self.m1 = self.m1_selector_widget.value
        self.m3 = self.m1 + self.m2
        self.v1x = self.v1x_selector_widget.value
        self.v1y = self.v1y_selector_widget.value
        self.gen_2d_collision_data()

    def refresh(self, change=None):
        if change and change['name'] != 'value':
            return

        self.generate_data()

        progress = widgets.IntProgress(
            value=0,
            min=0,
            max=len(self.ts),
            step=1
        )
        self.control_panel.children = (
            widgets.Label('Simulating data'),
            progress,
        )

        self.generate_data()
        for i, t in enumerate(self.ts):
            self.render_frame(i)
            progress.value = i

        self.control_panel.children = (
            self.image_widget,
            widgets.VBox([
                self.m1_selector_widget,
                self.v1x_selector_widget,
                self.v1y_selector_widget,
            ]),
            widgets.VBox([
                self.sweep_selector,
                self.play_button,
            ]),
            widgets.VBox([
                self.v3x_label,
                self.v3y_label,
            ])
        )

        self.display_frame(self.sweep_selector.value)

    def redraw(self, change=None):
        self.display_frame(self.sweep_selector.value)

    def gen_2d_collision_data(self, tc=1, tf=2):
        m1 = self.m1
        m2 = self.m2
        m3 = self.m3

        v1x = self.v1x
        v1y = self.v1y
        v2x = self.v2x
        v2y = self.v2y

        m3 = m1 + m2
        v3x = (m1 * v1x + m2 * v2x) / m3
        v3y = (m1 * v1y + m2 * v2y) / m3

        n_steps = 24
        ts_bc = np.linspace(0, tc, n_steps)
        ts_ac = np.linspace(tc, tf, n_steps)

        x10 = -v1x * tc
        x20 = -v2x * tc

        y10 = -v1y * tc
        y20 = -v2y * tc

        x1s = x10 + ts_bc * v1x
        y1s = y10 + ts_bc * v1y

        x2s = x20 + ts_bc * v2x
        y2s = y20 + ts_bc * v2y

        x3s = v3x * (ts_ac - tc)
        y3s = v3y * (ts_ac - tc)

        self.v3x = v3x
        self.v3y = v3y

        self.x1s = x1s
        self.y1s = y1s
        self.x2s = x2s
        self.y2s = y2s
        self.x3s = x3s
        self.y3s = y3s
        self.ts_bc = ts_bc
        self.ts_ac = ts_ac
        self.ts = np.concatenate((ts_bc, ts_ac))

    def render_frame(self, frame):
        self.col_ax.clear()
        self.col_ax.set_ylim(-10, 10)
        self.col_ax.set_xlim(-10, 10)
        self.col_ax.set_aspect('equal')

        if frame >= 24:
            x3 = self.x3s[frame - 24]
            y3 = self.y3s[frame - 24]
            particle1 = Circle([x3, y3], radius=np.sqrt(self.m3), facecolor='purple', alpha=0.5)
            self.col_ax.add_patch(particle1)

        else:
            x1 = self.x1s[frame]
            x2 = self.x2s[frame]
            y1 = self.y1s[frame]
            y2 = self.y2s[frame]

            particle1 = Circle([x1, y1], radius=np.sqrt(self.m1), facecolor='red', alpha=0.5)
            particle2 = Circle([x2, y2], radius=np.sqrt(self.m2), facecolor='blue', alpha=0.5)
            self.col_ax.add_patch(particle1)
            self.col_ax.add_patch(particle2)

        self.fig.savefig(f'frame_2d_{frame}.png')

    def display_frame(self, frame):
        file = open(f"frame_2d_{frame}.png", "rb")
        image = file.read()
        self.image_widget.value = image

    def interact(self):
        display(self.control_panel)
