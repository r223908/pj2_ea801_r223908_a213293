### EA801 - PROJETO 2

### Câmbio CVT Físico com BitDogLab V7

**Autores:** 
- Raul Galdino Tancredo (RA: 223908 / [@r223908](https://github.com/r223908))
- Arthur Lucas Da Silva Nogueira (RA: 213293 / [@arthurnog](https://github.com/arthurnog)))

**Professor:** Eric Rohmer

* **Proposta de Projeto**: [Proposta em G-Docs](https://docs.google.com/document/d/18PMYSmtTR0OQQLU4SV4fV71K-Bi9EbMdW6YyoQtnZmc/edit?usp=sharing) (acesso "Comentador" para UNICAMP)
* **Relatório de projeto**: [Relatório em G-Docs](https://docs.google.com/document/d/1z_JGgpvWlYswWX_sQGRnS61v9bXmHXGZWmitXccoX50/edit?usp=sharing) (acesso "Comentador" para UNICAMP)
* **Demonstração do projeto no YouTube**: [Vídeo](a)

---
## ⚙️ DESCRIÇÃO DO SISTEMA (v0)
O sistema desenvolvido consiste na implementação de uma bancada de testes para um **Câmbio de Transmissão Continuamente Variável (CVT)** simulado, controlado remotamente via interface sem fio. O projeto utiliza a plataforma BitDogLab V7 como unidade central de processamento, integrando comunicação serial, controle de potência e telemetria.

O controle é dividido em dois eixos de atuação:
1. Eixo motor: Um motor de corrente contínua (DC), simulando a rotação do motor primário, controlado via PWM.
2. Atuador do câmbio: Um segundo motor acoplado a um sistema de fuso (atuador linear), responsável por alterar a posição física da correia do câmbio CVT.

A interface homem-máquina (IHM) é realizada de forma remota através de um módulo Bluetooth (conectado à interface UART da placa) com a integração de um aplicativo no celular. O display OLED da placa é utilizado para exibir a telemetria em tempo real.



<figure align="center">
  <img src="/docs/images/blockDiag_v0.png" width="100%" style="border: 2px solid black; border-radius: 8px;" alt="Diagrama de blocos do projeto">
  <figcaption><i>Figura 1: Diagrama de blocos do projeto.</i></figcaption>
</figure>

<figure align="center">
  <img src="/docs/images/referencia_lego_1.png" width="90%" style="border: 2px solid black; border-radius: 8px;" alt="Referência LEGO">
  <figcaption><i>Figura 1: Referência de projeto feito em LEGO.</i></figcaption>
</figure>


---
## ❗REQUISITOS
1. BitDogLab V7.
2. Ponte H L293D (CI) para ambos os motores.
3. Protoboard 400 pinos.
4. Jumpers.
5. Fonte regulável.
6. Cabo micro USB.
7. Ambiente de desenvolvimento configurado para MicroPython.

---
## 📚 REFERÊNCIAS
1. Repositório BitDogLab V7: [Repositório no GitHub](https://gitlab.unicamp.br/fabiano/bitdoglab-v7)
2. Banco de Informação de Hardware: [BitDogLabV7_BIH](https://docs.google.com/document/d/13-68OqiU7ISE8U2KPRUXT2ISeBl3WPhXjGDFH52eWlU/edit?tab=t.0)
3. LEGO Continuous Variable Transmission (CVT) V3 [Link YouTube](https://www.youtube.com/watch?v=sa60egMprYc)
4. LEGO Simple CVT (Continuously Variable Transmission) [Link YouTube](https://www.youtube.com/watch?v=1y5fQr0dDVg)

---
## 📄LICENÇA
* Ver o arquivo `LICENSE`.

---
## 📂 ESTRUTURA DO PROJETO
``` text
├── .vscode/                        → Listagens das config. e bibliotecas
├── docs/                           → Documentação do projeto
│   ├── images/                     → Imagens para relatórios e referências
│   ├── video/                      
│   │   └── Vídeo(s) original(is)   → Vídeo original
│   └── (...)                       → Proposta e relatório
├── libs/                           → Bibliotecas
│   └── (...)
├── src/                            → Código-fonte
│   └── (...)
├── .micropico                      → Arquivo necessário para a extensão Pi PICO no VSCODE
├── LICENSE                         → Licença de uso do código
└── README.md                       → Resumo e estrutura do projeto
```
