import pygame, sys, math
from settings import *

class Board:
    def __init__(self, rows=20):
        self.init_board(rows)
        self.buttons = [Button("Clear", (0, HEIGHT - 200)), Button("Generate", (WIDTH // 2, HEIGHT - 200))]
        self.checkboxes = [CheckBox("A*", (20, HEIGHT - 120), True), 
                           CheckBox("Dijkstra", (20, HEIGHT - 60)),
                           CheckBox("Diagonal", (300, HEIGHT - 120)),
                           CheckBox("Manhattan", (500, HEIGHT - 120), True),
                           CheckBox("Euclidean", (500, HEIGHT - 60))]
        
        self.algo = self.checkboxes[0].text
        self.diagonal = self.checkboxes[2].is_checked
        self.distance = self.checkboxes[3].text

    def set_search_options(self, selected, *others): # Sets the search options
        selected.is_checked = True
        for checkbox in others:
            checkbox.is_checked = False

    def create_board(self): # Creates 2D list which represents the board
        board = [[Node(self, (row, col)) for col in range(self.columns)] for row in range(self.rows)]
        board[1][1].node_type = "start"
        board[self.rows-2][self.columns-2].node_type = "end"

        return board

    def init_board(self, rows): # Resets the class attibutes when changing the size of the grid
        self.rows = self.columns = rows
        self.node_width = self.node_height = WIDTH / self.rows
        self.board = self.create_board()

        self.start = self.board[1][1]
        self.end = self.board[self.rows-2][self.columns-2]
        self.move_start = self.move_end = False

    def draw(self, surface, freeze=False, only_board=False): # Draws the board
        for nodes in self.board:
            for node in nodes:
                node.draw(self, surface)
        
        for row in range(self.rows + 1):
            pygame.draw.line(surface, BLACK, (0, row * self.node_height), (WIDTH, row * self.node_height), 1)
        
        for col in range(self.columns + 1):
            pygame.draw.line(surface, BLACK, (col * self.node_width, 0), (col * self.node_width, HEIGHT - 200), 1)

        if not only_board:
            for button in self.buttons:
                button.draw(surface)

            for checkbox in self.checkboxes:
                checkbox.draw(surface)

        pygame.display.update()
        if freeze:
            pygame.time.wait(2)

    def user_input(self): # Gets user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4 and self.rows > 10:
                    self.rows = self.columns = SCROLLS[SCROLLS.index(self.rows)-1]
                    self.init_board(self.rows)
                if event.button == 5 and self.rows < 50:
                    self.rows = self.columns = SCROLLS[SCROLLS.index(self.rows)+1]
                    self.init_board(self.rows)
                if event.button == 1:
                    if self.checkboxes[0].rect.collidepoint(event.pos) and not self.checkboxes[0].is_checked:
                        self.set_search_options(self.checkboxes[0], self.checkboxes[1])
                        self.algo = self.checkboxes[0].text
                    elif self.checkboxes[1].rect.collidepoint(event.pos) and not self.checkboxes[1].is_checked:
                        self.set_search_options(self.checkboxes[1], self.checkboxes[0])
                        self.algo = self.checkboxes[1].text
                    
                    if self.checkboxes[3].rect.collidepoint(event.pos) and not self.checkboxes[3].is_checked:
                        self.set_search_options(self.checkboxes[3], self.checkboxes[4])
                        self.distance = self.checkboxes[3].text
                    elif self.checkboxes[4].rect.collidepoint(event.pos) and not self.checkboxes[4].is_checked:
                        self.set_search_options(self.checkboxes[4], self.checkboxes[3])
                        self.distance = self.checkboxes[4].text

                    if self.checkboxes[2].rect.collidepoint(event.pos):
                        if self.checkboxes[2].is_checked:
                            self.checkboxes[2].is_checked = False
                            self.diagonal = False
                        else:
                            self.checkboxes[2].is_checked = True
                            self.diagonal = True
                    
                    for button in self.buttons:
                        if button.rect.collidepoint(event.pos):
                            if button.rect.left == 0:
                                self.init_board(self.rows)
                            else:
                                self.shortest_path(self.algo, self.distance, self.diagonal)
        
        keys = pygame.mouse.get_pressed()
        for nodes in self.board:
            for node in nodes:                
                if node.rect.collidepoint(pygame.mouse.get_pos()):
                    if keys[0]:
                        if node.node_type == "start":
                            self.move_start = True
                        elif node.node_type == "end":
                            self.move_end = True                        
                        elif node.node_type == "empty" and not self.move_start and not self.move_end:
                            node.node_type = "wall"
                    elif keys[2]:
                        if node.node_type == "wall":
                            node.node_type = "empty"
                
                if (self.move_start and node.node_type == "start") or (self.move_end and node.node_type == "end"):
                    node.node_type = "empty"
                if node.rect.collidepoint(pygame.mouse.get_pos()) and node.node_type == "empty":
                    if self.move_start:
                        node.node_type = "start"
                        self.start = node
                    elif self.move_end:
                        node.node_type = "end"
                        self.end = node
                
                if not keys[0]:
                    self.move_start = False
                    self.move_end = False

    def heuristic(self, start, end, distance): # Calculating the heuristic cost (h cost)
        if distance == "Manhattan":
            return abs(start.x - end.x) + abs(start.y - end.y)
        if distance == "Euclidean":
            return math.sqrt(((start.x - end.x) ** 2) + ((start.y - end.y) ** 2))

    def reconstruct_path(self, current_node): # Reconstruct the shortest path between the two nodes
        path = []
        current = current_node
        while current:
            if not path:
                current.set_type("end")
            else:
                current.set_type("path")
            path.append(current)
            current = current.parent
            self.draw(pygame.display.get_surface(), True)

        return path

    def shortest_path(self, algo, distance, allow_diagonal): # Finds the shortest using A* or Dijkstra algorighm
        open_list = [self.start]    
        closed_list = []
        
        if algo == "A*":
            self.start.h = self.heuristic(self.start.position, self.end.position, distance)
            self.start.f = self.start.h

        possible_moves = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    
        if allow_diagonal: # Adding optional moves depending on the value of "allow_diagonal"
            possible_moves.extend([(1, 1), (-1, 1), (-1, -1), (1, -1)])

        while open_list:
            current_node = open_list[0]
            for node in open_list:
                if node.f < current_node.f:
                    current_node = node
            
            if current_node == self.end: # End condition
                return self.reconstruct_path(current_node)

            current_node.set_type("current")
            self.draw(pygame.display.get_surface(), True, True)
            
            open_list.remove(current_node)
            closed_list.append(current_node)

            for pos in possible_moves: # Lopping through every possible neighbour
                neighbour_pos = pygame.math.Vector2(current_node.position.x + pos[0], current_node.position.y + pos[1])
                if neighbour_pos.x not in set(range(0, self.columns)) or neighbour_pos.y not in set(range(0, self.rows)):
                    continue
                
                neighbour = self.board[int(neighbour_pos.x)][int(neighbour_pos.y)]

                if neighbour in closed_list:
                    continue
                if neighbour.node_type != "empty" and neighbour.node_type != "end":
                    continue

                neighbour.set_type("neighbour")
                neighbour.parent = current_node
                self.draw(pygame.display.get_surface(), True, True)
                
                if algo == "A*":
                    neighbour.g = current_node.g + 1
                    neighbour.h = self.heuristic(neighbour.position, self.end.position, distance)
                    neighbour.f = neighbour.g + neighbour.h

                    for open_node in open_list:
                        if open_node == neighbour and neighbour.g < open_node.g:
                            open_node.g = neighbour.g
                            open_node.parent = neighbour.parent
                            continue
                
                elif algo == "Dijkstra":
                    cost = current_node.f + 1
                    if cost < neighbour.f:
                        neighbour.f = cost
                
                open_list.append(neighbour)

        return False
                

class Node:
    def __init__(self, board, position, node_type="empty"):
        self.position = pygame.math.Vector2(position)
        self.node_type = node_type
        self.parent = None

        self.f = 0 # f cost
        self.g = 0 # g cost
        self.h = 0 # h cost

        self.image = pygame.Surface((board.node_width, board.node_height))
        self.rect = self.image.get_rect(topleft=(self.position.x * board.node_height, self.position.y * board.node_width))

    def set_type(self, node_type): # Sets the type of the node
        if self.node_type != "start":
            self.node_type = node_type

    def draw(self, board, surface): # Draws the node
        self.image.fill(NODE_COLOR[self.node_type])
        surface.blit(self.image, (self.position.x * board.node_height, self.position.y * board.node_width))


class Button:
    def __init__(self, text, pos):
        self.image = pygame.Surface((WIDTH // 2, 50))
        self.rect = self.image.get_rect(topleft=pos)

        self.font = pygame.font.SysFont("arial", 20, True, True)
        self.text = self.font.render(text, 1, BLACK)

    def draw(self, surface): # Draws the button
        self.image.fill(CERISE)        
        pygame.draw.rect(self.image, BLACK, (0, 0, WIDTH // 2, 50), 1)
        self.image.blit(self.text, (0, 0))
        surface.blit(self.image, self.rect)


class CheckBox:
    def __init__(self, text, pos, is_checked=False):
        self.text = text
        self.image = pygame.Surface((30, 30))
        self.rect = self.image.get_rect(topleft=pos)

        self.font = pygame.font.SysFont("arial", 20, True, True)
        self.message = self.font.render(text, 1, BLACK)
        self.is_checked = is_checked

    def draw(self, surface): # Draws the checkbox
        if self.is_checked:
            self.image.fill(BLACK)
        else:
            self.image.fill(WHITE)
        pygame.draw.rect(self.image, BLACK, (0, 0, 30, 30), 1)
        
        surface.blit(self.message, (self.rect.right + 10, self.rect.top + 5))
        surface.blit(self.image, self.rect)


class Game:
    def __init__(self):
        pygame.init()
        self.win = pygame.display.set_mode((WIDTH, HEIGHT))
        self.board = Board()

    def run(self): # Main game loop
        while True:
            self.board.user_input()
            
            self.win.fill(WHITE)
            self.board.draw(self.win)

if __name__ == "__main__":
    game = Game()
    game.run()