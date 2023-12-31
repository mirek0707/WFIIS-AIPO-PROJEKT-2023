import platform
from enum import Enum
from tkinter import filedialog

from PIL import ImageTk

from dijkstra_algorithm import dijkstra
from procimg import ProcImg
from utils import *


class Application(tk.Frame):
    def __init__(self, master=None, window_width=1280, window_height=720):
        super().__init__(master)
        self.master = master
        self.config(bg="#606060")

        self.window_width = window_width
        self.window_height = window_height
        self.pack(fill=tk.BOTH, expand=True)

        self.text = None
        self.current_image_type = None
        self.image = None
        self.original_image = None
        self.transformed_image = None
        self.steps = None

        # Transformations
        self.binarization = tk.BooleanVar()
        self.binarization.set(True)
        self.segmentation = tk.BooleanVar()
        self.segmentation.set(True)
        self.morph = tk.BooleanVar()
        self.morph.set(True)
        self.filter = tk.BooleanVar()
        self.filter.set(True)
        self.skeletonization = tk.BooleanVar()
        self.skeletonization.set(True)
        self.branch_removal = tk.BooleanVar()
        self.branch_removal.set(True)
        self.vertex_search = tk.BooleanVar()
        self.vertex_search.set(True)
        self.vertex_deduplication = tk.BooleanVar()
        self.vertex_deduplication.set(True)
        self.path_coloring = tk.BooleanVar()
        self.path_coloring.set(True)
        self.path_flooding = tk.BooleanVar()
        self.path_flooding.set(True)

        # Graph
        self.graph = None
        self.graph_image = None
        self.font_size = tk.IntVar(value=20)
        self.path_start = tk.StringVar()
        self.path_end = tk.StringVar()
        self.path_options = tk.StringVar()
        self.path_options_trigger = tk.BooleanVar()
        self.path_options_trigger.set(True)

        # Header
        self.title = tk.Label(self, text="Find fastest path", bg='black', fg='white', padx=10, pady=10)
        self.title.pack(fill=tk.X)

        # Interface frame
        self.interface_frame = tk.Frame(self, width=self.window_width * 0.2, borderwidth=1, relief="solid")
        self.interface_frame.pack_propagate(False)
        self.interface_frame.pack(side="left", fill=tk.Y)
        self.should_disable_show_buttons = tk.BooleanVar()
        self.should_disable_show_buttons.set(True)
        self.should_disable_show_graph_path_points_select = tk.BooleanVar()
        self.should_disable_show_graph_path_points_select.set(True)
        self.should_disable_show_graph_with_shortest_path = tk.BooleanVar()
        self.should_disable_show_graph_with_shortest_path.set(True)
        self.create_buttons()
        self.interface_frame.config(bg="#606060")

        # Content header
        self.content_header = tk.Label(self, bg='grey', relief='solid', borderwidth=1, padx=8, pady=8, anchor='w',
                                       fg="black")
        self.content_header.pack(fill=tk.X)
        self.set_header_text("Load image first")

        # Content frame
        self.content_frame = tk.Frame(self, borderwidth=1, relief="solid")
        self.content_frame.config(bg="#606060")
        self.content_frame.pack(side="left", fill=tk.BOTH, expand=True)

        # Footer
        self.footer = tk.Label(self.master,
                               text="Authors: Piotr Deda, Kamil Jagodziński, Aleksander Kluczka, Mirosław Kołodziej, "
                                    "Jakub Kraśniak, Adam Łaba, Paweł Sipko, Krystian Śledź",
                               bg='black', fg='white', padx=10, pady=10)
        self.footer.pack(side="bottom", fill=tk.X)

    # Methods

    def load_image(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png")])
        if filepath:
            self.original_image = self.get_image(image_path=filepath)
            self.show_original_image()
            self.handle_transformation_change()
            self.handle_graph_change()
            self.should_disable_show_buttons.set(False)

    def show_original_image(self):
        self.current_image_type = ImageType.ORIGINAL
        self.set_image(self.original_image)
        self.show_image()
        self.set_header_text("Original image")

    def show_transformed_image(self):
        self.current_image_type = ImageType.TRANSFORMED
        self.set_image(self.transformed_image)
        self.show_image()
        self.set_header_text("Transformed image")

    def handle_transformation_change(self, *_args):
        img = ProcImg(pillow_to_cv2(self.original_image))
        if self.segmentation.get():
            img.segmentation()
        if self.binarization.get():
            img.binarization()
        if self.morph.get():
            img.morph_close()
        if self.filter.get():
            img.filter()
        if self.skeletonization.get():
            img.skeletonization()
        if self.branch_removal.get():
            img.branch_removal()
        if self.vertex_search.get():
            img.vertex_search()
        if self.vertex_deduplication.get():
            img.vertex_deduplication()
        if self.path_coloring.get():
            img.path_coloring()
        if self.path_flooding.get():
            img.path_flooding()
        self.transformed_image = cv2_to_pillow(img.get_last_image())
        self.steps = img.get_steps()
        self.graph = img.get_graph()

        if self.current_image_type is ImageType.TRANSFORMED:
            self.show_transformed_image()

    def handle_font_size_change(self, *_args):
        if self.current_image_type is ImageType.WITH_GRAPH:
            self.show_image_with_graph()
        elif self.current_image_type is ImageType.WITH_GRAPH_SP:
            self.show_image_with_graph_and_shortest_path()

    def handle_graph_change(self):
        self.path_options.set(','.join([str(i) for i in range(len(self.graph.vertices))]))
        self.should_disable_show_graph_path_points_select.set(False)
        if self.current_image_type is ImageType.WITH_GRAPH:
            self.show_image_with_graph()

    def handle_path_point_change(self, *_args):
        if self.path_start.get() and self.path_end.get():
            shortest_distance, shortest_path = dijkstra(self.graph, int(self.path_start.get()),
                                                        int(self.path_end.get()))
            self.graph.set_shortest_path(shortest_path)
            self.should_disable_show_graph_with_shortest_path.set(False)
            if platform.system() != "Darwin" and self.current_image_type is ImageType.WITH_GRAPH_SP:
                self.show_image_with_graph_and_shortest_path()

    def show_image_with_graph(self):
        self.current_image_type = ImageType.WITH_GRAPH
        self.graph_image = self.graph.get_image_with_graph(self.original_image.copy(), self.font_size.get())
        self.set_image(self.graph_image)
        self.show_image()
        self.set_header_text("Original Image With Graph")

    def show_image_with_graph_and_shortest_path(self):
        self.current_image_type = ImageType.WITH_GRAPH_SP
        self.graph_image = self.graph.get_image_with_graph(self.original_image.copy(), self.font_size.get(),
                                                           with_shortest_path=True)
        self.set_image(self.graph_image)
        self.show_image()
        self.set_header_text("Original Image With Graph And Shortest Path")

    def show_step(self, step_name):
        step = next((step for step in self.steps if step.step_name == step_name), None)
        self.transformed_image = cv2_to_pillow(step.image)
        self.show_transformed_image()

    # UI

    def create_buttons(self):
        self.create_label_with_toolip(self.interface_frame, text="1. Step - data")
        self.create_button_with_tooltip(self.interface_frame, text="Load Image", command=self.load_image)
        self.create_button_with_tooltip(self.interface_frame, text="Show Original Image",
                                        command=self.show_original_image, disabled_var=self.should_disable_show_buttons)
        self.create_divider(self.interface_frame)

        self.create_label_with_toolip(self.interface_frame, text="2. Step - transformations")
        self.create_button_with_tooltip(self.interface_frame, "Show segmentation",
                                        command=lambda: self.show_step("segmentation"),
                                        disabled_var=self.should_disable_show_buttons,
                                        tooltip_text="Performs image segmentation using k-means clustering.")
        self.create_button_with_tooltip(self.interface_frame, "Show binarization",
                                        command=lambda: self.show_step("binarization"),
                                        disabled_var=self.should_disable_show_buttons,
                                        tooltip_text="Converts an input image to a binary image using "
                                                     "Otsu's thresholding.", )
        self.create_button_with_tooltip(self.interface_frame, "Show morph",
                                        command=lambda: self.show_step("morph_close"),
                                        disabled_var=self.should_disable_show_buttons,
                                        tooltip_text="Performs morphological closing on a binary image.")
        self.create_button_with_tooltip(self.interface_frame, "Show filter",
                                        command=lambda: self.show_step("filter"),
                                        disabled_var=self.should_disable_show_buttons,
                                        tooltip_text="Applies bilateral filter to an image.")
        self.create_button_with_tooltip(self.interface_frame, "Show skeletonization",
                                        command=lambda: self.show_step("skeletonization"),
                                        disabled_var=self.should_disable_show_buttons,
                                        tooltip_text="Performs skeletonization on a binary image.")
        self.create_button_with_tooltip(self.interface_frame, "Show branch removal",
                                        command=lambda: self.show_step("branch_removal"),
                                        disabled_var=self.should_disable_show_buttons,
                                        tooltip_text="Removes small branches from a skeletonized image.")
        self.create_button_with_tooltip(self.interface_frame, "Show vertex search",
                                        command=lambda: self.show_step("vertex_search"),
                                        disabled_var=self.should_disable_show_buttons,
                                        tooltip_text="Finds junction points in a skeletonized image.")
        self.create_button_with_tooltip(self.interface_frame, "Show vertex deduplication",
                                        command=lambda: self.show_step("vertex_deduplication"),
                                        disabled_var=self.should_disable_show_buttons,
                                        tooltip_text="Removes erroneous adjacent junction points from an image.")
        self.create_button_with_tooltip(self.interface_frame, "Show path coloring",
                                        command=lambda: self.show_step("path_coloring"),
                                        disabled_var=self.should_disable_show_buttons,
                                        tooltip_text="Colors the paths in an image, each with a different color.")
        self.create_button_with_tooltip(self.interface_frame, "Show path flooding",
                                        command=lambda: self.show_step("path_flooding"),
                                        disabled_var=self.should_disable_show_buttons,
                                        tooltip_text="Floods the paths in an image with their respective colors "
                                                     "and calculates path weights.")
        self.create_divider(self.interface_frame)

        self.create_label_with_toolip(self.interface_frame, text="3. Step - graph")
        self.create_slider_with_tooltip(self.interface_frame, "Font Size", self.font_size,
                                        callback=self.handle_font_size_change)
        self.create_button_with_tooltip(self.interface_frame, text="Show Image With Graph",
                                        command=self.show_image_with_graph,
                                        disabled_var=self.should_disable_show_buttons)
        self.create_select_with_tooltip(self.interface_frame, text="Select Start Point", var=self.path_start,
                                        options_var=self.path_options, callback=self.handle_path_point_change,
                                        disabled_var=self.should_disable_show_graph_path_points_select)
        self.create_select_with_tooltip(self.interface_frame, text="Select End Point", var=self.path_end,
                                        options_var=self.path_options, callback=self.handle_path_point_change,
                                        disabled_var=self.should_disable_show_graph_path_points_select)
        self.create_button_with_tooltip(self.interface_frame, text="Show Image With Shortest Path",
                                        command=self.show_image_with_graph_and_shortest_path,
                                        disabled_var=self.should_disable_show_graph_with_shortest_path)

    def show_image(self):
        self.clear_content()

        if self.image is None:
            self.set_text("No image to show")
            self.show_text(True)
            return

        image_label = tk.Label(self.content_frame, image=self.image)
        image_label.pack()

    def show_text(self, error=False):
        self.clear_content()

        if self.text is None:
            self.set_text("No text to show")
            self.show_text(True)
            return

        text_label = tk.Label(self.content_frame, text=self.text, font=("Arial", 20), fg="red" if error else "white")
        text_label.pack(anchor='w')

    def set_header_text(self, text):
        self.content_header.config(text=text)

    # UI utils

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def create_button_with_tooltip(self, frame, text, command, tooltip_text=None, disabled_var=None):
        create_button_with_tooltip(self, frame, text, command, tooltip_text, disabled_var)

    @staticmethod
    def create_divider(frame, color='black'):
        divider = tk.Frame(frame, bg=color, height=1)
        divider.pack(fill=tk.X, pady=8)

    def create_slider_with_tooltip(self, frame, text, var, from_=5, to=30, callback=None, tooltip_text=None):
        create_slider_with_tooltip(self, frame, text, var, from_=from_, to=to, callback=callback,
                                   tooltip_text=tooltip_text)

    def create_select_with_tooltip(self, frame, text, var, options_var, callback=None, tooltip_text=None,
                                   disabled_var=None):
        create_select_with_tooltip(self, frame, text, var, options_var, callback=callback, tooltip_text=tooltip_text,
                                   disabled_var=disabled_var)

    def create_label_with_toolip(self, frame, text, tooltip_text=None):
        create_label_with_toolip(self, frame, text, tooltip_text=tooltip_text)

    def get_image(self, image=None, image_path=None):
        return get_image(self, image=image, image_path=image_path)

    def set_image(self, image):
        self.image = ImageTk.PhotoImage(image)

    def set_text(self, text):
        self.text = text


class ImageType(Enum):
    ORIGINAL = 1
    TRANSFORMED = 2
    WITH_GRAPH = 3
    WITH_GRAPH_SP = 4
