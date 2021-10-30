import pygame
import math
from settings import *


class Board():
    def __init__(self):
        self.rows = 20
        self.columns = 20
        self.width = WIDTH / self.columns
        self.graph = [["empty" for col in range(self.columns)] for row in range(self.rows)]

    def update(self, rows, columns):
        self.rows = rows
        self.columns = columns
        self.width = WIDTH / self.columns
        self.graph = [["empty" for col in range(self.columns)] for row in range(self.rows)]

    def place_walls(self, row, col):
        self.graph[row][col] = "wall"

    def clear_walls(self, row, col):
        self.graph[row][col] = "empty"

    def random_generation(self):
        print("Coming soon...")

    def draw_board(self, win):
        win.fill(WHITE)
        for row in range(self.rows):
            pygame.draw.line(win, BLACK, (0, row * self.width), (WIDTH, row * self.width), 1)
            for col in range(self.columns):
                pygame.draw.line(win, BLACK, (col * self.width, 0), (col * self.width, HEIGTH - 200), 1)
                if self.graph[row][col] == "wall":
                    pygame.draw.rect(win, BLACK, pygame.Rect(col * self.width +1, row * self.width +1, self.width -1, self.width -1))



class Button():
    def __init__(self, x, text):
        self.x = x
        self.text = text
        self.buttons_rect = pygame.Rect(self.x, HEIGTH - 200, WIDTH / 3, 50)
        self.isPressed = False

    def draw(self, win):
        pygame.draw.rect(win, BLACK, self.buttons_rect, 1)
        pygame.draw.rect(win, CERISE, (self.x + 1, HEIGTH - 199, WIDTH / 3 - 2, 48))
        if self.isPressed == True:
            pygame.draw.rect(win, GREEN, (self.x + 1, HEIGTH - 199, WIDTH / 3 - 2, 48))
        text = font.render(self.text, 1, (0, 0, 0))
        win.blit(text, (self.x + WIDTH / 6 - (text.get_width() / 2), HEIGTH - 190))



class CheckBox():
    def __init__(self, x, y, text):
        self.x = x
        self.y = y
        self.text = text
        self.is_checked = False
        self.rect = pygame.Rect(self.x, self.y, 30, 30)

    def draw(self):
        pygame.draw.rect(win, BLACK, self.rect, 1)
        if self.is_checked:
            square = pygame.Rect(self.x + 5, self.y + 5, 20, 20)
            pygame.draw.rect(win, BLACK, square)
        text = font.render(self.text, 1, (0, 0, 0))
        win.blit(text, (self.x + 40, self.y + 2))



class Node():
    def __init__(self, parent, position):
        self.parent = parent
        self.position = position

        self.f = 0
        self.g = 0
        self.h = 0

    def __eq__(self, other):
        return self.position == other.position

    def get_node_rect(self, width):
        return pygame.Rect(self.position[1] * width + 1, self.position[0] * width + 1, width - 1, width - 1)

    def draw(self, color, node_rect):
        pygame.draw.rect(win, color, node_rect)


def draw_path(color, path, width):
    for p in path:
        node_rect = pygame.Rect(p[1] * width + 1, p[0] * width + 1, width - 1, width - 1)
        pygame.draw.rect(win, color, node_rect)
        pygame.display.update()


def freeze(ms):
    i = 0
    while i < ms:
        pygame.time.delay(10)
        i += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                i = 101
                pygame.quit()


def heuristic(start, end, distance):
    if distance == "Manhattan":
        return abs(start[0] - end[0]) + abs(start[1] - end[1])
    if distance == "Euclidean":
        return math.sqrt(((start[0] - end[0]) ** 2) + ((start[1] - end[1]) ** 2))


def return_path(current_node):
    path = []
    current = current_node
    while current is not None:
        path.append(current.position)
        current = current.parent
    return path[::-1]


