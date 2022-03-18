import pygame
import math
import random
from settings import *


class Board():
    def __init__(self):
        self.rows = 20
        self.columns = 20
        self.width = WIDTH // self.columns
        self.graph = [["empty" for col in range(self.columns)] for row in range(self.rows)] # 2D list which represents the grid

    def update(self, rows, columns):
        self.rows = rows
        self.columns = columns
        self.width = WIDTH / self.columns
        self.graph = [["empty" for col in range(self.columns)] for row in range(self.rows)]

    def place_walls(self, row, col):
        self.graph[row][col] = "wall"

    def clear_walls(self, row, col):
        self.graph[row][col] = "empty"

    def random_generation(self, start, end):
        nodes = (start.position, end.position)
        for position in nodes: # Making sure that both start and end node are within the grid
            if position[0] == 0:
                position = (position[0] + 1, position[1])
            if position[1] == 0:
                position = (position[0], position[1] + 1)
            if position[0] == self.rows - 1:
                position = (position[0] - 1, position[1])
            if position[1] == self.columns - 1:
                position = (position[0], position[1] - 1)
        
        for row in range(self.rows): # Filling the grid up of walls
            for col in range(self.columns):
                self.graph[row][col] = "wall"
        self.graph[end.position[0]][end.position[1]] = "empty"

        frontier = [start.position] # Frontier list
        possible_neighbors = [(0, 2), (0, -2), (2, 0), (-2, 0)]

        while len(frontier) > 0: # Prim's algorithm for maze generation
            random_frontier = frontier[random.randint(0, len(frontier) - 1)] # Choosing a frontier randomly among the frontier list
            self.graph[random_frontier[0]][random_frontier[1]] = "empty"
            frontier.remove(random_frontier)

            for neighbour in possible_neighbors:
                if((random_frontier[0] + neighbour[0], random_frontier[1] + neighbour[1]) in frontier or
                    random_frontier[0] + neighbour[0] < 1 or
                    random_frontier[0] + neighbour[0] > self.rows - 2 or
                    random_frontier[1] + neighbour[1] < 1 or
                    random_frontier[1] + neighbour[1] > self.columns - 2):

                    continue
                
                # Putting the cell between the chosen cell and another "empty" cell in state "empty"
                if self.graph[random_frontier[0] + neighbour[0]][random_frontier[1] + neighbour[1]] == "empty":
                    self.graph[(random_frontier[0] + (random_frontier[0] + neighbour[0])) // 2][(random_frontier[1] + (random_frontier[1] + neighbour[1])) // 2] = "empty"
                    break
            
            for neighbour in possible_neighbors: # Computing every frontier of the chosen node
                if((random_frontier[0] + neighbour[0], random_frontier[1] + neighbour[1]) in frontier or
                    random_frontier[0] + neighbour[0] < 1 or
                    random_frontier[0] + neighbour[0] > self.rows - 2 or
                    random_frontier[1] + neighbour[1] < 1 or
                    random_frontier[1] + neighbour[1] > self.columns - 2 or
                    self.graph[random_frontier[0] + neighbour[0]][random_frontier[1] + neighbour[1]] == "empty"):

                    continue
                
                frontier.append((random_frontier[0] + neighbour[0], random_frontier[1] + neighbour[1]))

    
    def draw_board(self, win): # Drawing the board including grids and walls
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

        self.f = 0 # f cost
        self.g = 0 # g cost
        self.h = 0 # h cost

    def __eq__(self, other):
        return self.position == other.position

    def get_node_rect(self, width): # Getting the Rect object of a node in the board
        return pygame.Rect(self.position[1] * width + 1, self.position[0] * width + 1, width - 1, width - 1)

    def draw(self, color, node_rect):
        pygame.draw.rect(win, color, node_rect)


def draw_path(color, path, width): # Drawing the final path if found
    for node in path:
        node.draw(color, node.get_node_rect(width))

def is_within_grid(graph, position): # Cheking if the node is within the grid
    if (position[0] > len(graph) -1 or
        position[0] < 0 or
        position[1] > len(graph[len(graph) -1]) -1 or
        position[1] < 0):

        return 0

    return 1


def freeze(ms): # Freezing the program
    i = 0
    while i < ms:
        pygame.time.delay(10)
        i += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                i = 101
                pygame.quit()


def heuristic(start, end, distance): # Calculating the heuristic cost (h cost)
    if distance == "Manhattan":
        return abs(start[0] - end[0]) + abs(start[1] - end[1])
    if distance == "Euclidean":
        return math.sqrt(((start[0] - end[0]) ** 2) + ((start[1] - end[1]) ** 2))


def return_path(current_node, node_width): # Returns a list of every coordinates that forms the final path
    path = []
    current = current_node
    while current is not None:
        path.append(current)
        current.draw(BLUE, current.get_node_rect(node_width))
        pygame.display.update()
        freeze(0.1)
        current = current.parent
    return path[1:-1]


def a_star(graph, node_width, start, end, distance, allow_diagonal): # A* algorithm
    open_list = []
    closed_list = []

    open_list.append(start)

    current_iteration = 0
    max_iterations = (len(graph) // 2) ** 10 # Set a max iteration in case the algorithm takes too long to find a path
    neighbors = set()

    possible_moves = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    diagonal_moves = []
    
    # All possible moves depending on the "allow_diagonal" variable
    if allow_diagonal:
        diagonal_moves = [(1, 1), (-1, 1), (-1, -1), (1, -1)]

    while len(open_list) > 0:
        current_iteration += 1

        current_node = open_list[0]
        current_index = 0
        for index, node in enumerate(open_list): # Finding the node with the lowest f cost
            if node.f < current_node.f:
                current_node = node
                current_index = index

        current_node.draw(RED, current_node.get_node_rect(node_width)) # Draws it

        if current_iteration > max_iterations:
            return return_path(current_node, node_width)

        open_list.pop(current_index)
        closed_list.append(current_node)

        if current_node == end: # The current node is the final destination, returning the final path
            return return_path(current_node, node_width)

        children = [] # Lists containing every reachable neighbors nodes

        for new_position in possible_moves + diagonal_moves: # Iterating through every possible moves
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])
            if node_position in neighbors: # Checking if the current neighbour has already been calculated in previous iterations
                continue
            else:
                neighbors.add(node_position)

            if is_within_grid(graph, node_position) == 0:
                continue

            if graph[node_position[0]][node_position[1]] != "empty": # Has to be an empty node
                continue
            
            if new_position in diagonal_moves: # Prevention for the corner cut problem
                counter = 0
                for straight_move in possible_moves:
                    if is_within_grid(graph, (node_position[0] + straight_move[0], node_position[1] + straight_move[1])) == 0:
                        continue
                    if graph[node_position[0]+straight_move[0]][node_position[1]+straight_move[1]] != "empty":
                        counter += 1
                if counter > 1:
                    continue

            new_node = Node(current_node, node_position) # Creating a new Node object
            new_node.draw(LIME, new_node.get_node_rect(node_width))
            pygame.display.update()
            freeze(0.1)

            children.append(new_node)

        for child in children: # Iterating through every reachable neighbors
            child.g = current_node.g + 1
            child.h = heuristic(child.position, end.position, distance)
            child.f = child.g + child.h # Updating the cost of the path

            for open_node in open_list:
                if open_node == child and child.g >= open_node.g:
                    open_list.remove(child)
                    continue

            open_list.append(child)


