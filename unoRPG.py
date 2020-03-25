# -*- coding: utf-8 -*-
# python3 unoRPG.py
# feito por Paulo Almeida 2020

from random import randint, shuffle
import time

numero_cartas_inicio = 7
xp_inicio = 10

class Baralho():
    def __init__(self):
        self.cartas = []
        self.lixo = []
        cores = ['vermelho','verde','azul','amarelo']
        for cor in cores:
            # duas vezes numeros de 1-9 e 0
            for num in range(1,19+1):
                num = num % 10
                self.cartas.append(Carta(num,cor,'nada'))
            # adiciono 2 cartas +2, inverte e bloqueio da mesma cor
            for _ in range(2):
                self.cartas.append(Carta(-1,cor,'+2'))
                self.cartas.append(Carta(-2,cor,'inverte'))
                self.cartas.append(Carta(-3,cor,'bloqueio'))
        # adiciono 4 cartas +4 e mudar cor
        for _ in range(4):
            self.cartas.append(Carta(-4,'preto','+4'))
            self.cartas.append(Carta(-5,'preto','mudar cor'))

    def embaralhar(self):
        shuffle(self.cartas)
    def pegar_carta(self):
        if (len(self.cartas) == 0):
            self.repor_cartas()
        return self.cartas.pop()
    def repor_cartas(self):
        self.cartas = self.lixo
        self.lixo = []
        self.embaralhar()
    def add_lixo(self,carta):
        self.lixo.append(carta)

class Carta():
    def __init__(self,num,cor,especial):
        self.num = num
        self.cor = cor
        self.especial = especial

    def same_cor(self,carta):
        return carta.cor == self.cor or carta.cor == 'preto'
    def same_num(self,carta):
        return carta.num == self.num
    def is_especial(self):
        return self.especial != 'nada'
    def ler(self):
        # cartas especiais
        if self.is_especial():
            return (self.especial+" "+str(self.cor))
        # cartas normais
        else:
            return (str(self.num)+" "+str(self.cor))

class Jogador():
    def __init__(self,nome,st,dx,iq):
        self.vivo = True
        self.nome = nome
        self.cartas = []
        self.st = st
        self.dx = dx
        self.iq = iq

    def add_carta(self,carta):
        self.cartas.append(carta)
    def qtd_cartas(self):
        return len(self.cartas)
    def morrer(self):
        self.vivo = False

class Bot(Jogador):
    def acao_turno(self,carta_topo):
        carta_select = None
        for carta in self.cartas:
            if (carta_topo.same_cor(carta) or carta_topo.same_num(carta)):
                carta_select = carta
                self.cartas.remove(carta)
                break
        return carta_select


class Mesa():
    def __init__(self, jogadores):
        self.jogadores = jogadores
        self.turno_jogador = 0
        self.baralho = Baralho()
        self.baralho.embaralhar()
        self.sentido_horario = True
        # dou cartas pros jogadores
        for _ in range(numero_cartas_inicio):
            for j in self.jogadores:
                j.add_carta(self.baralho.pegar_carta())
        # carta de inicio do game
        self.carta_topo = self.baralho.pegar_carta()
        # carta topo nao pode ser especial
        while (self.carta_topo.is_especial()):
            self.baralho.add_lixo(self.carta_topo)
            self.carta_topo = self.baralho.pegar_carta()

    def avancar_turno(self):
        sentido = 1 if self.sentido_horario else -1
        self.turno_jogador = (self.turno_jogador + sentido) % 4

    def jogador_comprar_carta(self, qtde):
        jogador_turno = self.jogadores[self.turno_jogador]
        for _ in range(qtde):
            jogador_turno.add_carta(self.baralho.pegar_carta())
        # avisar que jogador comprou
        texto = str(qtde) + (" carta" if (qtde == 1) else " cartas")
        print(jogador_turno.nome+"("+str(jogador_turno.qtd_cartas())+") comprou "+texto)
        # mais cartas que o jogador consegue carregar
        if jogador_turno.qtd_cartas() > (numero_cartas_inicio + jogador_turno.st):
            jogador_turno.morrer()
            print(jogador_turno.nome+" tentou carregar mais cartas do que conseguia e acabou morrendo esmagado")

    def jogar_carta(self,nova_carta):
        self.baralho.add_lixo(self.carta_topo)
        self.carta_topo = nova_carta
        # avisar que jogador jogou a carta
        jogador_turno = self.jogadores[self.turno_jogador]
        nome = jogador_turno.nome
        print(jogador_turno.nome+"("+str(jogador_turno.qtd_cartas())+")"+" jogou "+nova_carta.ler())

    def carta_especial_executar_acao(self,nova_cor):
        carta = self.carta_topo
        if   carta.especial == '+2':
            self.avancar_turno()
            jogador_turno = self.jogadores[self.turno_jogador]
            self.jogador_comprar_carta(2)
        elif carta.especial == 'inverte':
            print("Sentido das jogadas foi invertido")
            self.sentido_horario = not self.sentido_horario
        elif carta.especial == 'bloqueio':
            self.avancar_turno()
            jogador_turno = self.jogadores[self.turno_jogador]
            print("Pulado o turno de "+jogador_turno.nome+"("+str(jogador_turno.qtd_cartas())+")")
        elif carta.especial == '+4':
            self.avancar_turno()
            jogador_turno = self.jogadores[self.turno_jogador]
            self.jogador_comprar_carta(4)
            self.carta_topo.cor = nova_cor
            print("Cor escolhida: "+nova_cor)
        elif carta.especial == 'mudar cor':
            self.carta_topo.cor = nova_cor
            print("Cor escolhida: "+nova_cor)

    def falar_uno(self):
        jogador_turno = self.jogadores[self.turno_jogador]
        nome = jogador_turno.nome
        # procura jogador pra falar uno antes
        falaram_antes = False
        for j in self.jogadores:
            # n eh o mesmo jogador
            if j != jogador_turno:
                rand_j = randint(0,5)
                rand_jogador_turno = randint(0,9)
                if (j.dx + rand_j) > (jogador_turno.dx + rand_jogador_turno):
                    falaram_antes = True
                    print(j.nome+" falou uno antes que "+nome)
                    print("DXs:"+str(j.dx)+"+("+str(rand_j)+")           "+str(jogador_turno.dx)+"+("+str(rand_jogador_turno)+")")
                    time.sleep(3)
                    # comprar carta
                    self.jogador_comprar_carta(1)
                    break
        # caso ngm fale uno antes
        if (falaram_antes == False):
            print(jogador_turno.nome+" falou Uno")

