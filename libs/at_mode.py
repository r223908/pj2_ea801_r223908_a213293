import machine
import sys
import uselect
import utime

# Configura a UART0 nos pinos 0 (TX) e 1 (RX) - Conector J2
# O baud rate de 38400 é o padrão de fábrica para o modo AT do HC-05
uart = machine.UART(0, baudrate=38400, tx=machine.Pin(0), rx=machine.Pin(1))

print("==================================")
print("     Terminal AT para HC-05       ")
print("==================================")
print("Digite 'AT' e pressione Enter.")
print("A resposta deve ser 'OK'.")
print("==================================")

# Configura a entrada do teclado (terminal USB) para não bloquear o código
teclado = uselect.poll()
teclado.register(sys.stdin, uselect.POLLIN)

# Envia um "AT" inicial de teste (igual ao seu código C++)
uart.write('AT\r\n')

while True:
    # 1. Se chegou algo do HC-05, imprime no terminal do PC
    if uart.any():
        resposta = uart.read()
        try:
            print(resposta.decode('utf-8'), end='')
        except UnicodeError:
            print(resposta) # Imprime cru se houver lixo na serial
            
    # 2. Se você digitou algo no terminal do PC, envia para o HC-05
    if teclado.poll(0):
        comando = sys.stdin.readline().strip() # Lê o que foi digitado
        if comando:
            # O HC-05 exige que os comandos AT terminem com Carriage Return e Line Feed (\r\n)
            uart.write(comando + '\r\n')
            
    utime.sleep(0.01) # Pequena pausa para não sobrecarregar o processador