def main():
    clock = pygame.time.Clock()
    run = True

    board = Board()
    buttons_list = [Button(0, "Clear"), Button(WIDTH / 3, "Random"), Button(WIDTH / 3 * 2, "Generate")]
    
    algo_boxes = [CheckBox(20, HEIGTH - 120, "A*"), CheckBox(20, HEIGTH - 60, "Dijkstra")]
    
    option_boxes = [CheckBox(300, HEIGTH - 120, "Diagonal")]
    heuristic_boxes = [CheckBox(500, HEIGTH - 120, "Manhattan"), CheckBox(500, HEIGTH - 60, "Euclidean")]
    
    algo_boxes[0].is_checked = True
    algorithm = algo_boxes[0].text
    heuristic_boxes[0].is_checked = True
    heuristic = heuristic_boxes[0].text

    start = Node(None, (1, 1))
    end = Node(None, (board.rows - 2, board.columns - 2))
    path = []
    
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
                if buttons_list[1].buttons_rect.collidepoint(pygame.mouse.get_pos()):
                    board.random_generation(start, end)
                if event.button == 4 and board.rows > 10:
                    board.rows -= 5
                    board.columns -= 5
                    start.position = (1, 1)
                    end.position = (board.rows - 2, board.columns - 2)
                    board.update(board.rows, board.columns)
                elif event.button == 5 and board.rows < 50:
                    board.rows += 5
                    board.columns += 5
                    start.position = (1, 1)
                    end.position = (board.rows - 2, board.columns - 2)
                    board.update(board.rows, board.columns)
                path = []
            if event.type == pygame.MOUSEBUTTONUP and buttons_list[1].isPressed:
                buttons_list[1].isPressed = False
            
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
        
        if algorithm == "A*":
            for heuristic_box in heuristic_boxes:
                heuristic_box.draw()
                if heuristic_box.is_checked:
                    heuristic = heuristic_box.text
        if path != None:
            draw_path(BLUE, path, board.width)
        pygame.display.update()
        
        mouse_inputs = pygame.mouse.get_pressed()

        for row in range(board.rows):
            for col in range(board.columns):
                rect = pygame.Rect(col * board.width +1, row * board.width +1, math.ceil(board.width -1), math.ceil(board.width -1))
                if mouse_inputs[0]:
                    path = []
                    if start.get_node_rect(board.width).collidepoint(pygame.mouse.get_pos()) and can_place_walls == False and can_remove_walls == False:
                        can_move_start = True
                    elif end.get_node_rect(board.width).collidepoint(pygame.mouse.get_pos()) and can_place_walls == False and can_remove_walls == False:
                        can_move_end = True
                    elif rect.collidepoint(pygame.mouse.get_pos()) and board.graph[row][col] == "empty" and can_remove_walls == False:
                        can_place_walls = True
                    elif rect.collidepoint(pygame.mouse.get_pos()) and board.graph[row][col] == "wall" and can_place_walls == False:
                        can_remove_walls = True
                    elif buttons_list[0].buttons_rect.collidepoint(pygame.mouse.get_pos()):
                        board.clear_walls(row, col)
                        buttons_list[0].isPressed = False
                    elif buttons_list[2].buttons_rect.collidepoint(pygame.mouse.get_pos()):
                        if algorithm == "A*":
                            draw_path(WHITE, path, board.width)
                            path = a_star(board.graph,
                                          board.width,
                                          start,
                                          end,
                                          heuristic,
                                          option_boxes[0].is_checked)
                        
                        elif algorithm == "Dijkstra":
                            print("Coming soon...")
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

            else:
                continue
            break


pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGTH))
pygame.display.set_caption("Pathfinder")
font = pygame.font.SysFont("arial", 20, True, True)
main()