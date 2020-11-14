"""Geração de documentos da IPB em HTML"""

import os
from time import perf_counter
from xml.etree.ElementTree import parse

from yattag.indentation import indent
from documento import Documento


inicio_tempo = perf_counter()

if 'tools' in os.getcwd():
    os.chdir('../')

# Constituição
caminho_documento = os.path.join(os.getcwd(), 'constituicao.xml')

constituicao = Documento(parse(caminho_documento).getroot())

with open('docs/constituicao.html', mode='w', encoding='utf-8') as f:
    f.write(indent(constituicao.gerar_html().getvalue(), indentation='    '))

# Código de Disciplina
caminho_documento = os.path.join(os.getcwd(), 'codigo_de_disciplina.xml')

codigo_de_disciplina = Documento(parse(caminho_documento).getroot())

with open('docs/codigo_de_disciplina.html', mode='w', encoding='utf-8') as f:
    f.write(indent(codigo_de_disciplina.gerar_html().getvalue(), indentation='    '))


print('Tempo de execução: ', perf_counter() - inicio_tempo)
