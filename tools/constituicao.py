from cores_terminal import CoresTerminal

import roman
import re
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
                line('style', 'span.latim { font-style: italic; }')

            with tag('body'):
                with tag('section', klass='section'):
                    with tag('div', klass='container'):
                        line('h1', titulo, klass='title is-1 has-text-centered')

                        for capitulo in self.capitulos:
                            capitulo.gerar_html(doc, tag, text, line)

        return doc


class Capitulo:
    def __init__(self, xml):
        self.secoes = []
        self.id = int(xml.attrib['id'])
        self.titulo = xml.attrib['titulo']

        for secao in xml.findall('secao'):
            self.secoes.append(Secao(self, secao))

    def gerar_html(self, doc, tag, text, line):
        with tag('section', id=self.gerar_id(), klass='capitulo block'):
            line('h2', f'Capítulo {roman.toRoman(self.id)}',
                 klass='title is-3 has-text-centered')
            line('h2', self.titulo, klass='title is-3 has-text-centered')

            for secao in self.secoes:
                secao.gerar_html(doc, tag, text, line)

    def gerar_id(self): return f'c{self.id}'


class Secao:
    def __init__(self, pai, xml):
        self.pai = pai
        self.artigos = []
        self.id = int(xml.attrib['id'])
        self.titulo = xml.attrib['titulo'] if 'titulo' in xml.attrib else None

        for artigo in xml.findall('artigo'):
            self.artigos.append(Artigo(artigo))

    def gerar_html(self, doc, tag, text, line):
        with tag('section', id=self.gerar_id(), klass='secao block'):
            if self.titulo is None:
                line('h2', 'Seção Única',
                     klass='title is-5 has-text-centered is-sr-only')
            else:
                line('h2', f'Seção {self.id}ª - {self.titulo}',
                     klass='title is-5 has-text-centered')

            for artigo in self.artigos:
                artigo.gerar_html(doc, tag, text, line)

    def gerar_id(self): return f'{self.pai.gerar_id()}_s{self.id}'


class Artigo:
    def __init__(self, xml):
        self.paragrafos = []
        self.id = int(xml.attrib['id'])

        self.paragrafos.append(Caput(self, xml.find('caput')))

        for paragrafo in xml.findall('paragrafo'):
            self.paragrafos.append(Paragrafo(self, paragrafo))

    def gerar_html(self, doc, tag, text, line):
        with tag('div', id=self.gerar_id(), klass='artigo block'):
            for paragrafo in self.paragrafos:
                paragrafo.gerar_html(doc, tag, text, line)

    def gerar_id(self): return f'a{self.id}'


class Paragrafo:
    def __init__(self, pai, xml):
        self.pai = pai
        self.alineas = []

        if not hasattr(self, 'id'):
            self.id = int(xml.attrib['id'])

        self.texto = xml.find('texto').text

        Utilitario.verificar_pontuacao(self.texto)

        alineas = xml.find('alineas')

        if alineas is not None:
            for alinea in alineas.findall('alinea'):
                self.alineas.append(Alinea(self, alinea))

    def gerar_html(self, doc, tag, text, line):
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
            line('strong', rotulo)
            doc.asis(f' {Utilitario.processar_texto(self.texto)}')

            for alinea in self.alineas:
                alinea.gerar_html(doc, tag)

    def gerar_id(self): return f'{self.pai.gerar_id()}_p{self.id}'


class Caput(Paragrafo):
    def __init__(self, pai, xml):
        self.id = 0

        super().__init__(pai, xml)

    def gerar_html(self, doc, tag, text, line):
        super().gerar_html(doc, tag, text, line)


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
    @staticmethod
    def verificar_pontuacao(texto):
        if texto.endswith(tuple([';', '.', ':'])):
            return

        print(f'{CoresTerminal.ALERTA}Alerta{CoresTerminal.ENDC}')
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