def a_star(graph, node_width, start, end, distance, allow_diagonal, allow_bidirectional):
    open_list = []
    closed_list = []

    open_list.append(start)

    current_iteration = 0
    max_iterations = (len(graph) // 2) ** 10
    neighbors = set()
    
    if allow_diagonal:
        possible_moves = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, 1), (-1, -1), (1, -1)]
    else:
        possible_moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    while len(open_list) > 0:
        current_iteration += 1

        current_node = open_list[0]
        current_index = 0
        for index, node in enumerate(open_list):
            if node.f < current_node.f:
                current_node = node
                current_index = index

        if current_iteration > max_iterations:
            return return_path(current_node)

        open_list.pop(current_index)
        closed_list.append(current_node)

        if current_node == end:
            return return_path(current_node)

        children = []

        for new_position in possible_moves:
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])
            if node_position in neighbors:
                continue
            else:
                neighbors.add(node_position)

            if (node_position[0] > len(graph) -1 or
                node_position[0] < 0 or
                node_position[1] > len(graph[len(graph) -1]) -1 or
                node_position[1] < 0):
                continue

            if graph[node_position[0]][node_position[1]] != "empty":
                continue

            new_node = Node(current_node, node_position)
            new_node.draw(RED, new_node.get_node_rect(node_width))
            pygame.display.update()
            freeze(1)

            children.append(new_node)

        for child in children:
            child.g = current_node.g + 1
            child.h = heuristic(child.position, end.position, distance)
            child.f = child.g + child.h

            for open_node in open_list:
                if open_node == child and child.g >= open_node.g:
                    open_list.remove(child)
                    continue

            for closed_node in closed_list:
                if closed_node == child:
                    closed_list.remove(child)
                    continue

            open_list.append(child)


