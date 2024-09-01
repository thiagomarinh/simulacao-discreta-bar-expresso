import simpy
import random
import numpy as np

# variaveis
RANDOM_SEED = 42
numero_cadeiras = 6
tempo_chegada_clientes = 4  # em minutos
tempo_consumo_clientes = 3  # em minutos
desvio_consumo = 1  # desvio padrão em minutos
probabilidade_copos = [0.3, 0.45, 0.2, 0.05]
tempo_atendimento = 0.7  # em minutos
desvio_atendimento = 0.3  # desvio padrão em minutos
tempo_lavagem_copos = 0.5  # em minutos
desvio_lavagem = 0.1  # desvio padrão em minutos
tempo_congelamento_copos = 4  # em minutos
numero_de_copos = 20
capacidade_pia = 6

# Estatísticas
clientes_atendidos = 0
copos_usados = 0

def cliente(env, nome, bar, cadeiras, freezer, pia, atendentes):
    global clientes_atendidos, copos_usados

    # Chegada do cliente
    print(f'{env.now:.2f} - {nome} chegou.')

    with cadeiras.request() as cadeira:
        yield cadeira
        print(f'{env.now:.2f} - {nome} sentou.')

        # Quantidade de copos que o cliente vai beber
        copos_para_beber = np.random.choice([1, 2, 3, 4], p=probabilidade_copos)

        for i in range(copos_para_beber):
            with atendentes.request() as atendente:
                yield atendente

                # Atendimento (pegar e servir copo)
                yield env.timeout(abs(random.gauss(tempo_atendimento, desvio_atendimento)))
                print(f'{env.now:.2f} - {nome} foi atendido e recebeu o copo {i + 1}.')

                # Consumir bebida
                yield env.timeout(abs(random.gauss(tempo_consumo_clientes, desvio_consumo)))
                print(f'{env.now:.2f} - {nome} terminou de beber o copo {i + 1}.')

                # Após o consumo, o copo vai para a pia
                with pia.request() as lugar_pia:
                    yield lugar_pia
                    print(f'{env.now:.2f} - {nome} teve seu copo {i+1} colocado na pia.')

                    # Lavagem do copo
                    yield env.timeout(abs(random.gauss(tempo_lavagem_copos, desvio_lavagem)))

                    # Mover copo lavado para o freezer
                    with freezer.request() as espaco_freezer:
                        yield espaco_freezer
                        print(f'{env.now:.2f} - Copo {i + 1} do {nome} foi lavado e colocado no freezer.')
                        yield env.timeout(tempo_congelamento_copos)
                        freezer.release(espaco_freezer)
                        print(f'{env.now:.2f} - Copo {i + 1} do {nome} está pronto para uso.')

            copos_usados += 1

        cadeiras.release(cadeira)
        print(f'{env.now:.2f} - {nome} deixou o bar.')

    clientes_atendidos += 1


def gerar_clientes(env, bar, cadeiras, freezer, pia, atendentes):
    nome_cliente = 0
    while True:
        yield env.timeout(random.expovariate(1 / tempo_chegada_clientes))
        nome_cliente += 1
        env.process(cliente(env, f'Cliente {nome_cliente}', bar, cadeiras, freezer, pia, atendentes))


# Configuração do ambiente de simulação
env = simpy.Environment()
bar = simpy.Resource(env, capacity=numero_cadeiras)
cadeiras = simpy.Resource(env, capacity=numero_cadeiras)
freezer = simpy.Resource(env, capacity=numero_de_copos)
pia = simpy.Resource(env, capacity=capacidade_pia)
atendentes = simpy.Resource(env, capacity=2)

# Iniciar a geração de clientes
env.process(gerar_clientes(env, bar, cadeiras, freezer, pia, atendentes))

# Rodar a simulação por um tempo determinado (em minutos)
env.run(until=120)

print(f'\nEstatísticas finais:')
print(f'Clientes atendidos: {clientes_atendidos}')
print(f'Copos usados: {copos_usados}')
