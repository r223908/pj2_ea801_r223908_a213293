from setup import *

# Função de Interrupção dos Botões
def trata_interrupcao_botao(pino):
    global cor_travada, ultimo_tempo_btn
    tempo_atual = utime.ticks_ms()
    # "Debounce" de 200ms
    if utime.ticks_diff(tempo_atual, ultimo_tempo_btn) > 200:
        if pino == botao_a:
            cor_travada = corVermelha
        elif pino == botao_b:
            cor_travada = corAzul
        elif pino == botao_c:
            cor_travada = corVerde
        ultimo_tempo_btn = tempo_atual

# Atribuir as interrupções aos botões
botao_a.irq(trigger=Pin.IRQ_FALLING, handler=trata_interrupcao_botao)
botao_b.irq(trigger=Pin.IRQ_FALLING, handler=trata_interrupcao_botao)
botao_c.irq(trigger=Pin.IRQ_FALLING, handler=trata_interrupcao_botao)

def printOled(desvio):
    display.fill(0)     # Limpa a tela antes de desenhar os novos dados
    display.text("BitDogLab V7", 16, 0)     # Cabeçalho
    display.text("-" * 16, 0, 10)
    
    if abs(desvio) <= ZONA_MORTA:   # 1. Lógica para descobrir a velocidade (%) e o sentido
        porcentagem = 0
        texto_sentido = "Parado"
    else:
        # Fator de 0.0 a 1.0 transformado em 0 a 100
        porcentagem = 100* (abs(desvio) - ZONA_MORTA) / (32768 - ZONA_MORTA)
        # Trava em 100% caso o ADC do joystick passe um pouquinho do limite
        porcentagem = 100 if porcentagem>100 else porcentagem
        # Define o sentido baseado no eixo Y (se precisar inverter, é só trocar o < por > aqui)
        texto_sentido = "Horario" if desvio < 0 else "Anti-horario"
    # 2. Plota as informações calculadas
    display.text("Sentido:", 0, 25)
    display.text(texto_sentido, 0, 35) # Coloquei na linha de baixo para não cortar o texto
    display.text(f"Velocidade: {porcentagem}%", 0, 50)
    display.show()

def buzzerSound():
    # Se o valor for 0 (pressionado), liga o som. Se for 1 (solto), desliga.
    if joystick_sw.value() == 0:
        buzzer.freq(1000)        # Frequência do som (1000 Hz = um apito médio/agudo)
        buzzer.duty_u16(32768)   # Volume em 50% (metade de 65535)
    else:
        buzzer.duty_u16(0)       # Volume 0 (Desliga o buzzer)


ultimo_tempo_pisca = utime.ticks_ms()
ultimo_tempo_oled = utime.ticks_ms()
estado_led_motor = False
for i in range(NUM_LEDS):   # Garante que todos os LEDs começam apagados
    np[i] = (0, 0, 0)
np.write()

# Ciclo Principal (Independente dos Botões)
while True:
    # 1. Pega o tempo atual logo no início para todo mundo usar
    tempo_atual = utime.ticks_ms()
    # 2. Leitura do joystick
    valor_y = joystick_y.read_u16()
    desvio = valor_y - CENTRO_JOYSTICK
    # 3. Atualizamos a tela APENAS a cada ATT_DISPLAY_MS ms
    if utime.ticks_diff(tempo_atual, ultimo_tempo_oled) >= ATT_DISPLAY_MS:
        printOled(desvio)
        ultimo_tempo_oled = tempo_atual
    np.fill((0, 0, 0))      # Limpa TODOS os LEDs da matriz de uma vez. 

    buzzerSound()           # 4. Só faz o som se o joystick for pressionado

    if abs(desvio) <= ZONA_MORTA:   # 5. Zona Morta (Parado)
        np[LED_MEIO] = cor_travada  
    else:       # 6. Fora da Zona Morta (Em movimento)
        fator_velocidade = (abs(desvio) - ZONA_MORTA) / (32768 - ZONA_MORTA)
        leds_por_segundo = fator_velocidade * MAX_LEDS_POR_SEGUNDO
        leds_por_segundo = .1 if leds_por_segundo < 0.1 else leds_por_segundo
        intervalo_ms = int(1000 / leds_por_segundo)     # intervalo para correr o frame do motor inteiro

        tempo_atual = utime.ticks_ms()
        # 6.a. Lógica do Buffer Circular do frame do motor
        if utime.ticks_diff(tempo_atual, ultimo_tempo_pisca) >= intervalo_ms:    
            if desvio < 0:  # Gira para um lado (avança na lista)
                indice_frame = (indice_frame + 1) % len(FRAMES_MOTOR)
            else:   # Gira para o outro lado (retrocede na lista)
                indice_frame = (indice_frame - 1) % len(FRAMES_MOTOR)
            ultimo_tempo_pisca = tempo_atual
        # Acende os LEDs correspondentes ao frame atual na cor escolhida
        for led in FRAMES_MOTOR[indice_frame]:
            np[led] = cor_travada
    np.write()          # Envia o desenho para a matriz fisicamente
    utime.sleep(0.01)   # 10 ms