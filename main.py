# -*- coding: utf-8 -*-

import pygame
import os
import math
import sys
import random
import neat

screen_width = 1400
screen_height = 900
generation = 0

class Car:
    def __init__(self):
        self.surface = pygame.image.load("car.png")
        self.surface = pygame.transform.scale(self.surface, (100, 100)) ## escala do carro (tamanho)
        self.rotate_surface = self.surface
        ##posição onde o carro irá começar
        self.pos = [700, 650] 
        self.angle = 0
        self.speed = 0
        self.center = [self.pos[0] + 50, self.pos[1] + 50]
        self.radars = []
        self.radars_for_draw = []
        self.is_alive = True
        self.goal = False
        self.distance = 0
        self.time_spent = 0

    def draw(self, screen): ## desenho das linhas
        #blit (pygame) consigo desenhar em determinado pixel da tela
        screen.blit(self.rotate_surface, self.pos)
        #self.desenharRadar(screen) 

    ##desenho do radar
    def desenharRadar(self, screen):
        for r in self.radars:
            pos, dist = r
            pygame.draw.line(screen, (0, 255, 0), self.center, pos, 1) 

    def colisao_check(self, map):
        self.is_alive = True
        ##verificação da colisao dos pontos
        for p in self.four_points:

            #verifcao para pegar o valor da cor de um unico pixel(x,y). Se for igual a cor branca em hex, então o carro bateu.
            #get_at (PYGAME)
            if map.get_at((int(p[0]), int(p[1]))) == (255, 255, 255, 255): 
                self.is_alive = False
                break

    def check_radar(self, degree, map):
        tamanho = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * tamanho)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * tamanho)

        while not map.get_at((x, y)) == (255, 255, 255, 255) and tamanho < 300:
            
            tamanho = tamanho + 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * tamanho)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * tamanho)

        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))

        self.radars.append([(x, y), dist])

    def atualizacao(self, map):
        #Velocidade
        self.speed = 15

        #Posição / andar
        self.rotate_surface = self.rot_center(self.surface, self.angle)
        self.pos[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        if self.pos[0] < 20:
            self.pos[0] = 20
        elif self.pos[0] > screen_width - 120:
            self.pos[0] = screen_width - 120

        self.distance += self.speed
        self.time_spent += 1
        self.pos[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        if self.pos[1] < 20:
            self.pos[1] = 20
        elif self.pos[1] > screen_height - 120:
            self.pos[1] = screen_height - 120

        # Calculo dos 4 pontos de colisao
        self.center = [int(self.pos[0]) + 50, int(self.pos[1]) + 50]
        ##tamanho do carro
        tamanho = 40
        esquerda_cima = [self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * tamanho, self.center[1]
         + math.sin(math.radians(360 - (self.angle + 30))) * tamanho]
        direita_cima = [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * tamanho, self.center[1] 
        + math.sin(math.radians(360 - (self.angle + 150))) * tamanho]
        esquerda_baixo = [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * tamanho, self.center[1] 
        + math.sin(math.radians(360 - (self.angle + 210))) * tamanho]
        direito_baixo = [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * tamanho, self.center[1] 
        + math.sin(math.radians(360 - (self.angle + 330))) * tamanho]
        self.four_points = [esquerda_cima, direita_cima, esquerda_baixo, direito_baixo]

        self.colisao_check(map)
        self.radars.clear()
        ##  faço for num range de -90 a 50 decremetando sempre 45. A distancia de quanto o carro vai conseguir ver pelos sensores (parte da dor da cabeça)
        for d in range(-90, 50, 45):
            self.check_radar(d, map)

    def get_data(self):
        radars = self.radars
        ret = [0, 0, 0, 0, 0]
        for i, r in enumerate(radars):
            ret[i] = int(r[1] / 30)
        return ret

    def vivo(self):
        return self.is_alive

    def recompensa(self):
        return self.distance

    def rot_center(self, image, angle):
        orig_rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image

def run_car(genomes, config):

    # Inicializando NEAT

    ## Criando listas contendo o próprio genoma
    nets = []
    ##Lista dos carros
    cars = []

    ## Irá fazer a inicialização dos genomas e a população size e com isso será preciso criar cada rede e genomes fitness
    for id, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0
    ## Fim inicialização


        # Inicializando a classe dos carros
        cars.append(Car())

    # Inicializando o jogo
    
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    #printando na tela as fontes das escritas
    generation_font = pygame.font.SysFont("Arial", 50)
    font = pygame.font.SysFont("Arial", 30)
    map = pygame.image.load('map2.png')


    # ------------------- LOOP PRINCIPAL -------------------- #
    global generation
    generation += 1

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        # Inserindo os dados e pegando os dados da rede
        for index, car in enumerate(cars):## cada carro coloca os seus dados na rede e pega a melhor ação e vira o angulo de acordo com a ação

            ## mandar a posição dos radar (sensores) e determinar com o resultado da rede que vai chegar se viro o angulo para direita ou para esquerda 
            output = nets[index].activate(car.get_data())
            ##retorno da funcao de ativacao (tanh)
            i = output.index(max(output))

            ## O angulo que o carro irá realizar conforme o resultado da funcao de ativacao
            if i <= 0.5:
                car.angle += 10
            else:
                car.angle -= 10

        # Atualizando o carro e o fitness
        carros_restant = 0
        for i, car in enumerate(cars):
            if car.vivo():
                carros_restant += 1
                car.atualizacao(map)
                genomes[i][1].fitness += car.recompensa() ## Dar uma recompensa para que o carro continue no trajeto (que continue vivo)

    # ------------------- FIM LOOP PRINCIPAL -------------------- #

        # Verificação dos carros se estao vivos, caso não estiverem a geração acaba
        if carros_restant == 0:
            break

        # Desenho 
        screen.blit(map, (0, 0))
        for car in cars:
            if car.vivo():
                car.draw(screen)

        text = generation_font.render("Geração: " + str(generation), True, (0,0,0))
        text_rect = text.get_rect()
        text_rect.center = (screen_width/2, 20)
        screen.blit(text, text_rect)

        text = font.render("Carros vivos: " + str(carros_restant), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (screen_width/2, 200)
        screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    
    caminho = "./config-feedforward.txt"
    config = neat.config.Config(neat.DefaultGenome, 
    neat.DefaultReproduction, neat.DefaultSpeciesSet, 
    neat.DefaultStagnation, caminho)

    # Criando o core da evolução da classe do algoritmo
    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Rodando o NEAT com o máximo de geração threshold
    p.run(run_car)