def menu():
    print("Bem vindo a nossa cidade de Unopolis")
    print("Qual seu nome bravo aventureiro(a)?")
    nome = input()
    print("Tem certeza q é assim que você deseja ser chamado?")
    jump = input("(Escreva 'pular' para pular essa seção)\n")
    if (jump != "pular"):
        print("Nessas terras um forrasteiro como você pode ter qualquer nome "
            "que quiser, você pode muito bem mentir que não teria como ninguem "
            "descobrir, mas ok vou chamar você de "+nome+" de agora em diante" )

        time.sleep(4)
        print("\nCreio que você não esteja familiarizado com nosso sistema de "
            "descricao humana pela utilização de números do sistema decimal. "
            "Também conhecido como Atributos Básicos")
        time.sleep(4)
        print("ST representa sua força, ela determina a quantidade de cartas "
            " a mais, fora as iniciais, que você pode carregar")
        time.sleep(2)
        print("DX representa sua destreza, ela revela quem fala Uno mais rapido")
        time.sleep(2)
        print("IQ para sua inteligência, ela nao muda nada no jogo, não "
            "precisa ser muito inteligente pra jogar Uno")
        time.sleep(2)
        print("Olhando pra você através da camera do seu notebook eu diria... "
            "que uns 10 pontos tá mais que suficiente")
        time.sleep(2)
    # set ST
    feito = False
    while (not feito):
        st = input("Dos "+str(xp_inicio)+" restantes. "
            "Quantos pontos você quer gastar em ST (forca)? ")
        st = int(st)
        if (st <= xp_inicio and st >= 0): feito = True
        else: print("Não tente me enganar")
    # set DX
    feito = False
    while (not feito):
        dx = input("Dos "+str(xp_inicio-st)+" restantes. "
            "Quantos pontos você quer gastar em DX (destreza)? ")
        dx = int(dx)
        if (st + dx <= xp_inicio and dx >= 0): feito = True
        else: print("Não tente me enganar")
    # set IQ
    iq = input("Quantos pontos você quer gastar em IQ (inteligência)?"
        " Pode falar qualquer coisa eu não vou contar pra ver se esta certo ")
    iq = int(iq)

    time.sleep(1)
    print("Estou terminando sua ficha dê uma olhada")
    time.sleep(2)
    print("------------------------------")
    print("| Nome:"+nome)
    time.sleep(0.5)
    print("| ST:"+str(st))
    time.sleep(0.5)
    print("| DX:"+str(dx))
    time.sleep(0.5)
    print("| IQ:"+str(iq))
    print("------------------------------")
    time.sleep(1)
    print("Nossa... Me superei nessa, hahaha, acho que você percebeu que "
        "eu sou o artista da cidade, ou Sr.Da Vinci como alguns me chamam ")
    time.sleep(2)
    print("Acho que você já está pronto para entrar em um jogo, você concorda?")
    concorda = input("(Digite 'sim' para inciar partida)\n")
    while (concorda != "sim"):
        concorda = input("E agora?\n")
    # retorno
    print("Escolha a carta digitando o número que aparece a sua esquerda antes do 'dois pontos'")
    return Jogador(nome,st,dx,iq)

