from constituicao import Constituicao

import os
from time import perf_counter
from xml.etree.ElementTree import parse

inicio_tempo = perf_counter()

if 'tools' in os.getcwd():
    os.chdir('../')

caminho_xml = os.path.join(os.getcwd(), 'constituicao.xml')

constituicao = Constituicao(parse(caminho_xml).getroot())

constituicao.imprimir()
pass

print('Tempo de execução: ', perf_counter() - inicio_tempo)
