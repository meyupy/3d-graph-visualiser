import os
import pandas
import math
import pygame

pygame.init()

W = 1280

AXES_LENGTH, AXES_THICKNESS = W // 4, W // 256
GRAPH_CENTER_X, GRAPH_CENTER_Y = 9 * W // 32, 9 * W // 32
RECTS_CENTER_X, RECTS_CENTER_Y = 25 * W // 32, 3 * W // 16
RECTS_CIRCLE_RADIUS, RECT_WIDTH = 9 * W // 64, W // 64

GUI_FONT_SMALL = pygame.font.Font(None, W // 64)
GUI_FONT_MEDIUM = pygame.font.Font(None, 3 * W // 128)
GUI_FONT_LARGE = pygame.font.Font(None, W // 32)

BG_COLOR, BG_PANEL_COLOR = (191, 191, 191), (127, 127, 127)
BUTTON_COLOR_1_1, BUTTON_COLOR_1_2 = (175, 175, 175), (167, 167, 167)
BUTTON_COLOR_2_1, BUTTON_COLOR_2_2 = (143, 143, 143), (135, 135, 135)
TEXT_COLOR_1, TEXT_COLOR_2 = (127, 127, 127), (95, 95, 95)
RECT_COLOR_1_1, RECT_COLOR_1_2 = (143, 143, 143), (135, 135, 135)
RECT_COLOR_2_1, RECT_COLOR_2_2 = (111, 111, 111), (119, 119, 119)
RECT_COLOR_3_1, RECT_COLOR_3_2 = (79, 79, 79), (87, 87, 87)
AXES_COLOR, AXES_MIN_COLOR, AXES_MAX_COLOR = (95, 95, 95), (127, 127, 191), (191, 127, 127)
DOT_COLOR, DOT_CHOSEN_COLOR = (191, 63, 63), (223, 127, 0)

OUTPUTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'outputs')
USER_INPUTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_inputs')

SCREEN = pygame.display.set_mode((W, 9 * W // 16))
CLOCK = pygame.time.Clock()
pygame.display.set_caption("Third Dimensional Graph Visualiser")

bg_panel_rect = pygame.rect.Rect(9 * W // 16, 0, 7 * W // 16, 9 * W // 16)


class Button:

    def __init__(self, surface, text, font, x, y, width, height,
                 button_color_1, button_color_2, text_color, border_radius):
        self.surface = surface
        self.font = font
        self.button_color_1 = button_color_1
        self.button_color_2 = button_color_2
        self.color = button_color_1
        self.text_color = text_color
        self.border_radius = border_radius
        self.body_rect = pygame.rect.Rect(x, y, width, height)
        self.text = text
        self.text_surf = font.render(text, True, text_color)
        self.text_rect = self.text_surf.get_rect(center=self.body_rect.center)
        self.press_allowed = True
        self.pressed = False

    def is_clicked(self):
        mouse_pressed = pygame.mouse.get_pressed()[0]
        if self.body_rect.collidepoint(pygame.mouse.get_pos()):
            if mouse_pressed:
                self.pressed = True
            elif self.pressed and self.press_allowed:
                self.pressed = False
                return True
        else:
            self.pressed = False
            if mouse_pressed:
                self.press_allowed = False
            else:
                self.press_allowed = True
        return False

    def draw(self, text):
        if not (text is None or self.text == text):
            self.text = text
            self.text_surf = self.font.render(text, True, self.text_color)
            self.text_rect = self.text_surf.get_rect(center=self.body_rect.center)
        if self.body_rect.collidepoint(pygame.mouse.get_pos()):
            self.color = self.button_color_2
        else:
            self.color = self.button_color_1
        pygame.draw.rect(self.surface, self.color, self.body_rect, border_radius=self.border_radius)
        self.surface.blit(self.text_surf, self.text_rect)


button_hide_graph = Button(SCREEN, "Hide Graph", GUI_FONT_SMALL, W // 32, W // 32, W // 16, W // 32,
                           BUTTON_COLOR_1_1, BUTTON_COLOR_1_2, TEXT_COLOR_1, W // 128)
button_hide_dots = Button(SCREEN, "Hide Dots", GUI_FONT_SMALL, W // 32, 5 * W // 64, W // 16, W // 32,
                          BUTTON_COLOR_1_1, BUTTON_COLOR_1_2, TEXT_COLOR_1, W // 128)
button_reset_graph = Button(SCREEN, "Reset Graph", GUI_FONT_SMALL, 7 * W // 64, W // 32, W // 16, W // 32,
                            BUTTON_COLOR_1_1, BUTTON_COLOR_1_2, TEXT_COLOR_1, W // 128)
button_reset_all = Button(SCREEN, "Reset All", GUI_FONT_SMALL, 25 * W // 64, W // 32, W // 16, W // 32,
                          BUTTON_COLOR_1_1, BUTTON_COLOR_1_2, TEXT_COLOR_1, W // 128)
button_get_input = Button(SCREEN, "Get Input", GUI_FONT_SMALL, 15 * W // 32, W // 32, W // 16, W // 32,
                          BUTTON_COLOR_1_1, BUTTON_COLOR_1_2, TEXT_COLOR_1, W // 128)
button_save_data = Button(SCREEN, "Save Data", GUI_FONT_SMALL, 15 * W // 32, 5 * W // 64, W // 16, W // 32,
                          BUTTON_COLOR_1_1, BUTTON_COLOR_1_2, TEXT_COLOR_1, W // 128)
button_new_dot = Button(SCREEN, "New Dot", GUI_FONT_MEDIUM, 39 * W // 64,  7 * W // 16, 3 * W // 32, W // 32,
                        BUTTON_COLOR_2_1, BUTTON_COLOR_2_2, TEXT_COLOR_2, W // 128)
button_remove = Button(SCREEN, "Remove", GUI_FONT_MEDIUM, 39 * W // 64, W // 2, 3 * W // 32, W // 32,
                       BUTTON_COLOR_2_1, BUTTON_COLOR_2_2, TEXT_COLOR_2, W // 128)


class Slider:

    def __init__(self, surface, min_value, max_value, sequence, left_x, middle_y, width, height,
                 bar_color, controller_color_1, controller_color_2):
        self.surface = surface
        self.bar_color = bar_color
        self.controller_color_1 = controller_color_1
        self.controller_color_2 = controller_color_2
        self.controller_color = controller_color_1
        self.circle_radius = height
        self.border_radius = height // 2
        self.sequence = sequence
        self.min_x, self.max_x = left_x + height, left_x + width - height
        self.slide_length = self.max_x - self.min_x
        self.controller_x = left_x + height
        self.controller_y = middle_y
        self.min_value, self.max_value = min_value, max_value
        self.value_gap = self.max_value - self.min_value
        self.bar_rect = pygame.rect.Rect(left_x, middle_y - height // 2, width, height)
        self.holding = False

    def mouse_collides_controller(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        distance = ((mouse_x - self.controller_x) ** 2 + (mouse_y - self.controller_y) ** 2) ** .5
        if distance < self.circle_radius:
            return True
        return False

    def movement(self):
        mouse_pos = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0]:
            if self.mouse_collides_controller():
                self.holding = True
            if self.holding:
                self.controller_x = mouse_pos[0]
            elif self.bar_rect.collidepoint(mouse_pos):
                self.controller_x = mouse_pos[0]
            if self.controller_x < self.min_x:
                self.controller_x = self.min_x
            elif self.controller_x > self.max_x:
                self.controller_x = self.max_x
        else:
            self.holding = False

    def calculate_value(self):
        rounded_value = round(self.min_value + self.value_gap * (self.controller_x - self.min_x) / self.slide_length)
        return rounded_value - rounded_value % self.sequence

    def set_controller_pos_from_value(self, value):
        self.controller_x = self.min_x + self.slide_length * (value - self.min_value) / self.value_gap
        if self.controller_x < self.min_x:
            self.controller_x = self.min_x
        elif self.controller_x > self.max_x:
            self.controller_x = self.max_x

    def update_min_max_sequence_values(self, max_value):
        self.min_value = -max_value
        self.max_value = max_value
        self.value_gap = max_value * 2

    def draw(self):
        if self.holding:
            self.controller_color = self.controller_color_2
        else:
            self.controller_color = self.controller_color_1
        pygame.draw.rect(self.surface, self.bar_color, self.bar_rect, border_radius=self.border_radius)
        pygame.draw.circle(self.surface, self.controller_color,
                           (self.controller_x, self.controller_y), self.circle_radius)


slider_max_value = Slider(SCREEN, 4, 80, 4, W // 32, 33 * W // 64, W // 8, 3 * W // 320,
                          BUTTON_COLOR_1_1, BUTTON_COLOR_1_2, TEXT_COLOR_1)
slider_x_axes_alpha = Slider(SCREEN, 0, 359, 5, 13 * W // 32, 29 * W // 64, W // 8, 3 * W // 320,
                             BUTTON_COLOR_1_1, BUTTON_COLOR_1_2, TEXT_COLOR_1)
slider_y_axes_alpha = Slider(SCREEN, 0, 359, 5, 13 * W // 32, 31 * W // 64, W // 8, 3 * W // 320,
                             BUTTON_COLOR_1_1, BUTTON_COLOR_1_2, TEXT_COLOR_1)
slider_z_axes_alpha = Slider(SCREEN, 0, 359, 5, 13 * W // 32, 33 * W // 64, W // 8, 3 * W // 320,
                             BUTTON_COLOR_1_1, BUTTON_COLOR_1_2, TEXT_COLOR_1)
slider_dot_x_pos = Slider(SCREEN, -4, 4, 1, 49 * W // 64, 29 * W // 64, 3 * W // 16, 3 * W // 384,
                          BUTTON_COLOR_2_1, BUTTON_COLOR_2_2, TEXT_COLOR_2)
slider_dot_y_pos = Slider(SCREEN, -4, 4, 1, 49 * W // 64, 31 * W // 64, 3 * W // 16, 3 * W // 384,
                          BUTTON_COLOR_2_1, BUTTON_COLOR_2_2, TEXT_COLOR_2)
slider_dot_z_pos = Slider(SCREEN, -4, 4, 1, 49 * W // 64, 33 * W // 64, 3 * W // 16, 3 * W // 384,
                          BUTTON_COLOR_2_1, BUTTON_COLOR_2_2, TEXT_COLOR_2)
slider_x_axes_alpha.set_controller_pos_from_value(330)
slider_y_axes_alpha.set_controller_pos_from_value(90)
slider_z_axes_alpha.set_controller_pos_from_value(210)
slider_dot_x_pos.set_controller_pos_from_value(0)
slider_dot_y_pos.set_controller_pos_from_value(0)
slider_dot_z_pos.set_controller_pos_from_value(0)


class Axes:

    def __init__(self, surface, center_x, center_y, length, thickness, axes_color, min_color, max_color):
        self.surface = surface
        self.thickness = thickness
        self.axes_color = axes_color
        self.min_color = min_color
        self.max_color = max_color
        self.center_x = center_x
        self.center_y = center_y
        self.start_pos = (center_x, center_y + length // 2)   # negative
        self.end_pos = (center_x, center_y - length // 2)   # positive
        self.dint_positions = [self.start_pos, (center_x, center_y + length // 4),
                               (center_x, center_y), (center_x, center_y - length // 4), self.end_pos]
        self.radius = length // 2
        self.slope = 90

    def set_positions(self, alpha):
        x = self.radius * math.cos(alpha * math.pi / 180)
        y = self.radius * math.sin(alpha * math.pi / 180)
        start_x = self.center_x - x
        start_y = self.center_y + y
        end_x = self.center_x + x
        end_y = self.center_y - y
        self.start_pos = (start_x, start_y)
        self.end_pos = (end_x, end_y)
        d_x = (end_x - start_x)
        d_y = (end_y - start_y)
        self.dint_positions = [self.start_pos, (start_x + d_x // 4, start_y + d_y // 4),
                               (start_x + 3 * d_x // 4, start_y + 3 * d_y // 4), self.end_pos]

    def draw(self):
        pygame.draw.line(self.surface, self.axes_color, self.start_pos, self.end_pos, self.thickness)
        for n in range(len(self.dint_positions)):
            pos = self.dint_positions[n]
            if n == 0:
                pygame.draw.circle(self.surface, self.min_color, pos, self.thickness)
            elif n == len(self.dint_positions) - 1:
                pygame.draw.circle(self.surface, self.max_color, pos, self.thickness)
            else:
                pygame.draw.circle(self.surface, self.axes_color, pos, self.thickness)


x_axes = Axes(SCREEN, 9 * W // 32, 9 * W // 32, W // 4, AXES_THICKNESS, AXES_COLOR, AXES_MIN_COLOR, AXES_MAX_COLOR)
y_axes = Axes(SCREEN, 9 * W // 32, 9 * W // 32, W // 4, AXES_THICKNESS, AXES_COLOR, AXES_MIN_COLOR, AXES_MAX_COLOR)
z_axes = Axes(SCREEN, 9 * W // 32, 9 * W // 32, W // 4, AXES_THICKNESS, AXES_COLOR, AXES_MIN_COLOR, AXES_MAX_COLOR)


class DotRect:

    def __init__(self, surface, width, color_1_1, color_1_2, color_2_1, color_2_2, color_3_1, color_3_2):
        self.surface = surface
        self.colors_1 = (color_1_1, color_1_2)
        self.colors_2 = (color_2_1, color_2_2)
        self.colors_3 = (color_3_1, color_3_2)
        self.color = color_1_1
        self.width = width
        self.body_rect = pygame.rect.Rect(0, 0, 0, 0)
        self.press_allowed = True
        self.pressed = False
        self.is_chosen = False
        self.is_selected_to_connect = False
        self.dot_3d_pos = (0, 0, 0)
        self.dot_2d_pos = (0, 0)

    def is_clicked(self):
        mouse_pressed = pygame.mouse.get_pressed()[0]
        if self.body_rect.collidepoint(pygame.mouse.get_pos()):
            if mouse_pressed:
                self.pressed = True
            elif self.pressed and self.press_allowed:
                self.pressed = False
                return True
        else:
            self.pressed = False
            if mouse_pressed:
                self.press_allowed = False
            else:
                self.press_allowed = True
        return False

    def update_body(self, rect_center_x, rect_center_y):
        rect_center_x -= self.width // 2
        rect_center_y -= self.width // 2
        self.body_rect = pygame.rect.Rect(rect_center_x, rect_center_y, self.width, self.width)

    def draw(self):
        if self.is_selected_to_connect:
            if self.body_rect.collidepoint(pygame.mouse.get_pos()):
                self.color = self.colors_3[1]
            else:
                self.color = self.colors_3[0]
        elif self.is_chosen:
            if self.body_rect.collidepoint(pygame.mouse.get_pos()):
                self.color = self.colors_2[1]
            else:
                self.color = self.colors_2[0]
        else:
            if self.body_rect.collidepoint(pygame.mouse.get_pos()):
                self.color = self.colors_1[1]
            else:
                self.color = self.colors_1[0]
        pygame.draw.rect(self.surface, self.color, self.body_rect)


def work_on_input(input_index):
    user_inputs_list = os.listdir(USER_INPUTS_DIR)
    input_index += 1
    if input_index == len(user_inputs_list): input_index = 0
    input_data = pandas.read_csv(f"{USER_INPUTS_DIR}/{user_inputs_list[input_index]}")
    input_data_dict = input_data.to_dict()
    new_max_value = int(input_data_dict["maximum value"][0])
    new_x_axes_alpha = int(input_data_dict["x axes angle"][0])
    new_y_axes_alpha = int(input_data_dict["y axes angle"][0])
    new_z_axes_alpha = int(input_data_dict["z axes angle"][0])
    new_3d_positions = []
    for n in range(len(input_data)):
        new_3d_positions.append((list(input_data_dict["x"].values())[n],
                                 list(input_data_dict["y"].values())[n], list(input_data_dict["z"].values())[n]))
    new_connections = []
    for n in range(len(input_data)):
        if type(list(input_data_dict["connections"].values())[n]) is str:
            indexes_to_connect = [int(num) - 1 for num in list(input_data_dict["connections"].values())[n].split("-")]
            for dot_rect_index in indexes_to_connect:
                if not (n == dot_rect_index or
                        [n, dot_rect_index] in new_connections or [dot_rect_index, n] in new_connections):
                    new_connections.append([n, dot_rect_index])
    return ([new_max_value, new_x_axes_alpha, new_y_axes_alpha, new_z_axes_alpha, new_3d_positions, new_connections],
            input_index)


def save_as_output(dot_rect_num, connections_with_nums, x_positions, y_positions, z_positions,
                   x_axes_alpha, y_axes_alpha, z_axes_alpha, max_value):
    x_axes_angle_list = [str(x_axes_alpha)]
    y_axes_angle_list = [str(y_axes_alpha)]
    z_axes_angle_list = [str(z_axes_alpha)]
    max_value_list = [str(max_value)]
    for _ in range(dot_rect_num - 1):
        x_axes_angle_list.append(None)
        y_axes_angle_list.append(None)
        z_axes_angle_list.append(None)
        max_value_list.append(None)
    dataframe = pandas.DataFrame({
        "no": [str(num) for num in list(range(1, dot_rect_num + 1))],
        "connections": connections_with_nums,
        "x": x_positions,
        "y": y_positions,
        "z": z_positions,
        "x axes angle": x_axes_angle_list,
        "y axes angle": y_axes_angle_list,
        "z axes angle": z_axes_angle_list,
        "maximum value": max_value_list
    })
    output_no = 1
    while f"output_{output_no}.csv" in os.listdir(OUTPUTS_DIR): output_no += 1
    output_file_path = os.path.join(OUTPUTS_DIR, f"output_{output_no}.csv")
    dataframe.to_csv(output_file_path, index=False)


def produce_2d_pos_from_3d_pos(x, y, z, x_alpha, y_alpha, z_alpha, max_value):

    x_radius = x * AXES_LENGTH / (max_value * 2)
    x_x_add_value = round(x_radius * math.cos(x_alpha * math.pi / 180))
    x_y_add_value = round(x_radius * math.sin(x_alpha * math.pi / 180))

    y_radius = y * AXES_LENGTH / (max_value * 2)
    y_x_add_value = round(y_radius * math.cos(y_alpha * math.pi / 180))
    y_y_add_value = round(y_radius * math.sin(y_alpha * math.pi / 180))

    z_radius = z * AXES_LENGTH / (max_value * 2)
    z_x_add_value = round(z_radius * math.cos(z_alpha * math.pi / 180))
    z_y_add_value = round(z_radius * math.sin(z_alpha * math.pi / 180))

    second_dimensional_x_pos = GRAPH_CENTER_X + x_x_add_value + y_x_add_value + z_x_add_value
    second_dimensional_y_pos = GRAPH_CENTER_Y - x_y_add_value - y_y_add_value - z_y_add_value
    return second_dimensional_x_pos, second_dimensional_y_pos


def produce_dot_rect_positions(num_rects):
    the_dot_rect_positions = []
    alpha_sequence = 360 / num_rects
    current_alpha = 90
    for _ in range(num_rects):
        x = round(RECTS_CIRCLE_RADIUS * math.cos(current_alpha * math.pi / 180))
        y = round(RECTS_CIRCLE_RADIUS * math.sin(current_alpha * math.pi / 180))
        the_dot_rect_positions.append((RECTS_CENTER_X + x, RECTS_CENTER_Y - y))
        current_alpha += alpha_sequence
    return the_dot_rect_positions


def update_dot_rects(the_dot_rects):
    dot_rect_center_positions = produce_dot_rect_positions(len(the_dot_rects))
    for n in range(len(the_dot_rects)):
        the_dot_rects[n].update_body(dot_rect_center_positions[n][0], dot_rect_center_positions[n][1])
        the_dot_rects[n].is_chosen = False
    the_chosen_dot_rect = the_dot_rects[-1]
    the_chosen_dot_rect.is_chosen = True
    return the_dot_rects, the_chosen_dot_rect


def update_slider_values(sliders, values):
    for n in range(len(sliders)):
        sliders[n].set_controller_pos_from_value(values[n])


def mouse_on_graph_area():
    mouse_pos = pygame.mouse.get_pos()
    if 0 < mouse_pos[0] < 9 * W // 16 - 1 and 0 < mouse_pos[1] < 9 * W // 16 - 1:
        return True
    return False


current_input_index = 0

text_dot_position_x_surf = GUI_FONT_LARGE.render("x:", True, TEXT_COLOR_2)
text_dot_position_x_rect = text_dot_position_x_surf.get_rect(midleft=(47 * W // 64, 29 * W // 64))
text_dot_position_y_surf = GUI_FONT_LARGE.render("y:", True, TEXT_COLOR_2)
text_dot_position_y_rect = text_dot_position_y_surf.get_rect(midleft=(47 * W // 64, 31 * W // 64))
text_dot_position_z_surf = GUI_FONT_LARGE.render("z:", True, TEXT_COLOR_2)
text_dot_position_z_rect = text_dot_position_z_surf.get_rect(midleft=(47 * W // 64, 33 * W // 64))

dot_rects = [DotRect(SCREEN, RECT_WIDTH,
                     RECT_COLOR_1_1, RECT_COLOR_1_2, RECT_COLOR_2_1, RECT_COLOR_2_2, RECT_COLOR_3_1, RECT_COLOR_3_2)]
dot_rects, chosen_dot_rect = update_dot_rects(dot_rects)

selected_dot_rects_to_connect = []
dot_rect_connections = []

showing_graph = True
showing_dots = True

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    # # # Mechanics # # #

    maximum_value = slider_max_value.calculate_value()

    if mouse_on_graph_area():
        if pygame.mouse.get_pressed()[0] and chosen_dot_rect is not None:
            chosen_dot_rect.is_chosen = False
            chosen_dot_rect = None
        if button_hide_graph.is_clicked():
            showing_graph = not showing_graph
        if button_hide_dots.is_clicked():
            showing_dots = not showing_dots
        if button_reset_graph.is_clicked():
            slider_x_axes_alpha.set_controller_pos_from_value(330)
            slider_y_axes_alpha.set_controller_pos_from_value(90)
            slider_z_axes_alpha.set_controller_pos_from_value(210)
        slider_max_value.movement()
        if maximum_value != slider_max_value.calculate_value():
            maximum_value = slider_max_value.calculate_value()
            if chosen_dot_rect is not None:
                chosen_dot_rect.is_chosen = False
                chosen_dot_rect = None
        slider_x_axes_alpha.movement()
        slider_y_axes_alpha.movement()
        slider_z_axes_alpha.movement()
        slider_dot_x_pos.update_min_max_sequence_values(maximum_value)
        slider_dot_y_pos.update_min_max_sequence_values(maximum_value)
        slider_dot_z_pos.update_min_max_sequence_values(maximum_value)

    if button_get_input.is_clicked() and len(os.listdir(USER_INPUTS_DIR)) > 0:
        worked_input_list, current_input_index = work_on_input(current_input_index)
        # maximum value
        maximum_value = worked_input_list[0]
        slider_max_value.set_controller_pos_from_value(maximum_value)
        # axes alphas
        slider_x_axes_alpha.set_controller_pos_from_value(worked_input_list[1])
        slider_y_axes_alpha.set_controller_pos_from_value(worked_input_list[2])
        slider_z_axes_alpha.set_controller_pos_from_value(worked_input_list[3])
        # dot rects and 3d positions
        dot_rects = []
        for i in range(len(worked_input_list[4])):
            new_dot_rect = DotRect(SCREEN, RECT_WIDTH, RECT_COLOR_1_1, RECT_COLOR_1_2,
                                   RECT_COLOR_2_1, RECT_COLOR_2_2, RECT_COLOR_3_1, RECT_COLOR_3_2)
            new_dot_rect.dot_3d_pos = worked_input_list[4][i]
            dot_rects.append(new_dot_rect)
        dot_rects, chosen_dot_rect = update_dot_rects(dot_rects)
        chosen_dot_rect.is_chosen = False
        chosen_dot_rect = None
        # dot rect connections
        selected_dot_rects_to_connect = []
        dot_rect_connections = []
        for i1, i2 in worked_input_list[5]:
            dot_rect_connections.append([dot_rects[i1], dot_rects[i2]])

    if button_save_data.is_clicked():
        # dot rect connections
        dot_rect_connections_with_nums = []
        for i in range(len(dot_rects)):
            dot_rect_connections_with_nums.append([])
        for index in range(len(dot_rects) - 1):
            for dot_rect_1, dot_rect_2 in dot_rect_connections:
                if dot_rects.index(dot_rect_1) == index < dot_rects.index(dot_rect_2):
                    dot_rect_connections_with_nums[index].append(dot_rects.index(dot_rect_2) + 1)
                elif dot_rects.index(dot_rect_2) == index < dot_rects.index(dot_rect_1):
                    dot_rect_connections_with_nums[index].append(dot_rects.index(dot_rect_1) + 1)
        for i in range(len(dot_rect_connections_with_nums)):
            connection_list = [str(num) for num in dot_rect_connections_with_nums[i]]
            dot_rect_connections_with_nums[i] = "-".join(connection_list)
        # dot rect 3d positions
        dot_rect_x_positions = []
        dot_rect_y_positions = []
        dot_rect_z_positions = []
        for dot_rect in dot_rects:
            dot_rect_x_positions.append(str(dot_rect.dot_3d_pos[0]))
            dot_rect_y_positions.append(str(dot_rect.dot_3d_pos[1]))
            dot_rect_z_positions.append(str(dot_rect.dot_3d_pos[2]))
        # saving as csv
        save_as_output(len(dot_rects), dot_rect_connections_with_nums, dot_rect_x_positions, dot_rect_y_positions,
                       dot_rect_z_positions, slider_x_axes_alpha.calculate_value(),
                       slider_y_axes_alpha.calculate_value(), slider_z_axes_alpha.calculate_value(), maximum_value)

    if button_new_dot.is_clicked():
        dot_rects.append(DotRect(SCREEN, RECT_WIDTH, RECT_COLOR_1_1, RECT_COLOR_1_2,
                                 RECT_COLOR_2_1, RECT_COLOR_2_2, RECT_COLOR_3_1, RECT_COLOR_3_2))
        dot_rects, chosen_dot_rect = update_dot_rects(dot_rects)
        update_slider_values([slider_dot_x_pos, slider_dot_y_pos, slider_dot_z_pos], (0, 0, 0))

    if button_remove.is_clicked() and chosen_dot_rect is not None and len(dot_rects) > 1:
        if chosen_dot_rect in selected_dot_rects_to_connect:
            selected_dot_rects_to_connect.remove(chosen_dot_rect)
        dot_rects.remove(chosen_dot_rect)
        dot_rects, chosen_dot_rect = update_dot_rects(dot_rects)
        new_dot_rect_connections = [connection for connection in dot_rect_connections]
        for connection in dot_rect_connections:
            if not (connection[0] in dot_rects and connection[1] in dot_rects):
                new_dot_rect_connections.remove(connection)
        dot_rect_connections = [connection for connection in new_dot_rect_connections]
        update_slider_values([slider_dot_x_pos, slider_dot_y_pos, slider_dot_z_pos], chosen_dot_rect.dot_3d_pos)

    if button_reset_all.is_clicked():
        current_input_index = 0
        slider_x_axes_alpha.set_controller_pos_from_value(330)
        slider_y_axes_alpha.set_controller_pos_from_value(90)
        slider_z_axes_alpha.set_controller_pos_from_value(210)
        slider_dot_x_pos.set_controller_pos_from_value(0)
        slider_dot_y_pos.set_controller_pos_from_value(0)
        slider_dot_z_pos.set_controller_pos_from_value(0)
        slider_max_value.set_controller_pos_from_value(4)
        showing_graph = True
        showing_dots = True
        dot_rects = [DotRect(SCREEN, RECT_WIDTH,
                             RECT_COLOR_1_1, RECT_COLOR_1_2, RECT_COLOR_2_1, RECT_COLOR_2_2, RECT_COLOR_3_1,
                             RECT_COLOR_3_2)]
        dot_rects, chosen_dot_rect = update_dot_rects(dot_rects)
        selected_dot_rects_to_connect = []
        dot_rect_connections = []

    x_axes.set_positions(slider_x_axes_alpha.calculate_value())
    y_axes.set_positions(slider_y_axes_alpha.calculate_value())
    z_axes.set_positions(slider_z_axes_alpha.calculate_value())

    for dot_rect in dot_rects:
        if dot_rect.body_rect.collidepoint(pygame.mouse.get_pos()):
            for i in range(len(dot_rects)):
                dot_rects[i].is_chosen = False
            chosen_dot_rect = dot_rect
            chosen_dot_rect.is_chosen = True
            update_slider_values([slider_dot_x_pos, slider_dot_y_pos, slider_dot_z_pos], chosen_dot_rect.dot_3d_pos)
        if dot_rect.is_clicked():
            if dot_rect.is_selected_to_connect:
                dot_rect.is_selected_to_connect = False
                selected_dot_rects_to_connect.remove(dot_rect)
            else:
                dot_rect.is_selected_to_connect = True
                selected_dot_rects_to_connect.append(dot_rect)
                if len(selected_dot_rects_to_connect) == 2:
                    if (selected_dot_rects_to_connect in dot_rect_connections
                            or selected_dot_rects_to_connect[::-1] in dot_rect_connections):
                        for d_rect in selected_dot_rects_to_connect:
                            d_rect.is_selected_to_connect = False
                        for connection in dot_rect_connections:
                            if selected_dot_rects_to_connect in [connection, connection[::-1]]:
                                dot_rect_connections.remove(connection)
                        selected_dot_rects_to_connect = []
                    else:
                        dot_rect_connections.append(selected_dot_rects_to_connect)
                        for d_rect in selected_dot_rects_to_connect:
                            d_rect.is_selected_to_connect = False
                        selected_dot_rects_to_connect = []

    slider_dot_x_pos.movement()
    slider_dot_y_pos.movement()
    slider_dot_z_pos.movement()
    text_dot_position_surf = GUI_FONT_LARGE.render(f"({slider_dot_x_pos.calculate_value()}, "
                                                   f"{slider_dot_y_pos.calculate_value()}, "
                                                   f"{slider_dot_z_pos.calculate_value()})",
                                                   True, TEXT_COLOR_2)
    text_dot_position_rect = text_dot_position_surf.get_rect(center=(55 * W // 64, 25 * W // 64))
    if chosen_dot_rect is not None:
        chosen_dot_rect.dot_3d_pos = (slider_dot_x_pos.calculate_value(),
                                      slider_dot_y_pos.calculate_value(), slider_dot_z_pos.calculate_value())

    for dot_rect in dot_rects:
        new_dot_pos = [v for v in dot_rect.dot_3d_pos]
        for i in range(3):
            if new_dot_pos[i] < -maximum_value:
                new_dot_pos[i] = -maximum_value
            elif new_dot_pos[i] > maximum_value:
                new_dot_pos[i] = maximum_value
        dot_rect.dot_3d_pos = tuple(v for v in new_dot_pos)

    for dot_rect in dot_rects:
        dot_rect.dot_2d_pos = produce_2d_pos_from_3d_pos(
            dot_rect.dot_3d_pos[0], dot_rect.dot_3d_pos[1], dot_rect.dot_3d_pos[2],
            slider_x_axes_alpha.calculate_value(), slider_y_axes_alpha.calculate_value(),
            slider_z_axes_alpha.calculate_value(), maximum_value)

    # # # GUI # # #

    text_max_values_surf = GUI_FONT_LARGE.render(f"max:  ± {maximum_value}",
                                                 True, TEXT_COLOR_1)
    text_max_values_rect = text_max_values_surf.get_rect(center=(3 * W // 32, 31 * W // 64))
    text_x_axes_tangent_surf = GUI_FONT_LARGE.render(f"x:  {slider_x_axes_alpha.calculate_value()}°",
                                                     True, TEXT_COLOR_1)
    text_x_axes_tangent_rect = text_x_axes_tangent_surf.get_rect(midright=(25 * W // 64, 29 * W // 64))
    text_y_axes_tangent_surf = GUI_FONT_LARGE.render(f"y:  {slider_y_axes_alpha.calculate_value()}°",
                                                     True, TEXT_COLOR_1)
    text_y_axes_tangent_rect = text_y_axes_tangent_surf.get_rect(midright=(25 * W // 64, 31 * W // 64))
    text_z_axes_tangent_surf = GUI_FONT_LARGE.render(f"z:  {slider_z_axes_alpha.calculate_value()}°",
                                                     True, TEXT_COLOR_1)
    text_z_axes_tangent_rect = text_z_axes_tangent_surf.get_rect(midright=(25 * W // 64, 33 * W // 64))

    SCREEN.fill(BG_COLOR)

    if showing_graph:
        y_axes.draw()
        x_axes.draw()
        z_axes.draw()

    if showing_dots:
        for connection in dot_rect_connections:
            pygame.draw.line(SCREEN, DOT_COLOR, connection[0].dot_2d_pos, connection[1].dot_2d_pos, AXES_THICKNESS)
        for dot_rect in [d_rect for d_rect in dot_rects if d_rect != chosen_dot_rect]:
            pygame.draw.circle(SCREEN, DOT_COLOR, dot_rect.dot_2d_pos, AXES_THICKNESS * 2)
        if chosen_dot_rect is not None:
            pygame.draw.circle(SCREEN, DOT_CHOSEN_COLOR, chosen_dot_rect.dot_2d_pos, AXES_THICKNESS * 2)

    if mouse_on_graph_area():
        if showing_graph:
            button_hide_graph.draw("Hide Graph")
        else:
            button_hide_graph.draw("Show Graph")
        if showing_dots:
            button_hide_dots.draw("Hide Dots")
        else:
            button_hide_dots.draw("Show Dots")
        button_reset_graph.draw(None)
        button_reset_all.draw(None)
        button_get_input.draw(None)
        button_save_data.draw(None)
        slider_max_value.draw()
        slider_x_axes_alpha.draw()
        slider_y_axes_alpha.draw()
        slider_z_axes_alpha.draw()
        SCREEN.blit(text_max_values_surf, text_max_values_rect)
        SCREEN.blit(text_x_axes_tangent_surf, text_x_axes_tangent_rect)
        SCREEN.blit(text_y_axes_tangent_surf, text_y_axes_tangent_rect)
        SCREEN.blit(text_z_axes_tangent_surf, text_z_axes_tangent_rect)

    pygame.draw.rect(SCREEN, BG_PANEL_COLOR, bg_panel_rect)

    if chosen_dot_rect is not None:
        slider_dot_x_pos.draw()
        slider_dot_y_pos.draw()
        slider_dot_z_pos.draw()
        SCREEN.blit(text_dot_position_x_surf, text_dot_position_x_rect)
        SCREEN.blit(text_dot_position_y_surf, text_dot_position_y_rect)
        SCREEN.blit(text_dot_position_z_surf, text_dot_position_z_rect)
        SCREEN.blit(text_dot_position_surf, text_dot_position_rect)
    button_new_dot.draw(None)
    button_remove.draw(None)
    for connection in dot_rect_connections:
        pygame.draw.line(
            SCREEN, TEXT_COLOR_2, connection[0].body_rect.center, connection[1].body_rect.center, AXES_THICKNESS)
    for dot_rect in dot_rects:
        dot_rect.draw()

    # # # # # # #

    CLOCK.tick(60)
    pygame.display.update()
