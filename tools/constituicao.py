import re
import roman
import sys
from collections import namedtuple
from operator import attrgetter
from yattag import Doc


class Constituicao:
    def __init__(self, xml):
        self.capitulos = []

        for capitulo in xml.findall('capitulo'):
            self.capitulos.append(Capitulo(capitulo))

    def gerar_html(self):
        titulo = 'Constituição da Igreja Presbiteriana do Brasil'

        doc, tag, text, line = Doc().ttl()

        doc.asis('<!doctype html>')

        with tag('html', lang='pt-BR'):
            with tag('head'):
                doc.stag('meta', charset='utf-8')
                line('title', titulo)
                doc.stag('meta', name='author',
                         content='Igreja Presbiteriana do Brasil')
                doc.stag('meta', name='viewport',
                         content='width=device-width, initial-scale=1')
                doc.stag('link', rel='stylesheet',
                         href='https://cdn.jsdelivr.net/npm/bulma@0.9.1/css/bulma.min.css')
                with tag('style'):
                    text('span.latim { font-style: italic; }')
                    text('del { text-decoration: line-through }')

            with tag('body'):
                with tag('section', klass='section'):
                    with tag('div', klass='container'):
                        line('h1', titulo, klass='title is-1 has-text-centered')

                        for capitulo in self.capitulos:
                            capitulo.gerar_html(doc, tag, line)

        return doc


class Capitulo:
    def __init__(self, xml):
        self.secoes = []
        self.id = xml.attrib['id']
        self.titulo = xml.attrib['titulo']

        for secao in xml.findall('secao'):
            self.secoes.append(Secao(self, secao))

    def gerar_html(self, doc, tag, line):
        with tag('section', id=self.gerar_id(), klass='capitulo block'):
            if self.id != 'dg' and self.id != 'dt':
                line('h2', f'Capítulo {roman.toRoman(int(self.id))}',
                     klass='title is-3 has-text-centered')

            line('h2', self.titulo, klass='title is-3 has-text-centered')

            for secao in self.secoes:
                secao.gerar_html(doc, tag, line)

    def gerar_id(self): return f'c{self.id}'


class Secao:
    def __init__(self, pai, xml):
        self.pai = pai
        self.artigos = []
        self.id = int(xml.attrib['id'])
        self.titulo = xml.attrib['titulo'] if 'titulo' in xml.attrib else None

        for artigo in xml.findall('artigo'):
            self.artigos.append(Artigo(artigo))

    def gerar_html(self, doc, tag, line):
        with tag('section', id=self.gerar_id(), klass='secao block'):
            if self.titulo is None:
                line('h2', 'Seção Única',
                     klass='title is-5 has-text-centered is-sr-only')
            else:
                line('h2', f'Seção {self.id}ª - {self.titulo}',
                     klass='title is-5 has-text-centered')

            for artigo in self.artigos:
                artigo.gerar_html(doc, tag, line)

    def gerar_id(self): return f'{self.pai.gerar_id()}_s{self.id}'


class Artigo:
    def __init__(self, xml):
        self.paragrafos = []
        self.id = int(xml.attrib['id'])

        self.paragrafos.append(Caput(self, xml.find('caput')))

        for paragrafo in xml.findall('paragrafo'):
            self.paragrafos.append(Paragrafo(self, paragrafo))

    def gerar_html(self, doc, tag, line):
        with tag('div', id=self.gerar_id(), klass='artigo block'):
            for paragrafo in self.paragrafos:
                paragrafo.gerar_html(doc, tag, line)

    def gerar_id(self): return f'a{self.id}'


