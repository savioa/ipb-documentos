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
        preambulo = ('Em nome do Pai, do Filho e do Espírito Santo, nós, legítimos representantes '
                     'da Igreja Cristã Presbiteriana do Brasil, reunidos em Supremo Concílio, '
                     'no ano de 1950, com poderes para reforma da Constituição, investidos de toda '
                     'autoridade para cumprir as resoluções da legislatura de 1946, depositando '
                     'toda nossa confiança na bênção do Deus Altíssimo e tendo em vista a promoção '
                     'da paz, disciplina, unidade e edificação do povo de Cristo, elaboramos, '
                     'decretamos e promulgamos, para glória de Deus, a seguinte Constituição da '
                     'Igreja Presbiteriana do Brasil.')
        capitulos = {'preambulo': 'Preâmbulo',
                     'c1': 'I - Natureza, Governo e Fins da Igreja',
                     'c2': 'II - Organização das Comunidades Locais',
                     'c3': 'III - Membros da Igreja',
                     'c4': 'IV - Oficiais',
                     'c5': 'V - Concílios',
                     'c6': 'VI - Comissões e Outras Organizações',
                     'c7': 'VII - Ordens da Igreja',
                     'cdg': 'Disposições Gerais',
                     'cdt': 'Disposições Transitórias'}

        doc, tag, text, line = Doc().ttl()

        doc.asis('<!doctype html>')

        with tag('html', lang='pt-BR', klass='has-navbar-fixed-bottom'):
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
                    text('span[data-lang] { font-style: italic; }')
                    text('del { text-decoration: line-through }')
                line('script', '', src='base.js')

            with tag('body'):
                with tag('nav', ('aria-label', 'main navigation'),
                         klass='navbar is-fixed-bottom is-light is-hidden-mobile'
                         ):
                    with tag('div', klass='navbar-menu'):
                        with tag('div', klass='navbar-start'):
                            with tag('div', klass='navbar-item has-dropdown has-dropdown-up is-hoverable'):
                                line('a', 'Índice', klass='navbar-link')

                                with tag('div', klass='navbar-dropdown'):
                                    for chave, texto in capitulos.items():
                                        line('a', texto, klass='navbar-item', href=f'#{chave}')
                                        if chave == 'preambulo' or chave == 'c7':
                                            doc.stag('hr', klass='navbar-divider')

                        with tag('div', klass='navbar-end'):
                            with tag('div', klass='navbar-item'):
                                with tag('label', klass='checkbox'):
                                    doc.stag('input', type='checkbox', id='mostrar_versoes')
                                    text(' Apresentar versões obsoletas')

                with tag('section', klass='section'):
                    with tag('div', klass='container'):
                        line('h1', titulo, klass='title is-1 has-text-centered')

                        line('h2', 'Índice', klass='title is-3 has-text-centered is-hidden-tablet')
                        with tag('ul', klass='content is-hidden-tablet'):
                            for chave, texto in capitulos.items():
                                with tag('li'):
                                    line('a', texto, klass='', href=f'#{chave}')

                        with tag('section', id='preambulo', klass='capitulo block'):
                            line('h2', 'Preâmbulo',
                                 klass='title is-3 has-text-centered')
                            line('p', preambulo)

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
                titulo = 'Única'
                visibilidade = ' is-sr-only'
            else:
                titulo = f'{self.id}ª - {self.titulo}'
                visibilidade = ''

            line('h2', f'Seção {titulo}',
                 klass=f'title is-5 has-text-centered{visibilidade}')

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
            ordem = int(versao.attrib['ordem']
                        ) if 'ordem' in versao.attrib else 1

            if any(v.ordem == ordem for v in self.versoes_texto):
                print(f'{Utilitario.ERRO}Erro{Utilitario.ENDC}')
                print(f'* Texto com ordem repetida: {texto}')
                sys.exit(1)

            Utilitario.verificar_pontuacao(texto)

            self.vigente = self.vigente and texto != 'Revogado.'
            self.versoes_texto.append(
                Utilitario.VersaoTexto(texto, instrumento, ordem))

        self.versoes_texto = sorted(
            self.versoes_texto, key=attrgetter('ordem'))

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

        numero_versoes = len(self.versoes_texto)

        with tag('p', id=self.gerar_id(), klass=f'{tipo} content'):
            for indice, versao in enumerate(self.versoes_texto, start=1):
                visivel = indice == numero_versoes

                Paragrafo.__gerar_versao(
                    doc, tag, line, rotulo, versao, visivel)

            for alinea in self.alineas:
                alinea.gerar_html(doc, tag)

    def gerar_id(self): return f'{self.pai.gerar_id()}_p{self.id}'

    @staticmethod
    def __gerar_versao(doc, tag, line, rotulo, versao, visivel):
        classes = f'versao{"" if visivel else " obsoleta is-hidden"}'

        if versao.instrumento is not None:
            with tag('span', ('data-instrumento', versao.instrumento), klass=classes):
                Paragrafo.__tratar_visibilidade(
                    doc, tag, line, visivel, rotulo, versao.texto)
        else:
            with tag('span', klass=classes):
                Paragrafo.__tratar_visibilidade(
                    doc, tag, line, visivel, rotulo, versao.texto)

    @staticmethod
    def __tratar_visibilidade(doc, tag, line, visivel, rotulo, texto):
        if not visivel:
            with tag('del'):
                Paragrafo.__gerar_texto_versao(doc, line, rotulo, texto)

            doc.stag('br')
        else:
            Paragrafo.__gerar_texto_versao(doc, line, rotulo, texto)

    @staticmethod
    def __gerar_texto_versao(doc, line, rotulo, texto):
        line('strong', rotulo)
        doc.asis(f' {Utilitario.processar_texto(texto)}')


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
        return re.sub(f"({'|'.join(termos)})", r'<span data-lang="latim">\1</span>', texto)
