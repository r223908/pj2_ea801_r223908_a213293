from setup import *

# ==========================================
# FUNÇÕES DE HARDWARE (MOTORES E TELA)
# ==========================================

# Atualizado para receber a variável numérica da posição do CVT
def printOled(velocidade, posicao_cvt):
    display.fill(0)     # Limpa a tela antes de desenhar os novos dados
    display.text("Projeto CVT", 20, 0)     # Cabeçalho
    display.text("-" * 16, 0, 10)
    
    display.text(f"Motor: {velocidade}%", 0, 25)
    display.text(f"Posicao CVT: {posicao_cvt}%", 0, 40)
    display.show()

def controlar_motor_principal(velocidade_percentual):
    """Controla o motor primário (0 a 100%)"""
    if velocidade_percentual > 0:
        Mprincipal_DIR1.value(1)
        Mprincipal_DIR2.value(0)
    else:
        Mprincipal_DIR1.value(0)
        Mprincipal_DIR2.value(0)
    Mprincipal_PWM.duty_u16(int((velocidade_percentual / 100) * 65535))

# A função de mover o atuador físico fica guardada para o futuro
def mover_atuador_cvt(acao):
    pass # Implementaremos o PWM físico aqui futuramente


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


# ==========================================
# INICIALIZAÇÃO E LOOP PRINCIPAL
# ==========================================

ultimo_tempo_pisca = utime.ticks_ms()
ultimo_tempo_oled = utime.ticks_ms()

velocidade_atual = 0
posicao_cvt = 0 # Nova variável de estado do CVT (0 a 100%)

for i in range(NUM_LEDS):
    np[i] = (0, 0, 0)
np.write()

print("Aguardando comandos Bluetooth...")

while True:
    tempo_atual = utime.ticks_ms()
    
    # 1. ATUALIZAÇÃO DO DISPLAY OLED
    if utime.ticks_diff(tempo_atual, ultimo_tempo_oled) >= ATT_DISPLAY_MS:
        printOled(velocidade_atual, posicao_cvt)
        ultimo_tempo_oled = tempo_atual

    # 2. LEITURA DE COMANDOS BLUETOOTH
    if bluetooth.any():
        try:
            dados_brutos = bluetooth.read()
            if dados_brutos is not None:
                comando = dados_brutos.decode('utf-8').strip().upper()

            if comando:
                led_azul.value(1) # Feedback de recebimento
                
                # --- Lógica de Controle Atualizada ---
                if comando == startDir: # LIGA motor principal em 100%
                    velocidade_atual = 100
                    controlar_motor_principal(velocidade_atual)
                    
                elif comando == triangleDir: # Sobe marcha (Move CVT)
                    # Incrementa a posição virtual em passos de 10%
                    posicao_cvt = min(100, posicao_cvt + 10)
                    
                elif comando == crossDir: # Desce marcha (Move CVT)
                    # Decrementa a posição virtual em passos de 10%
                    posicao_cvt = max(0, posicao_cvt - 10)
                    
                elif comando == outButtonDir or comando == pauseDir: # PARADA de emergência / Desliga motor
                    velocidade_atual = 0
                    controlar_motor_principal(0)
                    # Nota: mantive a posicao_cvt onde estava. Se quiser que ela zere na parada, adicione: posicao_cvt = 0
                
                led_azul.value(0)
        except UnicodeError:
            pass # Ignora lixos na serial

    # 3. ANIMAÇÃO DA MATRIZ DE LEDS (Baseada na posicao_cvt)
    np.fill((0, 0, 0))
    if posicao_cvt == 0:
        np[LED_MEIO] = cor_travada  
    else:
        # A velocidade do motor virtual na matriz reflete a posição do CVT (0 a 100)
        leds_por_segundo = (posicao_cvt / 100) * MAX_LEDS_POR_SEGUNDO
        leds_por_segundo = .1 if leds_por_segundo < 0.1 else leds_por_segundo
        intervalo_ms = int(1000 / leds_por_segundo)
        
        if utime.ticks_diff(tempo_atual, ultimo_tempo_pisca) >= intervalo_ms:    
            indice_frame = (indice_frame + 1) % len(FRAMES_MOTOR)
            ultimo_tempo_pisca = tempo_atual
            
        for led in FRAMES_MOTOR[indice_frame]:
            np[led] = cor_travada
    np.write()
    
    utime.sleep(0.01)