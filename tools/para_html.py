"""Geração de documentos da IPB em HTML"""

import os
from time import perf_counter
from xml.etree.ElementTree import parse

from yattag.indentation import indent
from documento import Documento


inicio_tempo = perf_counter()

if 'tools' in os.getcwd():
    os.chdir('../')

caminho_constituicao = os.path.join(os.getcwd(), 'constituicao.xml')

constituicao = Documento(parse(caminho_constituicao).getroot())

with open('index.html', mode='w', encoding='utf-8') as f:
    f.write(indent(constituicao.gerar_html().getvalue(), indentation='    '))

print('Tempo de execução: ', perf_counter() - inicio_tempo)