class Paragrafo:
    def __init__(self, pai, xml, caput=False):
        self.pai = pai
        self.alineas = []
        self.versoes_texto = []

        self.vigente = True

        self.id = 0 if caput else int(xml.attrib['id'])

        for versao in xml.findall('texto'):
            texto = versao.text
            instrumento = versao.attrib['instrumento'] if 'instrumento' in versao.attrib else None
            ordem = int(versao.attrib['ordem']) if 'ordem' in versao.attrib else 1

            if any(v.ordem == ordem for v in self.versoes_texto):
                print(f'{Utilitario.ERRO}Erro{Utilitario.ENDC}')
                print(f'* Texto com ordem repetida: {texto}')
                sys.exit(1)

            Utilitario.verificar_pontuacao(texto)

            self.vigente = self.vigente and texto != 'Revogado.'
            self.versoes_texto.append(Utilitario.VersaoTexto(texto, instrumento, ordem))

        self.versoes_texto = sorted(self.versoes_texto, key=attrgetter('ordem'))

        alineas = xml.find('alineas')

        if alineas is not None:
            for alinea in alineas.findall('alinea'):
                self.alineas.append(Alinea(self, alinea))

    def gerar_html(self, doc, tag, line):
        if self.id == 0:
            tipo = 'caput'
            terminal = 'º' if self.pai.id < 10 else '.'
            rotulo = f'Art. {self.pai.id}{terminal}'
        else:
            tipo = 'paragrafo'
            if len(self.pai.paragrafos) > 2:
                rotulo = f'§ {self.id}º.'
            else:
                rotulo = 'Parágrafo único.'

        with tag('p', id=self.gerar_id(), klass=f'{tipo} content'):
            tamanho_historico = len(self.versoes_texto)

            for indice, versao in enumerate(self.versoes_texto, start=1):
                if indice != tamanho_historico:
                    with tag('del'):
                        self.__gerar_html(doc, tag, line, rotulo, versao)
                    doc.stag('br')
                else:
                    self.__gerar_html(doc, tag, line, rotulo, versao)

            for alinea in self.alineas:
                alinea.gerar_html(doc, tag)

    def gerar_id(self): return f'{self.pai.gerar_id()}_p{self.id}'

    def __gerar_html(self, doc, tag, line, rotulo, versao):
        line('strong', rotulo)
        doc.asis(f' {Utilitario.processar_texto(versao.texto)}')

        if versao.instrumento is not None:
            line('span', versao.instrumento, klass='tag is-info ml-2')


class Caput(Paragrafo):
    def __init__(self, pai, xml):
        super().__init__(pai, xml, caput=True)

    def gerar_html(self, doc, tag, line):
        super().gerar_html(doc, tag, line)


class Alinea:
    def __init__(self, pai, xml):
        self.pai = pai
        self.id = xml.attrib['id']
        self.texto = xml.text

        Utilitario.verificar_pontuacao(self.texto)

    def gerar_html(self, doc, tag):
        doc.stag('br')
        with tag('span', id=self.gerar_id()):
            doc.asis(f'{self.id}) {Utilitario.processar_texto(self.texto)}')

    def gerar_id(self): return f'{self.pai.gerar_id()}_{self.id}'


class Utilitario:
    VersaoTexto = namedtuple('VersaoTexto', 'texto instrumento ordem')

    ALERTA = '\033[33m'
    ERRO = '\033[31m'
    ENDC = '\033[0m'

    @staticmethod
    def verificar_pontuacao(texto):
        if texto.endswith(tuple([';', '.', ':'])):
            return

        print(f'{Utilitario.ALERTA}Alerta{Utilitario.ENDC}')
        print(f'* Texto sem terminal: {texto}')

    @staticmethod
    def processar_texto(texto):
        return Utilitario.marcar_referencias(Utilitario.marcar_termos_latinos(texto))

    @staticmethod
    def marcar_referencias(texto):
        return re.sub(r'art\. (\d{1,3})(º)?', r'<a href="#a\1">art. \1\2</a>', texto)

    @staticmethod
    def marcar_termos_latinos(texto):
        termos = ['ex officio', 'in fine', 'ad referendum', 'quorum']
        return re.sub(f"({'|'.join(termos)})", r'<span class="latim">\1</span>', texto)
