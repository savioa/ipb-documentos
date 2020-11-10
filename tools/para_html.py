"""Geração da constituição representada em HTML"""

import os
from time import perf_counter
from xml.etree.ElementTree import parse

from yattag.indentation import indent
from constituicao import Constituicao


inicio_tempo = perf_counter()

if 'tools' in os.getcwd():
    os.chdir('../')

caminho_xml = os.path.join(os.getcwd(), 'constituicao.xml')

constituicao = Constituicao(parse(caminho_xml).getroot())

# constituicao.imprimir()
html = constituicao.gerar_html()

with open('index.html', mode='w', encoding='utf-8') as f:
    f.write(indent(html.getvalue(), indentation='    '))

print('Tempo de execução: ', perf_counter() - inicio_tempo)