def gerar_bots():
    bots = []
    # bot 1
    st1 = randint(1,9)
    bots.append(Bot('Vivaldi',st1,(10 - st1),randint(0,10)))
    # bot 2
    st2 = randint(1,9)
    bots.append(Bot('Bach',st2,(10 - st2),randint(0,10)))
    # bot 3
    st3 = randint(1,9)
    bots.append(Bot('Van Gogh',st3,(10 - st3),randint(0,10)))
    # retorno
    return bots

def player_escolher_jogada(jogador, carta_topo):
    print("Seu turno, você possui:")
    # verifica se pode escolher alguma carta e printa as possibilidades
    possivel_carta = False
    for i in range(len(jogador.cartas)):
        carta = jogador.cartas[i]
        # verifica se a carta e possivel de ser jogada
        if (carta_topo.same_cor(carta) or carta_topo.same_num(carta)):
            possivel_carta = True
            print(str(i)+": "+carta.ler())
        # se nao for possivel
        else:
            print(str(i)+"  "+carta.ler())

    # se n tiver carta possivel
    if (not possivel_carta):
        print("Voce não possui nenhuma carta para jogar")
        time.sleep(2)
        return None

    # se houver carta possivel
    carta_select = None
    while True:
        print("Qual carta você escolhe?")
        n_carta = input()
        n_carta = int(n_carta)
        if (n_carta >= 0 and n_carta < jogador.qtd_cartas()):
            carta = jogador.cartas[int(n_carta)]
            if (carta_topo.same_cor(carta) or carta_topo.same_num(carta)):
                carta_select = carta
                jogador.cartas.remove(carta)
                break
            else:
                print("Você não pode jogar essa carta")

    return carta_select

def player_escolher_nova_cor():
    print("Qual será a próxima cor?\n(amarelo/azul/verde/vermelho)")
    nova_cor = input()
    while (nova_cor != "amarelo" and nova_cor != "azul" and nova_cor != "verde" and nova_cor != "vermelho"):
        print("Por favor digite uma das cores: amarelo/azul/verde/vermelho")
        nova_cor = input()
    return nova_cor

def game(jogadores):
    mesa = Mesa(jogadores)
    fim_jogo = False
    while not fim_jogo:
        turno_jogador   = mesa.turno_jogador
        jogador_turno   = mesa.jogadores[turno_jogador]
        if (jogador_turno.vivo):
            nome            = jogador_turno.nome
            carta_topo      = mesa.carta_topo
            # comunicacao
            print("\nCarta no topo: "+carta_topo.ler())
            time.sleep(2)
            # turno do player
            if (turno_jogador == 0):
                carta_jogada = player_escolher_jogada(jogador_turno,carta_topo)
            #turno dos bots
            else:
                carta_jogada = jogador_turno.acao_turno(carta_topo)
            # caso n tenha carta possivel para jogar
            if (carta_jogada == None):
                mesa.jogador_comprar_carta(1)
            else:
                mesa.jogar_carta(carta_jogada)
                # cartas especiais
                if carta_jogada.is_especial():
                    # mudar a cor  (por '+4' ou 'mudar cor')
                    nova_cor = None
                    if carta_jogada.cor == 'preto':
                        # turno do player
                        if (turno_jogador == 0):
                            nova_cor = player_escolher_nova_cor()
                        # bots
                        else:
                            r = randint(0,3)
                            if r == 0:   nova_cor = 'amarelo'
                            elif r == 1: nova_cor = 'azul'
                            elif r == 2: nova_cor = 'verde'
                            else:        nova_cor = 'vermelho'
                    # executar acao das cartas especiais
                    mesa.carta_especial_executar_acao(nova_cor)
                # gritar uno
                if (jogador_turno.qtd_cartas() == 1):
                    time.sleep(1)
                    mesa.falar_uno()
                # fim de jogo
                if (jogador_turno.qtd_cartas() == 0):
                    print(nome+" ganhou o jogo")
                    fim_jogo = True
            # final do turno do jogador
            time.sleep(2)
        mesa.avancar_turno()



def start():
    j1 = menu()
    # j1 = Jogador("Testerson",5,5,0)

    # criar jogadores
    jogadores = gerar_bots()
    jogadores.insert(0,j1)
    # iniciar jogo
    game(jogadores)


start()