def main():
    clock = pygame.time.Clock()
    run = True

    board = Board()
    buttons_list = [Button(0, "Clear"), Button(WIDTH / 3, "Random"), Button(WIDTH / 3 * 2, "Generate")]
    
    algo_boxes = [CheckBox(20, HEIGTH - 140, "A*"), 
                  CheckBox(20, HEIGTH - 105, "Dijkstra"),
                  CheckBox(20, HEIGTH - 70, "Best-First-Search"),
                  CheckBox(20, HEIGTH - 35, "Breadth-First-Search")]
    
    option_boxes = [CheckBox(300, HEIGTH - 120, "Diagonal"), CheckBox(300, HEIGTH - 60, "Bi-directional")]
    heuristic_boxes = [CheckBox(500, HEIGTH - 120, "Manhattan"), CheckBox(500, HEIGTH - 60, "Euclidean")]
    
    algo_boxes[0].is_checked = True
    algorithm = algo_boxes[0].text
    heuristic_boxes[0].is_checked = True
    heuristic = heuristic_boxes[0].text

    start = Node(None, (1, 1))
    end = Node(None, (board.rows - 2, board.columns - 2))
    path = None
    can_move_start = False
    can_move_end = False
    can_place_walls = False
    can_remove_walls = False

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4 and board.rows > 10:
                    board.rows -= 1
                    board.columns -= 1
                    end.position = (board.rows - 2, board.columns - 2)
                    board.update(board.rows, board.columns)
                elif event.button == 5 and board.rows < 40:
                    board.rows += 1
                    board.columns += 1
                    end.position = (board.rows - 2, board.columns - 2)
                    board.update(board.rows, board.columns)
            for button in buttons_list:
                if event.type == pygame.MOUSEBUTTONDOWN and button.buttons_rect.collidepoint(pygame.mouse.get_pos()):
                    if button.isPressed == False:
                        for otherButtons in buttons_list:
                            otherButtons.isPressed = False
                        button.isPressed = True
                    else:
                        button.isPressed = False
            for algo_box in algo_boxes:
                if event.type == pygame.MOUSEBUTTONDOWN and algo_box.rect.collidepoint(pygame.mouse.get_pos()):
                    if algo_box.is_checked == False:
                        for other_box in algo_boxes:
                            other_box.is_checked = False
                        algo_box.is_checked = True
                    else:
                        algo_box.is_checked = False
            for option_box in option_boxes:
                if event.type == pygame.MOUSEBUTTONDOWN and option_box.rect.collidepoint(pygame.mouse.get_pos()):
                    if option_box.is_checked:
                        option_box.is_checked = False
                    else:
                        option_box.is_checked = True
            for heuristic_box in heuristic_boxes:
                if event.type == pygame.MOUSEBUTTONDOWN and heuristic_box.rect.collidepoint(pygame.mouse.get_pos()):
                    if heuristic_box.is_checked == False:
                        for other_box in heuristic_boxes:
                            other_box.is_checked = False
                        heuristic_box.is_checked = True
                    else:
                        heuristic_box.is_checked = False
        
        board.draw_board(win)
        start.draw(TEAL, start.get_node_rect(board.width))
        end.draw(ORANGE, end.get_node_rect(board.width))
        for button in buttons_list:
            button.draw(win)
        for algo_box in algo_boxes:
            algo_box.draw()
            if algo_box.is_checked:
                algorithm = algo_box.text
        for option_box in option_boxes:
            option_box.draw()
        
        if algorithm == "A*" or algorithm == "Best-First-Search":
            for heuristic_box in heuristic_boxes:
                heuristic_box.draw()
                if heuristic_box.is_checked:
                    heuristic = heuristic_box.text
        pygame.display.update()
        
        mouse_inputs = pygame.mouse.get_pressed()

        for row in range(board.rows):
            for col in range(board.columns):
                rect = pygame.Rect(col * board.width +1, row * board.width +1, math.ceil(board.width -1), math.ceil(board.width -1))
                if mouse_inputs[0]:
                    if start.get_node_rect(board.width).collidepoint(pygame.mouse.get_pos()) and can_place_walls == False and can_remove_walls == False:
                        can_move_start = True
                    if end.get_node_rect(board.width).collidepoint(pygame.mouse.get_pos()) and can_place_walls == False and can_remove_walls == False:
                        can_move_end = True
                    if rect.collidepoint(pygame.mouse.get_pos()) and board.graph[row][col] == "empty" and can_remove_walls == False:
                        can_place_walls = True
                    if rect.collidepoint(pygame.mouse.get_pos()) and board.graph[row][col] == "wall" and can_place_walls == False:
                        can_remove_walls = True
                    if buttons_list[0].buttons_rect.collidepoint(pygame.mouse.get_pos()):
                        board.clear_walls(row, col)
                        buttons_list[0].isPressed = False
                    if buttons_list[1].buttons_rect.collidepoint(pygame.mouse.get_pos()):
                        board.clear_walls(row, col)
                        buttons_list[1].isPressed = False
                    if buttons_list[2].buttons_rect.collidepoint(pygame.mouse.get_pos()):
                        if algorithm == "A*":
                            path = a_star(board.graph, 
                                                board.width, 
                                                start, 
                                                end,
                                                heuristic, 
                                                option_boxes[0].is_checked, 
                                                option_boxes[1].is_checked)
                        
                        elif algorithm == "Dijkstra":
                            print("Test")
                        buttons_list[2].isPressed = False
                        break
                else:
                    can_move_start = False
                    can_move_end = False
                    can_place_walls = False
                    can_remove_walls = False

                if can_move_start and rect.collidepoint(pygame.mouse.get_pos()) and board.graph[row][col] == "empty":
                    start.position = (pygame.mouse.get_pos()[1] // int(board.width), pygame.mouse.get_pos()[0] // int(board.width))
                elif can_move_end and rect.collidepoint(pygame.mouse.get_pos()) and board.graph[row][col] == "empty":
                    end.position = (pygame.mouse.get_pos()[1] // int(board.width), pygame.mouse.get_pos()[0] // int(board.width))
                elif can_place_walls and rect.collidepoint(pygame.mouse.get_pos()):
                    board.place_walls(row, col)
                elif can_remove_walls and rect.collidepoint(pygame.mouse.get_pos()):
                    board.clear_walls(row, col)

            if path != None:
                run = False
                draw_path(BLUE, path, board.width)
                freeze(10000)
                break

    pygame.quit()


pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGTH))
pygame.display.set_caption("Pathfinder")
font = pygame.font.SysFont("arial", 20, True, True)
main()