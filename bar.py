import simpy
import random


def cliente(env, nome, bar, caixa_de_pia, freezer):
    chegada = env.now
    print(f'{nome} chegou ao bar no tempo {chegada:.2f}')

    with bar.request() as pedido:
        yield pedido
        print(f'{nome} começou a consumir no tempo {env.now:.2f}')

        # Tempo de consumo normalmente distribuído com média de 3 minutos e desvio padrão de 1 minuto
        tempo_consumo = max(0, random.normalvariate(3, 1))
        yield env.timeout(tempo_consumo)

        copos_para_consumir = random.choices(
            population=[1, 2, 3, 4],
            weights=[0.3, 0.45, 0.2, 0.05],
            k=1
        )[0]

        print(f'{nome} terminou de consumir {copos_para_consumir} copos no tempo {env.now:.2f}')

        for _ in range(copos_para_consumir):
            with caixa_de_pia.request() as pia_requisicao:
                yield pia_requisicao
                print(f'{nome} colocou um copo sujo na pia no tempo {env.now:.2f}')
                yield env.timeout(0.5)  # Tempo para colocar o copo sujo na pia

            with freezer.request() as freezer_requisicao:
                yield freezer_requisicao
                print(f'{nome} deixou um copo para lavar e congelar no tempo {env.now:.2f}')

                # Tempo para lavar e congelar o copo
                tempo_lavar_congelar = max(0, random.normalvariate(0.5, 0.1))
                yield env.timeout(tempo_lavar_congelar)
                print(f'{nome} terminou o processo de lavagem e congelamento no tempo {env.now:.2f}')

                # Copo ficará no freezer por 4 minutos
                yield env.timeout(4)


def gerar_clientes(env, bar, caixa_de_pia, freezer):
    cliente_id = 1
    while True:
        yield env.timeout(random.expovariate(1 / 4.0))  # Tempo médio entre chegadas de 4 minutos
        env.process(cliente(env, f'Cliente {cliente_id}', bar, caixa_de_pia, freezer))
        cliente_id += 1


def main():
    random.seed(42)
    env = simpy.Environment()

    # Recursos
    bar = simpy.Resource(env, capacity=6)  # 6 cadeiras no balcão
    caixa_de_pia = simpy.Resource(env, capacity=6)  # Capacidade máxima da pia é 6 copos sujos
    freezer = simpy.Resource(env, capacity=20)  # 20 copos disponíveis

    env.process(gerar_clientes(env, bar, caixa_de_pia, freezer))

    env.run(until=120)  # Simulação de 120 minutos


if __name__ == '__main__':
    main()
