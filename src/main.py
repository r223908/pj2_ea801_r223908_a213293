from setup import *

# ==========================================
# FUNÇÕES DE HARDWARE (MOTORES E TELA)
# ==========================================
def printOled(velocidade, direcao, posicao_cvt, bt_conectado):
    texto_sentido = "Horario" if direcao == 1 else "Anti-Hor."  
    texto_sentido = "Parado" if velocidade == 0 else texto_sentido
    texto_bt = "ON" if bt_conectado == 1 else "OFF"
    display.fill(0)
    display.text("Câmbio CVT", 20, 0)
    display.text("-" * 16, 0, 10)
    display.text(f"Motor: {texto_sentido}", 0, 25)
    display.text(f"Pos. CVT: {posicao_cvt}%", 0, 40)
    display.text(f"Bluetooth: {texto_bt}", 0, 55) # Nova linha no final!
    display.show()

def controlar_motor_principal(velocidade_percentual, direcao, fazer_rampa=False):
    """Controla o motor primário e seu sentido, com opção de rampa na reversão"""
    
    # Se pediram rampa e o motor não está zerado
    if fazer_rampa and velocidade_percentual > 0:
        passos = 10 # Divide a aceleração/desaceleração em 10 etapas
        # Metade do tempo para desacelerar, metade para acelerar. Converte ms para segundos.
        tempo_por_passo = (TEMPO_RAMPA_MS / 2000) / passos 
        passo_pwm = max(1, velocidade_percentual // passos)
        
        # 1. Rampa de descida (Freia suavemente mantendo a direção antiga)
        for v in range(velocidade_percentual, -1, -passo_pwm):
            Mprincipal_PWM.duty_u16(int((v / 100) * 65535))
            utime.sleep(tempo_por_passo)
            
        # 2. Desliga a Ponte H e inverte a direção
        Mprincipal_DIR1.value(0)
        Mprincipal_DIR2.value(0)
        Mprincipal_PWM.duty_u16(0)
        utime.sleep(0.05) # Pequena pausa de segurança mecânica
        
        if direcao == 1:
            Mprincipal_DIR1.value(1)
            Mprincipal_DIR2.value(0)
        else:
            Mprincipal_DIR1.value(0)
            Mprincipal_DIR2.value(1)
            
        # 3. Rampa de subida (Acelera suavemente no sentido novo)
        for v in range(0, velocidade_percentual + 1, passo_pwm):
            Mprincipal_PWM.duty_u16(int((v / 100) * 65535))
            utime.sleep(tempo_por_passo)
            
        # Garante que cravou exatamente na velocidade alvo no final da rampa
        Mprincipal_PWM.duty_u16(int((velocidade_percentual / 100) * 65535))

    else:
        # Comportamento direto (Ligar do zero ou Parada de emergência)
        if velocidade_percentual > 0:
            if direcao == 1:
                Mprincipal_DIR1.value(1)
                Mprincipal_DIR2.value(0)
            else:
                Mprincipal_DIR1.value(0)
                Mprincipal_DIR2.value(1)
        else:
            Mprincipal_DIR1.value(0)
            Mprincipal_DIR2.value(0)
            
        Mprincipal_PWM.duty_u16(int((velocidade_percentual / 100) * 65535))

def mover_atuador_cvt(acao):
    pass


# ==========================================
# Função de Interrupção dos Botões
# ==========================================
def trata_interrupcao_botao(pino):
    global cor_travada, ultimo_tempo_btn
    tempo_atual = utime.ticks_ms()
    if utime.ticks_diff(tempo_atual, ultimo_tempo_btn) > 200:
        if pino == botao_a:
            cor_travada = corVermelha
        elif pino == botao_b:
            cor_travada = corAzul
        elif pino == botao_c:
            cor_travada = corVerde
        ultimo_tempo_btn = tempo_atual

botao_a.irq(trigger=Pin.IRQ_FALLING, handler=trata_interrupcao_botao)
botao_b.irq(trigger=Pin.IRQ_FALLING, handler=trata_interrupcao_botao)
botao_c.irq(trigger=Pin.IRQ_FALLING, handler=trata_interrupcao_botao)




# ==========================================
# INICIALIZAÇÃO E LOOP PRINCIPAL
# ==========================================

ultimo_tempo_pisca = utime.ticks_ms()
ultimo_tempo_oled = utime.ticks_ms()

velocidade_atual = 0
direcao_motor = 1 
posicao_cvt = 0  

for i in range(NUM_LEDS):
    np[i] = (0, 0, 0)
np.write()

print("Aguardando comandos Bluetooth...")

while True:
    tempo_atual = utime.ticks_ms()
    
    # 1. ATUALIZAÇÃO DO DISPLAY OLED
    if utime.ticks_diff(tempo_atual, ultimo_tempo_oled) >= ATT_DISPLAY_MS:
        # Lemos o valor do pino na hora de atualizar a tela (vai retornar 1 ou 0)
        estado_conexao = status_bt.value()

        # Parada de emergência se perder a conexão com rampa de desaceleração
        if estado_conexao == 0 and velocidade_atual > 0:
            passos = 10                                             #Faz a rampa de desaceleração suave
            tempo_por_passo = (TEMPO_RAMPA_MS / 2000) / passos
            passo_pwm = max(1, velocidade_atual // passos)
            for v in range(velocidade_atual, -1, -passo_pwm):
                Mprincipal_PWM.duty_u16(int((v / 100) * 65535))
                utime.sleep(tempo_por_passo)
            velocidade_atual = 0                                    #zera as variáveis e garante o motor desligado
            controlar_motor_principal(0, direcao_motor)

        printOled(velocidade_atual, direcao_motor, posicao_cvt, estado_conexao)
        ultimo_tempo_oled = tempo_atual

    # 2. LEITURA DE COMANDOS BLUETOOTH
    if bluetooth.any():
        try:
            dados_brutos = bluetooth.read()
            if dados_brutos is not None:
                comando = dados_brutos.decode('utf-8').strip().upper()

                if comando:
                    led_azul.value(1) 
                    
                    if comando == startDir: 
                        velocidade_atual = 100
                        controlar_motor_principal(velocidade_atual, direcao_motor)
                        
                    elif comando == frontDir: 
                        # Verifica se está invertendo o sentido com o motor rodando
                        deve_fazer_rampa = (direcao_motor == -1 and velocidade_atual > 0)
                        direcao_motor = 1
                        controlar_motor_principal(velocidade_atual, direcao_motor, deve_fazer_rampa)
                        
                    elif comando == backDir: 
                        # Verifica se está invertendo o sentido com o motor rodando
                        deve_fazer_rampa = (direcao_motor == 1 and velocidade_atual > 0)
                        direcao_motor = -1
                        controlar_motor_principal(velocidade_atual, direcao_motor, deve_fazer_rampa)
                        
                    elif comando == triangleDir: 
                        posicao_cvt = min(100, posicao_cvt + 10)
                        
                    elif comando == crossDir: 
                        posicao_cvt = max(0, posicao_cvt - 10)
                        
                    elif comando == pauseDir: 
                        velocidade_atual = 0
                        controlar_motor_principal(0, direcao_motor)
                    
                    led_azul.value(0)
        except UnicodeError:
            pass 

    # 3. ANIMAÇÃO DA MATRIZ DE LEDS
    np.fill((0, 0, 0))
    if posicao_cvt == 0 or velocidade_atual == 0:
        np[LED_MEIO] = cor_travada 
    else:
        leds_por_segundo = (posicao_cvt / 100) * MAX_LEDS_POR_SEGUNDO
        leds_por_segundo = .1 if leds_por_segundo < 0.1 else leds_por_segundo
        intervalo_ms = int(1000 / leds_por_segundo)
        
        if utime.ticks_diff(tempo_atual, ultimo_tempo_pisca) >= intervalo_ms:    
            if direcao_motor == 1:
                indice_frame = (indice_frame + 1) % len(FRAMES_MOTOR)
            else:
                indice_frame = (indice_frame - 1) % len(FRAMES_MOTOR)
                
            ultimo_tempo_pisca = tempo_atual
            
        for led in FRAMES_MOTOR[indice_frame]:
            np[led] = cor_travada
    np.write()
    
    utime.sleep(0.01)